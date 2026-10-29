from django.urls import path

from . import views

urlpatterns = [
    path('', views.lista_talleres, name='lista_talleres'),
    path('talleres/nuevo/', views.crear_taller, name='crear_taller'),
    path('talleres/<int:pk>/inscribirse/', views.solicitar_inscripcion, name='solicitar_inscripcion'),
    path('inscripciones/<int:pk>/', views.resultado_inscripcion, name='resultado_inscripcion'),
    path('mis-inscripciones/', views.mis_inscripciones, name='mis_inscripciones'),
    path('talleres/<int:pk>/ocupacion/', views.ocupacion_taller, name='ocupacion_taller'),
    path('historial-cancelaciones/', views.historial_cancelaciones, name='historial_cancelaciones'),
]