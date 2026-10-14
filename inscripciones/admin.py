from django.contrib import admin
from .models import (
    Usuario, Coordinador, Operador, Participante, Instructor,
    EstudianteEstatico, Taller, Inscripcion, HistorialCancelacion
)


@admin.register(EstudianteEstatico)
class EstudianteEstaticoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'apellido', 'email')
    search_fields = ('codigo', 'nombre', 'apellido')


@admin.register(Taller)
class TallerAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'cupo_maximo', 'fecha_inicio', 'fecha_fin')
    search_fields = ('codigo', 'nombre')


@admin.register(Inscripcion)
class InscripcionAdmin(admin.ModelAdmin):
    list_display = ('participante', 'taller', 'estado', 'posicion_espera')
    list_filter = ('estado', 'taller')


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('username', 'codigo', 'rol', 'email')
    list_filter = ('rol',)


admin.site.register(Coordinador)
admin.site.register(Operador)
admin.site.register(Participante)
admin.site.register(Instructor)
admin.site.register(HistorialCancelacion)
from django.contrib import admin

# Register your models here.
