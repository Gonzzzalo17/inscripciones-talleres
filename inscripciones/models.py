from django.db import models
from django.contrib.auth.models import AbstractUser

porcentaje_lista_espera = 0.20
horas_limite_cancelacion = 3

class EstudianteEstatico(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    class Meta:
        managed = False  # IMPORTANTE: Indica a Django que NO cree ni modifique esta tabla (es de solo lectura/estática)
        db_table = 'estudiantes'  # Nombre de la tabla exacta en tu BD estática


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

    def __str__(self):
        return f"Coordinador: {self.usuario.username}"


class Operador(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return f"Operador: {self.usuario.username}"


class Participante(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return f"Participante: {self.usuario.username}"


class Instructor(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return f"Instructor: {self.usuario.username}"


# 3. Modelos de Inscripción e Historial (Andrea)
class Taller(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    cupo_maximo = models.PositiveIntegerField(default=30)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()

    def __str__(self):
        return self.nombre
class Inscripcion(models.Model):
    ESTADOS = [
        ('CONFIRMADO', 'Confirmado'),
        ('EN_ESPERA', 'En Espera'),
        ('CANCELADO', 'Cancelado'),
    ]

    participante = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='inscripciones')
    taller = models.ForeignKey('Taller', on_delete=models.CASCADE, related_name='inscripciones')
    estado = models.CharField(max_length=20, choices=ESTADOS, default='CONFIRMADO')
    posicion_espera = models.PositiveIntegerField(null=True, blank=True)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('participante', 'taller')

    def __str__(self):
        return f"{self.participante.username} - {self.taller} ({self.estado})"


class HistorialCancelacion(models.Model):
    participante = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='cancelaciones')
    taller = models.ForeignKey('Taller', on_delete=models.CASCADE)
    fecha_cancelacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cancelación: {self.participante.username} - {self.taller}"