import pytest


@pytest.fixture(autouse=True)
def contrasenas_rapidas_solo_en_pruebas(settings):
    # Cifrar una contraseña de verdad tarda ~0.5 s a propósito (para que sea difícil de adivinar).
    # En las pruebas usamos un cifrado rápido; la aplicación real sigue usando el seguro.
    settings.PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]