from django.core.exceptions import ValidationError
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import TallerForm
from .models import Inscripcion, Taller, Usuario
from .servicios.operador import Operador, porcentaje_lista_espera


def lista_talleres(request):
    talleres = Taller.objects.annotate(
        ocupadas=Count('inscripciones', filter=Q(inscripciones__estado='CONFIRMADO')),
        en_espera=Count('inscripciones', filter=Q(inscripciones__estado='EN_ESPERA')),
    ).order_by('fecha_inicio')
    return render(request, 'inscripciones/lista_talleres.html', {'talleres': talleres})


def crear_taller(request):
    if request.method == 'POST':
        form = TallerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_talleres')
    else:
        form = TallerForm()
    return render(request, 'inscripciones/crear_taller.html', {'form': form})


def solicitar_inscripcion(request, pk):
    taller = get_object_or_404(Taller, pk=pk)
    participantes = Usuario.objects.filter(rol=Usuario.Rol.PARTICIPANTE).order_by('username')
    error = None
    participante_seleccionado = ''

    if request.method == 'POST':
        participante_seleccionado = request.POST.get('participante', '')
        participante = None
        if participante_seleccionado.isdigit():
            participante = participantes.filter(pk=participante_seleccionado).first()

        if participante is None:
            error = "Elige un participante de la lista."
        else:
            try:
                inscripcion = Operador.registrar_inscripcion(participante, taller)
            except ValidationError as e:
                error = e.messages[0]
            else:
                return redirect('resultado_inscripcion', pk=inscripcion.pk)

    contexto = {
        'taller': taller,
        'ocupadas': taller.inscripciones.filter(estado='CONFIRMADO').count(),
        'en_espera': taller.inscripciones.filter(estado='EN_ESPERA').count(),
        'limite_espera': int(taller.cupo_maximo * porcentaje_lista_espera),
        'participantes': participantes,
        'error': error,
        'participante_seleccionado': participante_seleccionado,
    }
    return render(request, 'inscripciones/solicitar_inscripcion.html', contexto)


def resultado_inscripcion(request, pk):
    inscripcion = get_object_or_404(Inscripcion, pk=pk)
    return render(request, 'inscripciones/resultado_inscripcion.html', {'inscripcion': inscripcion})