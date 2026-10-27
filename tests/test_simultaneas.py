import threading
import time
from datetime import timedelta

import pytest
from django.db import close_old_connections, connections
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
        for numero in (1, 2, 3):
            c.execute("INSERT INTO estudiantes (ci, nombre, apellido) VALUES (%s, 'N', 'A')", [str(1000000 + numero)])


@pytest.fixture
def conteo_lento(monkeypatch):
    # Hace que contar inscripciones tarde un poco, para que los dos pedidos
    # lleguen a contar las plazas antes de que cualquiera guarde la suya.
    contar = QuerySet.count

    def contar_despacio(consulta):
        resultado = contar(consulta)
        if consulta.model is Inscripcion:
            time.sleep(0.3)
        return resultado

    monkeypatch.setattr(QuerySet, "count", contar_despacio)


def estudiante(numero):
    return Usuario.objects.create(username=f"estudiante{numero}", codigo=str(1000000 + numero))


def pedir_al_mismo_tiempo(personas, taller):
    # Cada persona pide desde su propio hilo; la barrera hace que salgan juntas.
    salida = threading.Barrier(len(personas))

    def pedir(persona):
        salida.wait()
        Operador.registrar_inscripcion(persona, taller)
        close_old_connections()

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