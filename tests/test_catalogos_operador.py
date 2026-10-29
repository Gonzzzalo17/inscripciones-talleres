
import pytest
from django.core.exceptions import ValidationError

from inscripciones.models import Categoria, MotivoEdicion, Usuario
from inscripciones.servicios.operador import Operador

pytestmark = pytest.mark.django_db


@pytest.fixture
def operador():
    return Usuario.objects.create_user(
        username="operador_catalogos",
        password="test123",
        rol=Usuario.Rol.OPERADOR,
    )


@pytest.fixture
def coordinador():
    return Usuario.objects.create_user(
        username="coordinador_catalogos",
        password="test123",
        rol=Usuario.Rol.COORDINADOR,
    )


def test_operador_puede_agregar_categoria(operador):
    categoria = Operador.agregar_categoria(operador, "Música")

    assert categoria.nombre == "Música"
    assert Categoria.objects.filter(nombre="Música").exists()


def test_solo_operador_puede_agregar_categoria(coordinador):
    with pytest.raises(ValidationError):
        Operador.agregar_categoria(coordinador, "Música")

    assert not Categoria.objects.filter(nombre="Música").exists()


@pytest.mark.parametrize("nombre", ["", "   "])
def test_no_permite_categoria_vacia(operador, nombre):
    with pytest.raises(ValidationError):
        Operador.agregar_categoria(operador, nombre)


def test_no_permite_categoria_duplicada(operador):
    Operador.agregar_categoria(operador, "Música")

    with pytest.raises(ValidationError):
        Operador.agregar_categoria(operador, "Música")


def test_operador_puede_agregar_motivo(operador):
    motivo = Operador.agregar_motivo_edicion(
        operador, "Cambio de horario"
    )

    assert motivo.descripcion == "Cambio de horario"
    assert MotivoEdicion.objects.filter(
        descripcion="Cambio de horario"
    ).exists()


def test_solo_operador_puede_agregar_motivo(coordinador):
    with pytest.raises(ValidationError):
        Operador.agregar_motivo_edicion(
            coordinador, "Cambio de horario"
        )

    assert not MotivoEdicion.objects.filter(
        descripcion="Cambio de horario"
    ).exists()


@pytest.mark.parametrize("descripcion", ["", "   "])
def test_no_permite_motivo_vacio(operador, descripcion):
    with pytest.raises(ValidationError):
        Operador.agregar_motivo_edicion(operador, descripcion)


def test_no_permite_motivo_duplicado(operador):
    Operador.agregar_motivo_edicion(operador, "Cambio de horario")

    with pytest.raises(ValidationError):
        Operador.agregar_motivo_edicion(
            operador, "Cambio de horario"
        )
