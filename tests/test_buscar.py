# Gantt 72-73: pantalla del operador para buscar inscripciones.
from datetime import timedelta
import pytest
from django.utils import timezone
from inscripciones.models import Inscripcion, Taller, Usuario

pytestmark = pytest.mark.django_db


def test_operador_busca_por_nombre_y_ve_la_inscripcion(client):
    ana = Usuario.objects.create(username="95445", codigo="95445", first_name="Ana", last_name="Rojas")
    inicio = timezone.now() + timedelta(days=3)
    taller = Taller.objects.create(codigo="TAL-SAL-01", nombre="Salsa", cupo_maximo=5,
                                   fecha_inicio=inicio, fecha_fin=inicio + timedelta(hours=2))
    Inscripcion.objects.create(participante=ana, taller=taller, estado="CONFIRMADO")
    client.force_login(Usuario.objects.create(username="OP01", rol=Usuario.Rol.OPERADOR))

    pagina = client.get("/buscar-inscripciones/", {"q": "rojas"}).content.decode()
    assert "Ana Rojas" in pagina and "Salsa" in pagina