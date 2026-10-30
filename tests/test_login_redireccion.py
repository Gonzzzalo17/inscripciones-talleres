# Seguridad del login: después de entrar solo se vuelve a páginas de este mismo sitio.
import pytest
from inscripciones.models import Usuario

pytestmark = pytest.mark.django_db


def test_login_no_manda_a_otro_sitio(client):
    ana = Usuario.objects.create(username="95445", codigo="95445", rol=Usuario.Rol.PARTICIPANTE)
    ana.set_password("Talleres-2026")
    ana.save()
    respuesta = client.post("/entrar/?next=https://sitio-falso.com/",
                            {"codigo": "95445", "contrasena": "Talleres-2026"})
    assert respuesta.url == "/mis-inscripciones/"