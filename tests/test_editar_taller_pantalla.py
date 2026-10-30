# Pantalla de editar taller: el coordinador cambia su taller y vuelve a quedar pendiente.
from datetime import timedelta
import pytest
from django.utils import timezone
from inscripciones.models import MotivoEdicion, Taller, Usuario

pytestmark = pytest.mark.django_db


def test_coordinador_edita_su_taller_desde_la_pantalla(client):
    coordinador = Usuario.objects.create(username="CO01", rol=Usuario.Rol.COORDINADOR)
    inicio = timezone.now() + timedelta(days=3)
    taller = Taller.objects.create(codigo="TAL-EDI-01", nombre="Taller a editar", cupo_maximo=10,
                                   fecha_inicio=inicio, fecha_fin=inicio + timedelta(hours=2),
                                   coordinador=coordinador)
    motivo = MotivoEdicion.objects.create(descripcion="Cambio de aula")
    client.force_login(coordinador)

    assert client.get(f"/talleres/{taller.pk}/editar/").status_code == 200   # el HTML existe
    client.post(f"/talleres/{taller.pk}/editar/", {
        "cupo_maximo": 20,
        "fecha_inicio": inicio.strftime("%Y-%m-%dT%H:%M"),
        "fecha_fin": (inicio + timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M"),
        "motivo": motivo.pk,
    })
    taller.refresh_from_db()
    assert taller.cupo_maximo == 20
    assert taller.estado == Taller.Estado.PENDIENTE   # vuelve a aprobación