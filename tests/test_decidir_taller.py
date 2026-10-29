# El operador aprueba o rechaza los talleres que pide un coordinador.
from datetime import timedelta
import pytest
from django.utils import timezone
from inscripciones.models import Taller, Usuario

pytestmark = pytest.mark.django_db


def taller_pendiente():
    inicio = timezone.now() + timedelta(days=3)
    return Taller.objects.create(codigo="TAL-PEN-01", nombre="Taller pendiente", cupo_maximo=5,
                                 fecha_inicio=inicio, fecha_fin=inicio + timedelta(hours=2),
                                 estado=Taller.Estado.PENDIENTE)


def test_operador_aprueba_un_taller_pendiente(client):
    taller = taller_pendiente()
    client.force_login(Usuario.objects.create(username="OP01", rol=Usuario.Rol.OPERADOR))
    respuesta = client.post(f"/talleres/{taller.pk}/decidir/", {"decision": "aprobar"}, follow=True)
    taller.refresh_from_db()
    assert taller.estado == Taller.Estado.APROBADO
    assert "Se aprobó el taller" in respuesta.content.decode()


def test_participante_no_ve_talleres_pendientes(client):
    taller_pendiente()
    client.force_login(Usuario.objects.create(username="95445", rol=Usuario.Rol.PARTICIPANTE))
    assert "Taller pendiente" not in client.get("/").content.decode()