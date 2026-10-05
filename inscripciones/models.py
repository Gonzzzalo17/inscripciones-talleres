from django.db import models
from django.contrib.auth.models import User

class Inscripcion(models.Model):
    ESTADOS = [
        ('CONFIRMADO', 'Confirmado'),
        ('EN_ESPERA', 'En Espera'),
        ('CANCELADO', 'Cancelado'),
    ]

    participante = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inscripciones')
    # Apunta al modelo Taller sin necesidad de definir la clase en este archivo
    taller = models.ForeignKey('Taller', on_delete=models.CASCADE, related_name='inscripciones')
    estado = models.CharField(max_length=20, choices=ESTADOS, default='CONFIRMADO')
    posicion_espera = models.PositiveIntegerField(null=True, blank=True)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('participante', 'taller')

    def __str__(self):
        return f"{self.participante.username} - {self.taller} ({self.estado})"


class HistorialCancelacion(models.Model):
    participante = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cancelaciones')
    taller = models.ForeignKey('Taller', on_delete=models.CASCADE)
    fecha_cancelacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cancelación: {self.participante.username} - {self.taller}"