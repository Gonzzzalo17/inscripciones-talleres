# Gantt 66-67: el estudiante crea su cuenta desde la pantalla de registro.
import pytest
from django.db import connections
from inscripciones.models import Usuario

pytestmark = pytest.mark.django_db(databases=["default", "estudiantes_db"])


@pytest.fixture(autouse=True)
def padron():
    # Padrón falso: solo el código 95445 es estudiante de la universidad
    with connections["estudiantes_db"].cursor() as c:
        c.execute("DROP TABLE IF EXISTS estudiantes")
        c.execute("CREATE TABLE estudiantes (ci TEXT PRIMARY KEY, nombre TEXT, apellido TEXT)")
        c.execute("INSERT INTO estudiantes VALUES ('95445', 'Ana', 'Rojas')")


def registrarse(client, codigo, contrasena):
    return client.post("/registrarse/", {"codigo": codigo, "contrasena": contrasena,
                                         "repetir_contrasena": contrasena})


def test_estudiante_del_padron_crea_su_cuenta_y_entra(client):
    respuesta = registrarse(client, "95445", "Talleres-2026")
    ana = Usuario.objects.get(username="95445")
    assert ana.rol == Usuario.Rol.PARTICIPANTE
    assert ana.get_full_name() == "Ana Rojas"          # el nombre sale del padrón
    assert ana.check_password("Talleres-2026")          # guardada cifrada
    assert respuesta.url == "/mis-inscripciones/"       # entra directo


def test_codigo_fuera_del_padron_no_crea_cuenta(client):
    respuesta = registrarse(client, "00000", "Talleres-2026")
    assert "no figura en la lista de estudiantes" in respuesta.content.decode()
    assert not Usuario.objects.filter(username="00000").exists()


def test_codigo_que_ya_tiene_cuenta_no_se_registra_dos_veces(client):
    registrarse(client, "95445", "Talleres-2026")
    client.post("/salir/")
    respuesta = registrarse(client, "95445", "Otra-Clave-99")
    assert "ya tiene una cuenta" in respuesta.content.decode()
    assert Usuario.objects.filter(username="95445").count() == 1