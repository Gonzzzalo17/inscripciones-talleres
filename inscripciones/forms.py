from django import forms
from datetime import timedelta
from .models import Taller, MotivoEdicion


class TallerForm(forms.ModelForm):
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


class EditarTallerForm(forms.ModelForm):
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

        if inicio and fin and fin <= inicio:
            raise forms.ValidationError(
                "La fecha de fin debe ser posterior a la de inicio."
            )

        if inicio and fin and fin > inicio + timedelta(days=7):
            raise forms.ValidationError(
                "La duración del taller no puede superar los 7 días."
            )

        return datos

    def clean_categoria(self):
        categoria = self.cleaned_data.get('categoria')
        if categoria is None:
            raise forms.ValidationError(
                "La categoría del taller es obligatoria."
            )
        return categoria

    def clean(self):
        datos = super().clean()
        inicio = datos.get('fecha_inicio')
        fin = datos.get('fecha_fin')
        if inicio and fin and fin <= inicio:
            raise forms.ValidationError("La fecha de fin debe ser posterior a la de inicio.")
        if inicio and fin and fin > inicio + timedelta(days=7):
            raise forms.ValidationError("La duración del taller no puede superar los 7 días desde la fecha de inicio.")
        return datos