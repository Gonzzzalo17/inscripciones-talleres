# HU-09 · Gantt 57: pruebas del baneo por cancelaciones.
# Regla: más de 3 cancelaciones dentro de 72 horas bloquean 24 horas.
from datetime import timedelta

import pytest
from django.core.exceptions import ValidationError
from django.db import connections
from django.utils import timezone

from inscripciones.models import HistorialCancelacion, Inscripcion, Taller, Usuario
from inscripciones.servicios.operador import Operador

pytestmark = pytest.mark.django_db(databases=["default", "estudiantes_db"])


@pytest.fixture(autouse=True)
def padron(db):
    # Padrón de prueba: los CI 1000001 a 1000010 son estudiantes autorizados.
    with connections["estudiantes_db"].cursor() as c:
        c.execute("DROP TABLE IF EXISTS estudiantes")
        c.execute("CREATE TABLE estudiantes (ci TEXT PRIMARY KEY, nombre TEXT, apellido TEXT)")
        for i in range(1, 11):
            c.execute("INSERT OR IGNORE INTO estudiantes VALUES (%s, 'N', 'A')", [str(1000000 + i)])


def usuario(i):
    u, _ = Usuario.objects.get_or_create(username=f"u{i}", defaults={"codigo": str(1000000 + i)})
    return u


def taller(codigo, cupo=1, empieza_en_dias=3):
    # Cada taller empieza en un día distinto para que no haya cruce de horario.
    inicio = timezone.now() + timedelta(days=empieza_en_dias)
    return Taller.objects.create(codigo=codigo, nombre=f"Taller {codigo}", cupo_maximo=cupo,
                                 fecha_inicio=inicio, fecha_fin=inicio + timedelta(hours=2))


def registrar_cancelaciones(participante, cantidad, hace_horas=1):
    # Crea 'cantidad' cancelaciones en el historial, hechas hace 'hace_horas' horas.
    t = taller(f"TAL-HIS-{cantidad}{hace_horas}", empieza_en_dias=20)
    fecha = timezone.now() - timedelta(hours=hace_horas)
    for _ in range(cantidad):
        cancelacion = HistorialCancelacion.objects.create(participante=participante, taller=t)
        # auto_now_add pone la fecha de ahora; la cambiamos para simular el pasado
        HistorialCancelacion.objects.filter(pk=cancelacion.pk).update(fecha_cancelacion=fecha)


def estado(i, t):
    return Inscripcion.objects.get(participante=usuario(i), taller=t).estado


def test_tres_cancelaciones_en_72_horas_no_bloquean():
    registrar_cancelaciones(usuario(1), 3)
    inscripcion = Operador.registrar_inscripcion(usuario(1), taller("TAL-DAN-01"))
    assert inscripcion.estado == "CONFIRMADO"


def test_cuatro_cancelaciones_en_72_horas_bloquean_24_horas():
    registrar_cancelaciones(usuario(1), 4)
    t = taller("TAL-DAN-01")
    with pytest.raises(ValidationError):
        Operador.registrar_inscripcion(usuario(1), t)
    assert not Inscripcion.objects.filter(participante=usuario(1), taller=t).exists()

    fin = Operador.calcular_fin_del_bloqueo(usuario(1))
    ultima = HistorialCancelacion.objects.filter(participante=usuario(1)).latest("fecha_cancelacion")
    assert fin == ultima.fecha_cancelacion + timedelta(hours=24)


def test_cuatro_cancelaciones_separadas_por_mas_de_72_horas_no_bloquean():
    registrar_cancelaciones(usuario(1), 2, hace_horas=100)
    registrar_cancelaciones(usuario(1), 2, hace_horas=1)
    inscripcion = Operador.registrar_inscripcion(usuario(1), taller("TAL-DAN-01"))
    assert inscripcion.estado == "CONFIRMADO"


def test_al_bloquearlo_pierde_sus_inscripciones_y_sale_de_las_esperas():
    confirmado = taller("TAL-ROB-01", cupo=1, empieza_en_dias=3)
    lleno = taller("TAL-MUS-01", cupo=1, empieza_en_dias=4)
    a_cancelar = taller("TAL-ART-01", cupo=5, empieza_en_dias=5)

    Operador.registrar_inscripcion(usuario(1), confirmado)    # u1 confirmado
    Operador.registrar_inscripcion(usuario(2), confirmado)    # u2 espera en el mismo taller
    Operador.registrar_inscripcion(usuario(3), lleno)         # u3 ocupa la única plaza
    Operador.registrar_inscripcion(usuario(1), lleno)         # u1 queda en espera
    Operador.registrar_inscripcion(usuario(1), a_cancelar)
    registrar_cancelaciones(usuario(1), 3)

    Operador.cancelar_inscripcion(usuario(1), a_cancelar)     # 4.ª cancelación -> bloqueo

    assert estado(1, confirmado) == "CANCELADO"   # pierde su plaza confirmada
    assert estado(2, confirmado) == "CONFIRMADO"  # el que esperaba la ocupa
    assert estado(1, lleno) == "CANCELADO"        # sale de la lista de espera
    with pytest.raises(ValidationError):
        Operador.registrar_inscripcion(usuario(1), taller("TAL-DAN-01", empieza_en_dias=6))


def test_pasadas_las_24_horas_puede_volver_a_inscribirse():
    registrar_cancelaciones(usuario(1), 4, hace_horas=25)
    inscripcion = Operador.registrar_inscripcion(usuario(1), taller("TAL-DAN-01"))
    assert inscripcion.estado == "CONFIRMADO"


def test_historial_ordenado_de_la_mas_reciente_a_la_mas_antigua():
    registrar_cancelaciones(usuario(1), 1, hace_horas=50)
    registrar_cancelaciones(usuario(1), 1, hace_horas=2)
    registrar_cancelaciones(usuario(1), 1, hace_horas=10)
    fechas = [c.fecha_cancelacion for c in Operador.consultar_historial_cancelaciones(usuario(1))]
    assert fechas == sorted(fechas, reverse=True)