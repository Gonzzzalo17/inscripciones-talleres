from django.urls import path

from . import views

urlpatterns = [
    path('entrar/', views.iniciar_sesion, name='login'),
    path('salir/', views.cerrar_sesion, name='logout'),
    path('registrarse/', views.registrarse, name='registro'),
    path('', views.lista_talleres, name='lista_talleres'),
    path('talleres/nuevo/', views.crear_taller, name='crear_taller'),
    path('talleres/<int:pk>/decidir/', views.decidir_taller, name='decidir_taller'),
    path('talleres/<int:pk>/inscribirse/', views.solicitar_inscripcion, name='solicitar_inscripcion'),
    path('inscripciones/<int:pk>/', views.resultado_inscripcion, name='resultado_inscripcion'),
    path('mis-inscripciones/', views.mis_inscripciones, name='mis_inscripciones'),
    path('inscripciones/<int:pk>/cancelar/', views.cancelar_inscripcion, name='cancelar_inscripcion'),
    path('talleres/<int:pk>/ocupacion/', views.ocupacion_taller, name='ocupacion_taller'),
    path('historial-cancelaciones/', views.historial_cancelaciones, name='historial_cancelaciones'),
    path('buscar-inscripciones/', views.buscar_inscripciones, name='buscar_inscripciones'),
    path('talleres/<int:pk>/editar/', views.editar_taller, name='editar_taller'),
    path('talleres/pendientes/', views.talleres_pendientes,name='talleres_pendientes'),
    path('operador/categorias-motivos/', views.gestionar_categorias_motivos, name='gestionar_categorias_motivos'),
    path('historial-cancelaciones/<int:participante_id>/levantar-bloqueo/', views.levantar_bloqueo, name='levantar_bloqueo'),
    path('talleres/<int:pk>/cancelar/', views.cancelar_taller, name='cancelar_taller'),
    path('notificaciones/', views.notificaciones, name='notificaciones'),
    path('talleres/por-categoria/', views.talleres_por_categoria, name='talleres_por_categoria'),
]