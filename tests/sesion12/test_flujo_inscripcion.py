"""Sesión 12 - tres pruebas del flujo "Solicitar inscripción" (P03)."""
import copy
import pytest
from version_inicial.reglas_sesion04 import crear_taller, registrar_inscripcion


def cis_inscritos(taller):
    return [registro["id_participante"] for registro in taller.inscritos]


def datos_del_taller(taller):
    return (taller.id_taller, taller.nombreTaller, taller.categoriaTaller, taller.cupo_maximo)


def test_aceptacion_ultima_plaza_de_un_taller_de_cupo_2():
    # Taller de cupo 2 con una plaza ocupada: otra persona toma la última.
    taller = crear_taller("Oratoria", 2, "Comunicación")
    registrar_inscripcion(taller, "1111111")
    primer_registro_antes = copy.deepcopy(taller.inscritos[0])
    datos_antes = datos_del_taller(taller)

    resultado = registrar_inscripcion(taller, "2222222")

    assert resultado["estado"] == "CONFIRMADO"
    assert resultado["id_participante"] == "2222222"
    assert cis_inscritos(taller) == ["1111111", "2222222"]
    assert len(taller.inscritos) == taller.cupo_maximo
    assert taller.inscritos[0] == primer_registro_antes
    assert taller.inscritos[1] == resultado
    assert datos_del_taller(taller) == datos_antes


def test_rechaza_repeticion_no_crea_duplicado():
    # Rechazo / Repetición (P03): repetir su inscripción no crea un duplicado ni aumenta la ocupación.
    taller = crear_taller("Taller de Repetición", 2, "General")
    registrar_inscripcion(taller, "7654321")
    inscritos_antes = copy.deepcopy(taller.inscritos)  # copia independiente

    with pytest.raises(ValueError):
        registrar_inscripcion(taller, "7654321")

    assert taller.inscritos == inscritos_antes
    assert len(taller.inscritos) == 1
    assert cis_inscritos(taller).count("7654321") == 1


def test_limite_con_cupo_lleno_nunca_hay_un_tercer_confirmado():
    # Cupo 2 lleno: la siguiente solicitud queda en espera y no entra a los confirmados.
    taller = crear_taller("Fotografía", 2, "Arte")
    registrar_inscripcion(taller, "1111111")
    registrar_inscripcion(taller, "2222222")
    inscritos_antes = copy.deepcopy(taller.inscritos)
    datos_antes = datos_del_taller(taller)

    resultado = registrar_inscripcion(taller, "3333333")

    assert resultado["estado"] == "EN_ESPERA"
    assert resultado["estado"] != "CONFIRMADO"
    assert resultado["id_participante"] == "3333333"
    assert taller.inscritos == inscritos_antes
    assert len(taller.inscritos) <= taller.cupo_maximo
    assert "3333333" not in cis_inscritos(taller)
    assert datos_del_taller(taller) == datos_antes
