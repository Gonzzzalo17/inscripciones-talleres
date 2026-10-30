from django import forms
from datetime import timedelta
from django.utils import timezone
from .models import Taller, MotivoEdicion


class TallerForm(forms.ModelForm):
    cupo_maximo = forms.IntegerField(
        min_value=4,
        max_value=40,
        error_messages={
            'min_value': 'El cupo mínimo permitido es 4.',
            'max_value': 'El cupo máximo permitido es 40.',
            'invalid': 'Ingresa un número válido.',
        }
    )
    class Meta:
        model = Taller
        fields = ['nombre','categoria', 'cupo_maximo', 'fecha_inicio', 'fecha_fin']
        labels = {
            'nombre': 'Nombre del taller',
            'categoria': 'Categoria',
            'cupo_maximo': 'Cupo máximo',
            'fecha_inicio': 'Inicio',
            'fecha_fin': 'Fin',
        }
        widgets = {
            'fecha_inicio': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'fecha_fin': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        }

    def clean(self):
        datos = super().clean()
        inicio = datos.get('fecha_inicio')
        fin = datos.get('fecha_fin')

        if inicio and inicio <= timezone.now():
            self.add_error(
                'fecha_inicio',
                'La fecha y hora de inicio deben ser futura.'
            )

        if inicio and fin:
            if fin <= inicio:
                self.add_error(
                    'fecha_fin',
                    'La fecha de fin debe ser posterior al inicio.'
                )
            elif fin > inicio + timedelta(days=7):
                self.add_error(
                    'fecha_fin',
                    'La duración del taller no puede superar los 7 días.'
                )

        return datos

class EditarTallerForm(forms.ModelForm):
    cupo_maximo = forms.IntegerField(
        min_value=4,
        max_value=40,
        error_messages={
            'min_value': 'El cupo mínimo permitido es 4.',
            'max_value': 'El cupo máximo permitido es 40.',
            'invalid': 'Ingresa un número válido.',
        }
    )
    motivo = forms.ModelChoiceField(
        queryset=MotivoEdicion.objects.all(),
        label="Motivo de edición",
        empty_label="Seleccione un motivo",
        required=True,
    )

    class Meta:
        model = Taller
        fields = ['cupo_maximo', 'fecha_inicio', 'fecha_fin']
        labels = {
            'cupo_maximo': 'Cupo máximo',
            'fecha_inicio': 'Inicio',
            'fecha_fin': 'Fin',
        }
        widgets = {
            'fecha_inicio': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
            'fecha_fin': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
        }

    def clean(self):
        datos = super().clean()
        inicio = datos.get('fecha_inicio')
        fin = datos.get('fecha_fin')
        if inicio and inicio <= timezone.now():
            self.add_error(
                'fecha_inicio',
                'La fecha y hora de inicio debe ser futura.'
            )

        if inicio and fin:
            if fin <= inicio:
                self.add_error(
                    'fecha_fin',
                    'La fecha de fin debe ser posterior al inicio.'
                )
            elif fin > inicio + timedelta(days=7):
                self.add_error(
                    'fecha_fin',
                    'La duración del taller no puede superar los 7 días.'
                )

        return datos
