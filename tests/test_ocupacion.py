import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from inscripciones.models import Taller, Inscripcion, Usuario
from inscripciones.servicios.operador import Operador

@pytest.mark.django_db
def test_calcular_ocupacion():
    # 1. Creamos un taller de prueba con cupo 10
    taller = Taller.objects.create(
        nombre="Taller de Prueba",
        codigo="TAL-PRUEBA-01",
        cupo_maximo=10,
        fecha_inicio=timezone.now() + timedelta(days=2),
        fecha_fin=timezone.now() + timedelta(days=3),
    )

    # Inicialmente todo debe estar en 0 / libres al máximo
    ocupacion_inicial = Operador.calcular_ocupacion(taller)
    assert ocupacion_inicial['ocupadas'] == 0
    assert ocupacion_inicial['libres'] == 10
    assert ocupacion_inicial['en_espera'] == 0
    assert ocupacion_inicial['maximo_espera'] == 2  # 20% de 10

    # 2. Consultar la ocupación no debe alterar ningún dato (prueba de no-mutación)
    Operador.calcular_ocupacion(taller)
    assert Taller.objects.filter(pk=taller.pk).count() == 1
    assert Inscripcion.objects.filter(taller=taller).count() == 0