from datetime import timedelta
import pytest
from django.utils import timezone
from inscripciones.models import Categoria, Inscripcion, Taller, Usuario
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

# buscar talleres por categoría
def test_buscar_por_categoria_trae_solo_los_de_esa_categoria():
    baile = Categoria.objects.get_or_create(nombre="Baile")[0]
    canto = Categoria.objects.get_or_create(nombre="Canto")[0]
    salsa = crear_taller_que_empieza_en_dias("TAL-SAL-01", 2)
    tango = crear_taller_que_empieza_en_dias("TAL-TAN-01", 1)
    coro = crear_taller_que_empieza_en_dias("TAL-COR-01", 1)
    Taller.objects.filter(pk__in=[salsa.pk, tango.pk]).update(categoria=baile)
    Taller.objects.filter(pk=coro.pk).update(categoria=canto)

    encontrados = Participante.buscar_talleres_por_categoria(baile)
    assert list(encontrados) == [tango, salsa]      # solo Baile, el más próximo primero

def test_buscar_no_muestra_pendientes_cancelados_ni_empezados():
    baile = Categoria.objects.get_or_create(nombre="Baile")[0]
    abierto = crear_taller_que_empieza_en_dias("TAL-ABI-01", 1)
    pendiente = crear_taller_que_empieza_en_dias("TAL-PEN-01", 1)
    cancelado = crear_taller_que_empieza_en_dias("TAL-CAN-01", 1)
    empezado = crear_taller_que_empieza_en_dias("TAL-EMP-01", -1)
    Taller.objects.update(categoria=baile)
    Taller.objects.filter(pk=pendiente.pk).update(estado=Taller.Estado.PENDIENTE)
    Taller.objects.filter(pk=cancelado.pk).update(cancelado=True)

    assert list(Participante.buscar_talleres_por_categoria(baile)) == [abierto]

def test_sin_elegir_categoria_ve_todos_los_talleres_disponibles():
    baile = Categoria.objects.get_or_create(nombre="Baile")[0]
    canto = Categoria.objects.get_or_create(nombre="Canto")[0]
    salsa = crear_taller_que_empieza_en_dias("TAL-SAL-01", 2)
    coro = crear_taller_que_empieza_en_dias("TAL-COR-01", 1)
    Taller.objects.filter(pk=salsa.pk).update(categoria=baile)
    Taller.objects.filter(pk=coro.pk).update(categoria=canto)

    assert list(Participante.buscar_talleres_por_categoria()) == [coro, salsa]