from django import forms
from datetime import timedelta
from .models import Taller


class TallerForm(forms.ModelForm):
    class Meta:
        model = Taller
        fields = ['codigo', 'nombre', 'cupo_maximo', 'fecha_inicio', 'fecha_fin']
        labels = {
            'codigo': 'Código del taller',
            'nombre': 'Nombre del taller',
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
        if inicio and fin and fin <= inicio:
            raise forms.ValidationError("La fecha de fin debe ser posterior a la de inicio.")
        limite_maximo= inicio + timedelta(days=30)
        if fin>limite_maximo:
            raise forms.ValidationError("La duración del taller no puede superar los 30 días desde la fecha de inicio.")
        return datos