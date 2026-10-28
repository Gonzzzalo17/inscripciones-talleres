import pytest

from inscripciones.servicios.instructor import Instructor
from inscripciones.servicios.operador import Operador
from tests.test_operador import padron, solicitar, taller, usuario

# HU-11 / CU-15: el instructor ve solo a los confirmados de su taller.
pytestmark = pytest.mark.django_db(databases=["default", "estudiantes_db"])


def test_lista_del_instructor_trae_confirmados_y_no_los_de_espera():
    danza = taller(codigo="DAN-INS-01", cupo=2)
    solicitar(1, danza)
    solicitar(2, danza)
    solicitar(3, danza)            # no hay plaza: queda en espera

    assert set(Instructor.listar_confirmados(danza)) == {usuario(1), usuario(2)}


def test_quien_cancela_ya_no_aparece_en_la_lista():
    danza = taller(codigo="DAN-INS-01", cupo=2)
    solicitar(1, danza)
    solicitar(2, danza)
    Operador.cancelar_inscripcion(usuario(1), danza)

    assert set(Instructor.listar_confirmados(danza)) == {usuario(2)}


def test_no_mezcla_confirmados_de_otro_taller():
    danza = taller(codigo="DAN-INS-01", cupo=2, empieza_en_horas=5)
    pintura = taller(codigo="PIN-INS-01", cupo=2, empieza_en_horas=10)
    solicitar(1, danza)
    solicitar(2, pintura)

    assert set(Instructor.listar_confirmados(danza)) == {usuario(1)}


def test_taller_sin_confirmados_devuelve_lista_vacia():
    danza = taller(codigo="DAN-INS-01", cupo=2)

    assert Instructor.listar_confirmados(danza).count() == 0