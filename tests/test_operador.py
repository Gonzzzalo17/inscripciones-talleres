from datetime import timedelta

import pytest
from django.core.exceptions import ValidationError
from django.db import connections
from django.utils import timezone
from inscripciones.servicios.coordinador import Coordinador
from inscripciones.models import HistorialCancelacion, Inscripcion, Taller, Usuario, Notificacion, Categoria
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
       (4, 1), (5, 1), (6, 2), (12, 3), (40, 8)])
def test_capacidad_lista_espera_redondea_hacia_arriba(cupo, esperado):
    assert Operador.capacidad_lista_de_espera(cupo) == esperado

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

# el operador acepta o rechaza los talleres que piden los coordinadores

def operador_del_sistema():
    return Usuario.objects.create(username="operador", rol=Usuario.Rol.OPERADOR)

def test_operador_aprueba_un_taller_pendiente_y_recien_ahi_acepta_inscripciones():
    pintura = taller(codigo="PIN-APR-01", cupo=5)
    pintura.estado = Taller.Estado.PENDIENTE
    pintura.save()
    with pytest.raises(ValidationError):
        solicitar(1, pintura)                      # pendiente: no se puede inscribir

    Operador.aprobar_taller(operador_del_sistema(), pintura)
    solicitar(1, pintura)

    assert estado(1, pintura) == "CONFIRMADO"

def test_taller_rechazado_no_acepta_inscripciones():
    pintura = taller(codigo="PIN-REC-01", cupo=5)
    pintura.estado = Taller.Estado.PENDIENTE
    pintura.save()

    Operador.rechazar_taller(operador_del_sistema(), pintura)

    pintura.refresh_from_db()
    assert pintura.estado == Taller.Estado.RECHAZADO
    with pytest.raises(ValidationError):
        solicitar(1, pintura)

def test_solo_el_operador_decide_y_solo_sobre_talleres_pendientes():
    coordinadora = Usuario.objects.create(username="coordinadora", rol=Usuario.Rol.COORDINADOR)
    pintura = taller(codigo="PIN-DEC-01", cupo=5)
    pintura.estado = Taller.Estado.PENDIENTE
    pintura.save()

    with pytest.raises(ValidationError):
        Operador.aprobar_taller(coordinadora, pintura)       # no es operadora
    Operador.aprobar_taller(operador_del_sistema(), pintura)
    with pytest.raises(ValidationError):
        Operador.rechazar_taller(Usuario.objects.get(username="operador"), pintura)  # ya no está pendiente

# cancelar un taller completo
def test_cancelar_taller_anula_a_todos_les_avisa_y_no_cuenta_para_el_bloqueo():
    t = taller(codigo="DAN-CAN-01", cupo=2, empieza_en_horas=24)
    for i in (1, 2, 3):                  # 1 y 2 confirmados, 3 en espera
        solicitar(i, t)
    avisos_antes = Notificacion.objects.count()

    Operador.cancelar_taller(operador_del_sistema(), t)

    t.refresh_from_db()
    assert t.cancelado
    assert Inscripcion.objects.filter(taller=t).exclude(estado="CANCELADO").count() == 0
    assert Notificacion.objects.count() == avisos_antes + 3     # un aviso para cada uno
    assert HistorialCancelacion.objects.count() == 0            # no suma para el bloqueo
    with pytest.raises(ValidationError):
        solicitar(4, t)                                         # ya no recibe inscripciones

def test_el_coordinador_solo_cancela_sus_talleres():
    ana = Usuario.objects.create(username="ana", rol=Usuario.Rol.COORDINADOR)
    luis = Usuario.objects.create(username="luis", rol=Usuario.Rol.COORDINADOR)
    taller_de_ana = taller(codigo="DAN-ANA-01", cupo=5)
    Taller.objects.filter(pk=taller_de_ana.pk).update(coordinador=ana)
    taller_de_ana.refresh_from_db()

    with pytest.raises(ValidationError):
        Operador.cancelar_taller(luis, taller_de_ana)           # no es suyo
    Operador.cancelar_taller(ana, taller_de_ana)                # el suyo: sí

    taller_de_ana.refresh_from_db()
    assert taller_de_ana.cancelado

@pytest.mark.django_db(databases=["default", "estudiantes_db"])
def test_operador_puede_levantar_bloqueo_y_conservar_historial_antiguo():
        participante = Usuario.objects.create(
            username="estudiante_bloqueado",
            codigo="1000001",
            rol=Usuario.Rol.PARTICIPANTE,
        )
        operador = Usuario.objects.create(
            username="operador_historial_test",
            codigo="OP-002",
            rol=Usuario.Rol.OPERADOR,
        )

        taller = Taller.objects.create(
            codigo="BAN-TEST-01",
            nombre="Taller de prueba",
            cupo_maximo=5,
            fecha_inicio=timezone.now() + timedelta(days=2),
            fecha_fin=timezone.now() + timedelta(days=2, hours=2),
            estado=Taller.Estado.APROBADO,
        )

        ahora = timezone.now()

        # Una cancelación antigua que debe conservarse.
        antigua = HistorialCancelacion.objects.create(
            participante=participante,
            taller=taller,
        )
        HistorialCancelacion.objects.filter(pk=antigua.pk).update(
            fecha_cancelacion=ahora - timedelta(days=5)
        )

        # Cuatro cancelaciones recientes que provocan el bloqueo.
        for _ in range(4):
            HistorialCancelacion.objects.create(
                participante=participante,
                taller=taller,
            )

        with pytest.raises(ValidationError):
            Operador.verificar_que_no_este_bloqueado(participante)

        Operador.levantar_bloqueo(operador, participante)

        # Ya no debe estar bloqueado.
        Operador.verificar_que_no_este_bloqueado(participante)

        # El historial antiguo debe seguir existiendo.
        assert HistorialCancelacion.objects.filter(
            pk=antigua.pk
        ).exists()

        # Las cancelaciones recientes deben haberse eliminado.
        assert not HistorialCancelacion.objects.filter(
            participante=participante,
            fecha_cancelacion__gte=ahora - timedelta(hours=72),
        ).exists()

        # La inscripción debe funcionar si el participante
        # también figura en el padrón estático.
        inscripcion = Operador.registrar_inscripcion(participante, taller)
        assert inscripcion.estado == "CONFIRMADO"
def test_operador_crea_taller_aprobado_sin_coordinador():
    operador = Usuario.objects.create(
        username="operador_creador_test",
        codigo="OP-003",
        rol=Usuario.Rol.OPERADOR,
    )
    categoria, _ = Categoria.objects.get_or_create(nombre="Deporte")

    taller_creado = Coordinador.crear_taller(
        nombre="Taller de prueba",
        cupo_maximo=10,
        fecha_inicio=timezone.now() + timedelta(days=2),
        fecha_fin=timezone.now() + timedelta(days=2, hours=2),
        categoria=categoria,
        usuario_creador=operador,
    )

    assert taller_creado.estado == Taller.Estado.APROBADO
    assert taller_creado.coordinador is None
    assert taller_creado.categoria == categoria