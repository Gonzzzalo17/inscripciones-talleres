from inscripciones.models import Notificacion

# Avisos en pantalla. Se guardan en la base de datos y
# los ve en su botón "Notificaciones"

def notificar(usuario, taller, mensaje):
    return Notificacion.objects.create(participante=usuario, taller=taller, mensaje=mensaje)

def listar_notificaciones(usuario):
    # La más nueva primero.
    return (Notificacion.objects.filter(participante=usuario)
            .select_related("taller")
            .order_by("-fecha", "-id"))

def contar_no_leidas(usuario):
    return Notificacion.objects.filter(participante=usuario, leida=False).count()

def marcar_todas_como_leidas(usuario):
    return Notificacion.objects.filter(participante=usuario, leida=False).update(leida=True)