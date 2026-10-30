# Regla del equipo: el coordinador solo ve sus propios talleres (lista y ocupación).
from datetime import timedelta
import pytest
from django.utils import timezone
from inscripciones.models import Taller, Usuario

pytestmark = pytest.mark.django_db


def test_coordinador_no_ve_talleres_de_otro_coordinador(client):
    yo = Usuario.objects.create(username="CO01", codigo="CO01", rol=Usuario.Rol.COORDINADOR)
    otro = Usuario.objects.create(username="CO02", codigo="CO02", rol=Usuario.Rol.COORDINADOR)
    inicio = timezone.now() + timedelta(days=3)
    Taller.objects.create(codigo="TAL-MIO-01", nombre="Taller mio", cupo_maximo=5, coordinador=yo,
                          fecha_inicio=inicio, fecha_fin=inicio + timedelta(hours=2))
    ajeno = Taller.objects.create(codigo="TAL-AJE-01", nombre="Taller ajeno", cupo_maximo=5, coordinador=otro,
                                  fecha_inicio=inicio, fecha_fin=inicio + timedelta(hours=2))
    client.force_login(yo)

    lista = client.get("/").content.decode()
    assert "Taller mio" in lista and "Taller ajeno" not in lista
    assert client.get(f"/talleres/{ajeno.pk}/ocupacion/").status_code == 403