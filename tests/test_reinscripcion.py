import pytest

from inscripciones.models import Inscripcion
from inscripciones.servicios.operador import Operador
from tests.test_operador import padron, solicitar, taller, usuario

# quien cancela y vuelve a pedir plaza cuenta como una persona nueva.
pytestmark = pytest.mark.django_db(databases=["default", "estudiantes_db"])


def inscripcion_de(i, t):
    return Inscripcion.objects.get(participante=usuario(i), taller=t)

def test_cancela_y_vuelve_a_pedir_con_plaza_libre_queda_confirmado_sin_duplicarse():
    t = taller(cupo=4, empieza_en_horas=24)
    solicitar(1, t)
    Operador.cancelar_inscripcion(usuario(1), t)

    solicitar(1, t)

    assert inscripcion_de(1, t).estado == "CONFIRMADO"
    assert Inscripcion.objects.filter(participante=usuario(1), taller=t).count() == 1   # reusa su fila

def test_cancela_y_vuelve_a_pedir_con_taller_lleno_queda_al_final_de_la_espera():
    t = taller(cupo=10, empieza_en_horas=24)
    for i in range(1, 12):               # 1 a 10 confirmados, 11 en espera
        solicitar(i, t)
    Operador.cancelar_inscripcion(usuario(1), t)   # 11 pasa a confirmado
    solicitar(12, t)                     # 12 queda primero en espera

    solicitar(1, t)                      # 1 vuelve a pedir

    assert (inscripcion_de(12, t).estado, inscripcion_de(12, t).posicion_espera) == ("EN_ESPERA", 1)
    assert (inscripcion_de(1, t).estado, inscripcion_de(1, t).posicion_espera) == ("EN_ESPERA", 2)