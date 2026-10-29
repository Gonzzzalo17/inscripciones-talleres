import os
from datetime import timedelta

import pytest
from django.db import connections
from django.utils import timezone

from inscripciones.models import Inscripcion, Taller, Usuario

# Pruebas de punta a punta, se abre un navegador de verdad (Chromium, sin ventana),
# se hace clic en las pantallas como lo haría una persona y se revisa lo que se ve y lo que quedó guardado.
# Necesitan (una sola vez):  pip install pytest-playwright   y   playwright install chromium
pytest.importorskip("pytest_playwright")                       # si no está instalado, se saltan
os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")    # el navegador y Django corren en el mismo proceso
pytestmark = pytest.mark.django_db(transaction=True, databases=["default", "estudiantes_db"])

CONTRASENA = "Talleres-2026"

@pytest.fixture(autouse=True)
def padron():
    # Padrón de prueba: solo el código 95445 (Ana Rojas) es estudiante de la universidad.
    with connections["estudiantes_db"].cursor() as c:
        c.execute("CREATE TABLE IF NOT EXISTS estudiantes (ci TEXT PRIMARY KEY, nombre TEXT, apellido TEXT, carrera TEXT)")
        c.execute("DELETE FROM estudiantes")
        c.execute("INSERT INTO estudiantes (ci, nombre, apellido) VALUES ('95445', 'Ana', 'Rojas')")

def cuenta(codigo, rol=Usuario.Rol.PARTICIPANTE):
    usuario = Usuario(username=codigo, codigo=codigo, rol=rol)
    usuario.set_password(CONTRASENA)
    usuario.save()
    return usuario

def taller_de_danza(cupo=10):
    inicio = timezone.now() + timedelta(days=2)
    return Taller.objects.create(codigo="TAL-DAN-01", nombre="Danza", cupo_maximo=cupo,
                                 fecha_inicio=inicio, fecha_fin=inicio + timedelta(hours=2))

def entrar(page, live_server, codigo):
    page.goto(f"{live_server.url}/entrar/")
    page.fill("#codigo", codigo)
    page.fill("#contrasena", CONTRASENA)
    page.click("button[type=submit]")

def pedir_plaza_en_danza(page, live_server):
    page.goto(f"{live_server.url}/")
    page.click("text=Solicitar inscripción")
    page.click("button:has-text('Solicitar inscripción')")

# el estudiante crea su cuenta y entra directo
def test_estudiante_se_registra_y_entra_a_mis_inscripciones(page, live_server):
    page.goto(f"{live_server.url}/registrarse/")
    page.fill("#codigo", "95445")
    page.fill("#contrasena", CONTRASENA)
    page.fill("#repetir_contrasena", CONTRASENA)
    page.click("button:has-text('Crear cuenta')")

    assert page.url.endswith("/mis-inscripciones/")
    assert Usuario.objects.get(username="95445").get_full_name() == "Ana Rojas"

# con plaza libre queda confirmada
def test_participante_entra_y_se_inscribe_en_un_taller(page, live_server):
    ana = cuenta("95445")
    taller_de_danza()

    entrar(page, live_server, "95445")
    pedir_plaza_en_danza(page, live_server)

    assert page.locator(".aviso.confirmado").is_visible()
    assert Inscripcion.objects.get(participante=ana).estado == "CONFIRMADO"

# con el taller lleno queda en la lista de espera
def test_con_el_taller_lleno_el_participante_queda_en_espera(page, live_server):
    ana = cuenta("95445")
    danza = taller_de_danza(cupo=4)
    for numero in range(4):                       # 4 confirmados: el taller queda lleno
        Inscripcion.objects.create(participante=cuenta(f"otro{numero}"), taller=danza, estado="CONFIRMADO")

    entrar(page, live_server, "95445")
    pedir_plaza_en_danza(page, live_server)

    assert page.locator(".aviso.espera").is_visible()
    assert Inscripcion.objects.get(participante=ana).posicion_espera == 1

# el participante cancela desde "Mis inscripciones"
def test_participante_cancela_su_inscripcion(page, live_server):
    ana = cuenta("95445")
    Inscripcion.objects.create(participante=ana, taller=taller_de_danza(), estado="CONFIRMADO")

    entrar(page, live_server, "95445")
    page.goto(f"{live_server.url}/mis-inscripciones/")
    page.on("dialog", lambda ventana: ventana.accept())          # acepta el "¿Seguro que quieres cancelar?"
    page.click("button:has-text('Cancelar')")

    page.wait_for_load_state()
    assert Inscripcion.objects.get(participante=ana).estado == "CANCELADO"

# un participante no puede abrir una pantalla que no le toca
def test_participante_no_puede_abrir_la_pantalla_de_crear_taller(page, live_server):
    cuenta("95445")

    entrar(page, live_server, "95445")
    respuesta = page.goto(f"{live_server.url}/talleres/nuevo/")

    assert respuesta.status == 403
    assert Taller.objects.count() == 0