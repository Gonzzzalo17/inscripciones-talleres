from django.contrib import admin
from .models import (
    Usuario,
    Coordinador,
    Operador,
    Participante,
    Categoria,
    MotivoEdicion,
    EstudianteEstatico,
    Taller,
    Inscripcion,
    HistorialCancelacion,
)


@admin.register(EstudianteEstatico)
class EstudianteEstaticoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'apellido', 'carrera')
    search_fields = ('codigo', 'nombre', 'apellido', 'carrera')

    def get_queryset(self, request):
        return super().get_queryset(request).using('estudiantes_db')

    def has_view_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


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
admin.site.register(Categoria)
admin.site.register(MotivoEdicion)
admin.site.register(HistorialCancelacion)

