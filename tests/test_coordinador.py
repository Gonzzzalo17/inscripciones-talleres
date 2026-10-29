from datetime import timedelta
import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone
from inscripciones.models import Inscripcion, Taller, Usuario
from inscripciones.servicios.coordinador import Coordinador
from inscripciones.servicios.operador import Operador

pytestmark = pytest.mark.django_db

def fecha_dentro_de_horas(horas):
    # Fecha y hora futura: ahora + las horas indicadas.
    return timezone.now() + timedelta(hours=horas)

def fecha_hace_horas(horas):
    # Fecha y hora pasada: ahora - las horas indicadas.
    return timezone.now() - timedelta(hours=horas)

def crear_taller_que_empieza_manana(nombre="Danza", cupo=10):
    # Crea un taller válido con la lógica real del coordinador:
    # empieza en 24 horas y dura 2 horas.
    return Coordinador.crear_taller(nombre, cupo,
                                    fecha_dentro_de_horas(24), fecha_dentro_de_horas(26))

def editar_taller_para_pasado_manana(taller, nombre, cupo):
    # Edita el taller con la lógica real del coordinador,
    # moviéndolo a pasado mañana (en 48 horas, dura 2 horas).
    return Coordinador.editar_taller(taller.pk, nombre, cupo,
                                     fecha_dentro_de_horas(48), fecha_dentro_de_horas(50),
                                     motivo="Cambio pedido por el coordinador")

def inscribir_participante(taller, estado, posicion_espera=None):
    # Crea un participante nuevo y lo inscribe directo en la base de datos,
    # sin pasar por las reglas. Solo sirve para preparar la situación de la prueba.
    participante = Usuario.objects.create(username=f"participante{Usuario.objects.count()}")
    return Inscripcion.objects.create(participante=participante, taller=taller,
                                      estado=estado, posicion_espera=posicion_espera)

def test_primer_taller_recibe_codigo_01():
    assert crear_taller_que_empieza_manana("Danza").codigo == "TAL-DAN-01"

def test_segundo_taller_de_la_misma_actividad_recibe_codigo_02():
    crear_taller_que_empieza_manana("Danza")
    assert crear_taller_que_empieza_manana("Danza moderna").codigo == "TAL-DAN-02"

def test_rechaza_cupo_cero():
    with pytest.raises(ValidationError):
        crear_taller_que_empieza_manana(cupo=0)

def test_rechaza_fin_antes_del_inicio():
    inicio = fecha_dentro_de_horas(24)
    fin_una_hora_antes = fecha_dentro_de_horas(23)
    with pytest.raises(ValidationError):
        Coordinador.crear_taller("Danza", 10, inicio, fin_una_hora_antes)

def test_editar_cambia_nombre_y_cupo():
    taller = editar_taller_para_pasado_manana(crear_taller_que_empieza_manana(), "Ballet", 20)
    assert (taller.nombre, taller.cupo_maximo) == ("Ballet", 20)

def test_bajar_el_cupo_solo_hasta_los_confirmados_sin_mover_a_nadie():
    taller = crear_taller_que_empieza_manana(cupo=10)
    for _ in range(3):
        inscribir_participante(taller, "CONFIRMADO")
    inscribir_participante(taller, "EN_ESPERA", posicion_espera=1)

    with pytest.raises(ValidationError):
        editar_taller_para_pasado_manana(taller, "Danza", 2)    # menos que los 3 confirmados
    editar_taller_para_pasado_manana(taller, "Danza", 3)        # igual a los confirmados: se permite

    taller.refresh_from_db()
    assert taller.cupo_maximo == 3
    assert taller.inscripciones.filter(estado="CONFIRMADO").count() == 3
    assert taller.inscripciones.filter(estado="EN_ESPERA").count() == 1

def test_editar_subiendo_el_cupo_confirma_a_la_espera_en_orden():
    taller = crear_taller_que_empieza_manana(cupo=1)
    inscribir_participante(taller, "CONFIRMADO")
    primero_en_espera = inscribir_participante(taller, "EN_ESPERA", posicion_espera=1)
    segundo_en_espera = inscribir_participante(taller, "EN_ESPERA", posicion_espera=2)

    editar_taller_para_pasado_manana(taller, "Danza", 2)

    primero_en_espera.refresh_from_db()
    segundo_en_espera.refresh_from_db()
    assert primero_en_espera.estado == "CONFIRMADO"
    assert (segundo_en_espera.estado, segundo_en_espera.posicion_espera) == ("EN_ESPERA", 1)

def test_rechaza_editar_un_taller_que_ya_empezo():
    taller_empezado = Taller.objects.create(codigo="TAL-DAN-01", nombre="Danza", cupo_maximo=10,
                                            fecha_inicio=fecha_hace_horas(1),
                                            fecha_fin=fecha_dentro_de_horas(1))
    with pytest.raises(ValidationError):
        editar_taller_para_pasado_manana(taller_empezado, "Ballet", 10)

def test_subir_el_cupo_confirma_al_primero_en_espera_y_el_segundo_pasa_a_ser_primero():
    taller = crear_taller_que_empieza_manana(cupo=1)
    inscribir_participante(taller, "CONFIRMADO")
    primero_en_espera = inscribir_participante(taller, "EN_ESPERA", posicion_espera=1)
    segundo_en_espera = inscribir_participante(taller, "EN_ESPERA", posicion_espera=2)
    taller.cupo_maximo = 2
    taller.save()

    assert Operador.promover_hasta_llenar(taller) == [primero_en_espera]
    segundo_en_espera.refresh_from_db()
    assert segundo_en_espera.posicion_espera == 1

def test_subir_el_cupo_nunca_confirma_mas_que_el_nuevo_cupo():
    taller = crear_taller_que_empieza_manana(cupo=1)
    inscribir_participante(taller, "CONFIRMADO")
    for posicion in (1, 2, 3):
        inscribir_participante(taller, "EN_ESPERA", posicion_espera=posicion)
    taller.cupo_maximo = 3
    taller.save()

    Operador.promover_hasta_llenar(taller)
    assert taller.inscripciones.filter(estado="CONFIRMADO").count() == 3
    assert taller.inscripciones.filter(estado="EN_ESPERA").count() == 1