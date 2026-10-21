from datetime import timedelta
import pytest
from django.utils import timezone
from inscripciones.models import Inscripcion, Taller, Usuario
from inscripciones.servicios.participante import Participante

pytestmark = pytest.mark.django_db


# Preparar los datos para que cada prueba sea corta.
def crear_taller_que_empieza_en_dias(codigo, dias):
    # Crea un taller que empieza dentro de 'dias' días y dura 2 horas.
    inicio = timezone.now() + timedelta(days=dias)
    return Taller.objects.create(codigo=codigo, nombre=f"Taller {codigo}", cupo_maximo=10,
                                 fecha_inicio=inicio, fecha_fin=inicio + timedelta(hours=2))


def inscribir(participante, taller, estado, posicion_espera=None):
    # Inscribe directo en la base de datos, sin pasar por las reglas.
    return Inscripcion.objects.create(participante=participante, taller=taller,
                                      estado=estado, posicion_espera=posicion_espera)
@pytest.fixture
def ana():
    return Usuario.objects.create(username="ana")


def test_sin_inscripciones_devuelve_lista_vacia(ana):
    assert list(Participante.consultar_mis_inscripciones(ana)) == []

def test_muestra_la_posicion_cuando_esta_en_espera(ana):
    inscribir(ana, crear_taller_que_empieza_en_dias("TAL-DAN-01", 1), "EN_ESPERA", posicion_espera=2)
    [inscripcion] = Participante.consultar_mis_inscripciones(ana)
    assert (inscripcion.estado, inscripcion.posicion_espera) == ("EN_ESPERA", 2)

def test_tambien_muestra_las_canceladas(ana):
    inscribir(ana, crear_taller_que_empieza_en_dias("TAL-DAN-01", 1), "CANCELADO")
    [inscripcion] = Participante.consultar_mis_inscripciones(ana)
    assert inscripcion.estado == "CANCELADO"

def test_no_muestra_inscripciones_de_otra_persona(ana):
    otra_persona = Usuario.objects.create(username="beto")
    inscribir(otra_persona, crear_taller_que_empieza_en_dias("TAL-DAN-01", 1), "CONFIRMADO")
    assert list(Participante.consultar_mis_inscripciones(ana)) == []

def test_ordena_del_taller_mas_proximo_al_mas_lejano(ana):
    taller_lejano = crear_taller_que_empieza_en_dias("TAL-AJE-01", 5)
    taller_proximo = crear_taller_que_empieza_en_dias("TAL-DAN-01", 1)
    inscribir(ana, taller_lejano, "CONFIRMADO")
    inscribir(ana, taller_proximo, "CONFIRMADO")
    talleres = [inscripcion.taller for inscripcion in Participante.consultar_mis_inscripciones(ana)]
    assert talleres == [taller_proximo, taller_lejano]