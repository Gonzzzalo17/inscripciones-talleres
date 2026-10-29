import pytest

from inscripciones.models import Notificacion, Taller, Usuario
from inscripciones.servicios.notificaciones import (contar_no_leidas, listar_notificaciones,
                                                    marcar_todas_como_leidas)
from inscripciones.servicios.operador import Operador
from tests.test_operador import padron, solicitar, taller, usuario

# Gantt 103: cada evento deja un aviso para la persona afectada.
pytestmark = pytest.mark.django_db(databases=["default", "estudiantes_db"])


def avisos_de(persona):
    return Notificacion.objects.filter(participante=persona).count()

def quienes_recibieron_avisos_despues_de(ultimo_id):
    return set(Notificacion.objects.filter(id__gt=ultimo_id).values_list("participante__username", flat=True))

def ultimo_aviso_id():
    return Notificacion.objects.order_by("-id").values_list("id", flat=True).first() or 0

def test_inscribirse_avisa_a_cada_uno_este_confirmado_o_en_espera():
    t = taller(cupo=2)
    for i in (1, 2, 3):                  # 1 y 2 confirmados, 3 en espera
        solicitar(i, t)

    assert [avisos_de(usuario(i)) for i in (1, 2, 3)] == [1, 1, 1]

def test_cancelar_avisa_al_que_cancela_y_al_que_pasa_de_espera_a_confirmado():
    t = taller(cupo=2, empieza_en_horas=24)
    for i in (1, 2, 3):                  # 3 queda en espera
        solicitar(i, t)
    antes = ultimo_aviso_id()

    Operador.cancelar_inscripcion(usuario(1), t)

    assert quienes_recibieron_avisos_despues_de(antes) == {"u1", "u3"}   # 2 no recibe nada

def test_la_cuarta_cancelacion_avisa_tambien_el_bloqueo():
    talleres = [taller(codigo=f"BLO-{n}", cupo=5, empieza_en_horas=24 + 3 * n) for n in range(4)]
    for t in talleres[:3]:
        solicitar(1, t)
        Operador.cancelar_inscripcion(usuario(1), t)
    solicitar(1, talleres[3])
    antes = avisos_de(usuario(1))

    Operador.cancelar_inscripcion(usuario(1), talleres[3])     # la cuarta en 72 h: bloqueo

    assert avisos_de(usuario(1)) == antes + 2                  # "cancelaste" + "quedaste bloqueado"

def test_aprobar_o_rechazar_avisa_al_coordinador_del_taller():
    operador = Usuario.objects.create(username="operador", rol=Usuario.Rol.OPERADOR)
    coordinadora = Usuario.objects.create(username="coordinadora", rol=Usuario.Rol.COORDINADOR)
    danza = taller(codigo="DAN-AVI-01", cupo=5)
    pintura = taller(codigo="PIN-AVI-01", cupo=5)
    Taller.objects.filter(pk__in=[danza.pk, pintura.pk]).update(estado=Taller.Estado.PENDIENTE,
                                                                 coordinador=coordinadora)

    Operador.aprobar_taller(operador, danza)
    Operador.rechazar_taller(operador, pintura)

    assert avisos_de(coordinadora) == 2

def test_ver_notificaciones_la_mas_nueva_primero_y_marcarlas_como_leidas():
    danza = taller(codigo="DAN-LEE-01", cupo=5, empieza_en_horas=5)
    pintura = taller(codigo="PIN-LEE-01", cupo=5, empieza_en_horas=10)
    solicitar(1, danza)
    solicitar(1, pintura)

    assert [aviso.taller for aviso in listar_notificaciones(usuario(1))] == [pintura, danza]
    assert contar_no_leidas(usuario(1)) == 2
    marcar_todas_como_leidas(usuario(1))
    assert contar_no_leidas(usuario(1)) == 0