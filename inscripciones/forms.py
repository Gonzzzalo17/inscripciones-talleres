from django import forms

from .models import Taller


class TallerForm(forms.ModelForm):
    class Meta:
        model = Taller
        fields = ['codigo', 'cupo_maximo', 'fecha_inicio', 'fecha_fin']
        labels = {
            'codigo': 'Código del taller',
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
        return datos