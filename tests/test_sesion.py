# HU-12 · Gantt 109: inicio de sesión según el rol y acceso a las pantallas.
import pytest
from django.core.exceptions import ValidationError
from inscripciones.models import Usuario
from inscripciones.servicios.sesion import Sesion, MENSAJE_DATOS_INCORRECTOS

pytestmark = pytest.mark.django_db

CONTRASENA = "Talleres-2026"


def crear_cuenta(codigo, rol):
    # Crea una cuenta con la contraseña cifrada, igual que el registro.
    usuario = Usuario(username=codigo, codigo=codigo, rol=rol)
    usuario.set_password(CONTRASENA)
    usuario.save()
    return usuario


# --- Lógica: Sesion.iniciar_sesion ---

def test_codigo_sin_cuenta_da_el_mismo_motivo():
    with pytest.raises(ValidationError) as error:
        Sesion.iniciar_sesion("00000", CONTRASENA)
    assert MENSAJE_DATOS_INCORRECTOS in error.value.messages




@pytest.mark.parametrize("rol, pantalla", [
    (Usuario.Rol.PARTICIPANTE, "mis_inscripciones"),
    (Usuario.Rol.COORDINADOR, "crear_taller"),
    (Usuario.Rol.OPERADOR, "lista_talleres"),
])
def test_cada_rol_va_a_su_pantalla(rol, pantalla):
    crear_cuenta("12345", rol)
    _, destino = Sesion.iniciar_sesion("12345", CONTRASENA)
    assert destino == pantalla


# --- Pantallas: entrar, salir y permisos ---

def test_al_entrar_el_participante_va_a_mis_inscripciones(client):
    crear_cuenta("95445", Usuario.Rol.PARTICIPANTE)
    respuesta = client.post("/entrar/", {"codigo": "95445", "contrasena": CONTRASENA})
    assert respuesta.status_code == 302
    assert respuesta.url == "/mis-inscripciones/"


def test_con_la_contrasena_mal_muestra_el_motivo(client):
    crear_cuenta("95445", Usuario.Rol.PARTICIPANTE)
    respuesta = client.post("/entrar/", {"codigo": "95445", "contrasena": "mal"})
    assert respuesta.status_code == 200
    assert MENSAJE_DATOS_INCORRECTOS in respuesta.content.decode()


def test_sin_sesion_lo_manda_a_entrar(client):
    respuesta = client.get("/talleres/nuevo/")
    assert respuesta.status_code == 302
    assert respuesta.url.startswith("/entrar/")


def test_participante_no_puede_abrir_pantallas_del_operador(client):
    client.force_login(crear_cuenta("95445", Usuario.Rol.PARTICIPANTE))
    assert client.get("/talleres/nuevo/").status_code == 403
    assert client.get("/historial-cancelaciones/").status_code == 403


def test_operador_puede_abrir_sus_pantallas(client):
    client.force_login(crear_cuenta("OP01", Usuario.Rol.OPERADOR))
    assert client.get("/talleres/nuevo/").status_code == 200
    assert client.get("/historial-cancelaciones/").status_code == 200


def test_cada_rol_ve_solo_su_menu(client):
    client.force_login(crear_cuenta("95445", Usuario.Rol.PARTICIPANTE))
    menu = client.get("/").content.decode()
    assert "Mis inscripciones" in menu
    assert "Crear taller" not in menu
    assert "Historial de cancelaciones" not in menu


def test_salir_cierra_la_sesion(client):
    client.force_login(crear_cuenta("95445", Usuario.Rol.PARTICIPANTE))
    client.post("/salir/")
    assert client.get("/").status_code == 302



# --- Error encontrado al probar: un participante podía inscribir a otro ---

@pytest.fixture
def padron():
    # Para inscribir, el sistema revisa el padrón de estudiantes: creamos uno falso con 2 códigos
    from django.db import connections
    with connections["estudiantes_db"].cursor() as c:
        c.execute("DROP TABLE IF EXISTS estudiantes")
        c.execute("CREATE TABLE estudiantes (ci TEXT PRIMARY KEY, nombre TEXT, apellido TEXT)")
        for ci in ("95445", "95446"):
            c.execute("INSERT INTO estudiantes VALUES (%s, 'N', 'A')", [ci])


@pytest.mark.django_db(databases=["default", "estudiantes_db"])
def test_participante_solo_puede_inscribirse_a_si_mismo(client, padron):
    from datetime import timedelta
    from django.utils import timezone
    from inscripciones.models import Taller
    yo = crear_cuenta("95445", Usuario.Rol.PARTICIPANTE)
    otro = crear_cuenta("95446", Usuario.Rol.PARTICIPANTE)
    inicio = timezone.now() + timedelta(days=3)
    taller = Taller.objects.create(codigo="T-01", nombre="Taller de prueba", cupo_maximo=5,
                                   fecha_inicio=inicio, fecha_fin=inicio + timedelta(hours=2))
    client.force_login(yo)
    # Aunque mande a mano el id de otro participante, queda inscrito él
    client.post(f"/talleres/{taller.pk}/inscribirse/", {"participante": otro.pk})
    assert taller.inscripciones.filter(participante=yo).exists()
    assert not taller.inscripciones.filter(participante=otro).exists()