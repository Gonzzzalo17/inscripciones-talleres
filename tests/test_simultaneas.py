import concurrent.futures
import threading
import time
from django.core.exceptions import ValidationError
from datetime import timedelta

import pytest
from django.db import  connections
from django.db.models.query import QuerySet
from django.utils import timezone

from inscripciones.models import Inscripcion, Taller, Usuario
from inscripciones.servicios.operador import Operador

# Simula dos personas pidiendo la última plaza al mismo tiempo (cada una en su hilo).
pytestmark = pytest.mark.django_db(transaction=True, databases=["default", "estudiantes_db"])


@pytest.fixture(autouse=True)
def padron():
    with connections["estudiantes_db"].cursor() as c:
        c.execute("CREATE TABLE IF NOT EXISTS estudiantes "
                  "(ci VARCHAR(20) PRIMARY KEY, nombre VARCHAR(100), apellido VARCHAR(100), carrera VARCHAR(100))")
        c.execute("DELETE FROM estudiantes")
        for numero in range(1, 31):
            c.execute("INSERT OR IGNORE INTO estudiantes (ci, nombre, apellido) VALUES (%s, 'N', 'A')",
                      [str(1000000 + numero)])


@pytest.fixture
def conteo_lento(monkeypatch):
    # Hace que contar inscripciones tarde un poco, para que los dos pedidos
    # lleguen a contar las plazas antes de que cualquiera guarde la suya.
    contar = QuerySet.count

    def contar_despacio(consulta):
        resultado = contar(consulta)
        if consulta.model is Inscripcion:
            time.sleep(0.1)
        return resultado

    monkeypatch.setattr(QuerySet, "count", contar_despacio)


def estudiante(numero):
    return Usuario.objects.create(username=f"estudiante{numero}", codigo=str(1000000 + numero))


def pedir_al_mismo_tiempo(personas, taller):
    # Cada persona pide desde su propio hilo; la barrera hace que salgan juntas.
    salida = threading.Barrier(len(personas))

    def pedir(persona):
        try:
            salida.wait()
            Operador.registrar_inscripcion(persona, taller)
        finally:
            connections.close_all()

    hilos = [threading.Thread(target=pedir, args=(persona,)) for persona in personas]
    for hilo in hilos:
        hilo.start()
    for hilo in hilos:
        hilo.join()


def test_dos_pedidos_a_la_vez_por_la_ultima_plaza_solo_uno_queda_confirmado(conteo_lento):
    inicio = timezone.now() + timedelta(hours=24)
    taller = Taller.objects.create(codigo="TAL-DAN-01", nombre="Danza", cupo_maximo=2,
                                   fecha_inicio=inicio, fecha_fin=inicio + timedelta(hours=2))
    Operador.registrar_inscripcion(estudiante(1), taller)        # queda 1 plaza libre

    pedir_al_mismo_tiempo([estudiante(2), estudiante(3)], taller)

    assert Inscripcion.objects.filter(taller=taller, estado="CONFIRMADO").count() == 2
    assert Inscripcion.objects.filter(taller=taller, estado="EN_ESPERA").count() == 1

def test_carga_solicitudes_simultaneas_respeta_limite_cupo_y_espera():
    # 1. Crear taller con cupo = 10
    taller = Taller.objects.create(
        codigo="CARGA-01",
        nombre="Taller de Prueba de Carga",
        cupo_maximo=10,
        fecha_inicio=timezone.now() + timedelta(days=2),
        fecha_fin=timezone.now() + timedelta(days=2, hours=2)
    )

    max_espera = Operador.capacidad_lista_de_espera(taller.cupo_maximo) # 2
    total_admitidos_posibles = taller.cupo_maximo + max_espera # 12

    # 2. Crear 20 participantes con CIs VÁLIDAS del padrón (1000001 a 1000020)
    participantes = []
    for i in range(1, 21):
        ci = str(1000000 + i)
        u, _ = Usuario.objects.get_or_create(
            username=f"p_carga_{i}",
            defaults={"codigo": ci, "rol": Usuario.Rol.PARTICIPANTE}
        )
        participantes.append(u)

    # 3. Intentar registrar inscripción
    def intentar_inscripcion(participante):
        try:
            return Operador.registrar_inscripcion(participante, taller)
        except ValidationError:
            return None
        finally:
            connections.close_all()

    # 4. Peticiones concurrentes
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        list(executor.map(intentar_inscripcion, participantes))

    # 5. Assertions
    confirmados = Inscripcion.objects.filter(taller=taller, estado="CONFIRMADO").count()
    en_espera = Inscripcion.objects.filter(taller=taller, estado="EN_ESPERA").count()

    assert confirmados <= taller.cupo_maximo, f"Se superó el cupo: {confirmados} > {taller.cupo_maximo}"
    assert en_espera <= max_espera, f"Se superó la lista de espera: {en_espera} > {max_espera}"
    assert confirmados + en_espera == total_admitidos_posibles