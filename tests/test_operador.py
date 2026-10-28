from datetime import timedelta

import pytest
from django.core.exceptions import ValidationError
from django.db import connections
from django.utils import timezone

from inscripciones.models import HistorialCancelacion, Inscripcion, Taller, Usuario, Notificacion
from inscripciones.servicios.operador import Operador

pytestmark = pytest.mark.django_db(databases=["default", "estudiantes_db"])


@pytest.fixture(autouse=True)
def padron(db):
    with connections["estudiantes_db"].cursor() as c:
        c.execute("DROP TABLE IF EXISTS estudiantes")
        c.execute("CREATE TABLE estudiantes "
                  "(ci TEXT PRIMARY KEY, nombre TEXT, apellido TEXT)")
        for i in range(1, 31):
            c.execute("INSERT OR IGNORE INTO estudiantes VALUES (%s, 'N', 'A')",
                      [str(1000000 + i)])


def usuario(i):
    ci = str(1000000 + i)
    u, _ = Usuario.objects.get_or_create(username=f"u{i}", defaults={"codigo": ci})
    return u

def taller(codigo="DAN-PAR-01", cupo=2, empieza_en_horas=5, duracion=2, inicio=None):
    inicio = inicio or timezone.now() + timedelta(hours=empieza_en_horas)
    return Taller.objects.create(
        codigo=codigo, nombre=f"Taller {codigo}", cupo_maximo=cupo,
        fecha_inicio=inicio, fecha_fin=inicio + timedelta(hours=duracion))

def solicitar(i, t):
    return Operador.registrar_inscripcion(usuario(i), t)

def estado(i, t):
    return Inscripcion.objects.get(participante=usuario(i), taller=t).estado

def confirmados(t):
    return Inscripcion.objects.filter(taller=t, estado="CONFIRMADO").count()

def en_espera(t):
    return Inscripcion.objects.filter(taller=t, estado="EN_ESPERA").count()

@pytest.mark.parametrize("cupo,esperado", [
    (1, 1), (2, 1), (5, 1), (10, 2), (12, 3), (15, 3), (20, 4), (35, 7), (55, 11)])
def test_capacidad_lista_espera_redondea_hacia_arriba(cupo, esperado):
    assert Operador.capacidad_lista_de_espera(cupo) == esperado

# ---- TAL-RF-01 ----
def test_confirmado_con_plaza_libre():
    t = taller(cupo=10)
    solicitar(1, t)
    assert estado(1, t) == "CONFIRMADO"
    assert confirmados(t) == 1

def test_e1_taller_ya_iniciado_no_escribe_nada():
    t = taller(empieza_en_horas=-1)
    with pytest.raises(ValidationError):
        solicitar(1, t)
    assert Inscripcion.objects.count() == 0

def test_e3_choque_de_horario_conserva_la_inscripcion_previa():
    a = taller("DAN-PAR-01")
    b = taller("FUT-PAR-01", inicio=a.fecha_inicio)
    solicitar(1, a)
    with pytest.raises(ValidationError):
        solicitar(1, b)
    assert estado(1, a) == "CONFIRMADO"
    assert not Inscripcion.objects.filter(taller=b).exists()

def test_e4_espera_en_ultima_posicion():
    t = taller(cupo=10)
    for i in range(1, 11):
        solicitar(i, t)
    solicitar(11, t)
    solicitar(12, t)
    assert estado(11, t) == "EN_ESPERA"
    assert Inscripcion.objects.get(participante=usuario(11), taller=t).posicion_espera == 1
    assert Inscripcion.objects.get(participante=usuario(12), taller=t).posicion_espera == 2
    assert confirmados(t) == 10

def test_e5_taller_y_espera_llenos_rechaza_sin_cambios():
    t = taller("FUT-PAR-01", cupo=10)
    for i in range(1, 13):               # 10 confirmados + 2 en espera
        solicitar(i, t)
    with pytest.raises(ValidationError):
        solicitar(13, t)
    assert confirmados(t) == 10
    assert en_espera(t) == 2
    assert not Inscripcion.objects.filter(participante=usuario(13)).exists()

def test_cupo_12_admite_3_en_espera_y_rechaza_el_cuarto():
    t = taller(cupo=12)
    for i in range(1, 16):               # 12 + 3
        solicitar(i, t)
    assert en_espera(t) == 3
    with pytest.raises(ValidationError):
        solicitar(16, t)

def test_duplicado_rechazado_sin_cambios():
    t = taller(cupo=2)
    solicitar(1, t)
    with pytest.raises(ValidationError):
        solicitar(1, t)
    assert confirmados(t) == 1

def test_ci_fuera_del_padron():
    t = taller()
    intruso = Usuario.objects.create(username="intruso", codigo="9999999")
    with pytest.raises(ValidationError):
        Operador.registrar_inscripcion(intruso, t)
    assert Inscripcion.objects.count() == 0

def test_usuario_sin_codigo_rechazado():
    t = taller()
    sin_codigo = Usuario.objects.create(username="sin_codigo")
    with pytest.raises(ValidationError):
        Operador.registrar_inscripcion(sin_codigo, t)

def test_caso_critico_cupo_2():
    t = taller(cupo=2)
    solicitar(1, t)
    solicitar(2, t)
    with pytest.raises(ValidationError):
        solicitar(2, t)                  # repetición de P-02
    solicitar(3, t)                      # ceil(0.4) = 1 -> P-03 queda EN ESPERA
    assert estado(3, t) == "EN_ESPERA"
    with pytest.raises(ValidationError):
        solicitar(4, t)                  # la espera (1) ya está llena
    assert confirmados(t) == 2

def test_cancelar_promueve_al_primero_en_espera():
    t = taller(cupo=10)
    for i in range(1, 13):               # 10 confirmados, 11 y 12 en espera
        solicitar(i, t)
    Operador.cancelar_inscripcion(usuario(1), t)
    assert estado(1, t) == "CANCELADO"
    assert estado(11, t) == "CONFIRMADO"
    assert Inscripcion.objects.get(participante=usuario(12), taller=t).posicion_espera == 1
    assert confirmados(t) == 10
    assert HistorialCancelacion.objects.filter(participante=usuario(1), taller=t).count() == 1

def test_cancelar_fuera_de_plazo_conserva_la_inscripcion():
    t = taller(empieza_en_horas=2)       # quedan menos de 3 h
    solicitar(1, t)
    with pytest.raises(ValidationError):
        Operador.cancelar_inscripcion(usuario(1), t)
    assert estado(1, t) == "CONFIRMADO"
    assert HistorialCancelacion.objects.count() == 0

def test_cancela_alguien_en_espera_y_las_posiciones_se_reordenan():
    t = taller(cupo=10, empieza_en_horas=24)
    for i in range(1, 13):               # 10 confirmados, 11 y 12 en espera
        solicitar(i, t)
    Operador.cancelar_inscripcion(usuario(11), t)
    restante = Inscripcion.objects.get(participante=usuario(12), taller=t)
    assert restante.posicion_espera == 1

def test_cancelar_avisa_felicidades_solo_al_promovido():
    t = taller(cupo=10)
    for i in range(1, 13):
        solicitar(i, t)
    Operador.cancelar_inscripcion(usuario(1), t)
    aviso = Notificacion.objects.get()
    assert aviso.participante == usuario(11)
    assert aviso.taller == t

def test_calcular_ocupacion_con_2_confirmados_1_en_espera_y_1_cancelado():
    t = taller(cupo=2, empieza_en_horas=24)
    for i in range(1, 4):                # 1 y 2 confirmados, 3 en espera
        solicitar(i, t)
    Operador.cancelar_inscripcion(usuario(1), t)   # 1 cancela y 3 pasa a confirmado
    solicitar(4, t)                      # 4 queda en espera

    ocupacion = Operador.calcular_ocupacion(t)

    assert ocupacion['ocupadas'] == 2
    assert ocupacion['libres'] == 0
    assert ocupacion['en_espera'] == 1
    assert ocupacion['maximo_espera'] == 1   # 20 % de 2, redondeado hacia arriba

def test_buscar_por_codigo_de_taller_trae_solo_las_de_ese_taller():
    danza = taller(codigo="DAN-BUS-01", cupo=5, empieza_en_horas=5)
    pintura = taller(codigo="PIN-BUS-01", cupo=5, empieza_en_horas=10)
    solicitar(1, danza)
    solicitar(2, danza)
    solicitar(3, pintura)

    encontradas = Operador.buscar_inscripciones("DAN-BUS")

    assert {inscripcion.taller for inscripcion in encontradas} == {danza}
    assert encontradas.count() == 2

def test_buscar_por_codigo_de_participante_trae_todas_sus_inscripciones():
    danza = taller(codigo="DAN-BUS-01", cupo=5, empieza_en_horas=5)
    pintura = taller(codigo="PIN-BUS-01", cupo=5, empieza_en_horas=10)
    solicitar(1, danza)
    solicitar(1, pintura)
    solicitar(2, danza)

    encontradas = Operador.buscar_inscripciones(usuario(1).codigo)

    assert {inscripcion.participante for inscripcion in encontradas} == {usuario(1)}
    assert {inscripcion.taller for inscripcion in encontradas} == {danza, pintura}

def test_buscar_sin_texto_no_trae_nada_y_no_cambia_datos():
    danza = taller(codigo="DAN-BUS-01", cupo=5)
    solicitar(1, danza)

    assert Operador.buscar_inscripciones("").count() == 0
    assert Operador.buscar_inscripciones("   ").count() == 0
    assert estado(1, danza) == "CONFIRMADO"