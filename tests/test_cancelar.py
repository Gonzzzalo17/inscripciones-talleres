# Gantt 34-35 / 40-41: botón "Cancelar" en Mis inscripciones.
from datetime import timedelta
import pytest
from django.db import connections
from django.utils import timezone
from inscripciones.models import Taller, Usuario
from inscripciones.servicios.operador import Operador

pytestmark = pytest.mark.django_db(databases=["default", "estudiantes_db"])


@pytest.fixture(autouse=True)
def padron():
    # Padrón falso con 2 estudiantes, para poder inscribirlos
    with connections["estudiantes_db"].cursor() as c:
        c.execute("DROP TABLE IF EXISTS estudiantes")
        c.execute("CREATE TABLE estudiantes (ci TEXT PRIMARY KEY, nombre TEXT, apellido TEXT)")
        for ci in ("95445", "95446"):
            c.execute("INSERT INTO estudiantes VALUES (%s, 'N', 'A')", [ci])


def inscrito(codigo):
    # Crea un participante inscrito en un taller que empieza en 3 días
    usuario = Usuario.objects.create(username=codigo, codigo=codigo)
    inicio = timezone.now() + timedelta(days=3)
    taller = Taller.objects.create(codigo=f"T-{codigo}", nombre="Taller de prueba", cupo_maximo=5,
                                   fecha_inicio=inicio, fecha_fin=inicio + timedelta(hours=2))
    return usuario, Operador.registrar_inscripcion(usuario, taller)


def test_participante_cancela_su_inscripcion(client):
    ana, inscripcion = inscrito("95445")
    client.force_login(ana)
    respuesta = client.post(f"/inscripciones/{inscripcion.pk}/cancelar/", follow=True)
    inscripcion.refresh_from_db()
    assert inscripcion.estado == "CANCELADO"
    assert "Se canceló la inscripción" in respuesta.content.decode()


def test_participante_no_puede_cancelar_la_de_otro(client):
    _, inscripcion_de_beto = inscrito("95446")
    ana = Usuario.objects.create(username="95445", codigo="95445")
    client.force_login(ana)
    assert client.post(f"/inscripciones/{inscripcion_de_beto.pk}/cancelar/").status_code == 403
    inscripcion_de_beto.refresh_from_db()
    assert inscripcion_de_beto.estado == "CONFIRMADO"