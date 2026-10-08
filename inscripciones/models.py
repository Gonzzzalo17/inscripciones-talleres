from django.db import models
from django.contrib.auth.models import AbstractUser


# 1. Clase Base de Usuario (Hereda de AbstractUser de Django)
class Usuario(AbstractUser):
    class Rol(models.TextChoices):
        COORDINADOR = 'COORDINADOR', 'Coordinador'
        OPERADOR = 'OPERADOR', 'Operador'
        PARTICIPANTE = 'PARTICIPANTE', 'Participante'
        INSTRUCTOR = 'INSTRUCTOR', 'Instructor del Taller'

    rol = models.CharField(
        max_length=20,
        choices=Rol.choices,
        default=Rol.PARTICIPANTE
    )
    codigo = models.CharField(max_length=20, unique=True, null=True, blank=True)

    def __str__(self):
        return f"{self.username} ({self.get_rol_display()})"


# 2. Clases Hijas / Perfiles por Rol
class Coordinador(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)

    # Permiso/Método propio: Publicar talleres, definir cupos

    def __str__(self):
        return f"Coordinador: {self.usuario.username}"


class Operador(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)

    # Permiso/Método propio: Registrar inscripciones y cancelaciones

    def __str__(self):
        return f"Operador: {self.usuario.username}"


class Participante(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)

    # Permiso/Método propio: Solicitar plaza

    def __str__(self):
        return f"Participante: {self.usuario.username}"


class Instructor(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)

    # Permiso/Método propio: Consultar lista de confirmados

    def __str__(self):
        return f"Instructor: {self.usuario.username}"