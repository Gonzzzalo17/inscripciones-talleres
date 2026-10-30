from django.core.exceptions import ValidationError
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from .forms import TallerForm,EditarTallerForm
from .models import Inscripcion, Taller, Usuario, Categoria, MotivoEdicion
from .servicios.operador import Operador
from .servicios.coordinador import Coordinador
from django.utils import timezone
from django.contrib.auth import login, logout
from django.views.decorators.http import require_POST
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.utils.http import url_has_allowed_host_and_scheme
from .acceso import solo_para, TODOS
from .servicios.sesion import Sesion
from .servicios.participante import Participante
from .servicios.permisos import puede_manejar_el_taller
from .servicios.notificaciones import listar_notificaciones, marcar_todas_como_leidas



@solo_para(*TODOS)
def lista_talleres(request):
    talleres = Taller.objects.annotate(
        ocupadas=Count('inscripciones', filter=Q(inscripciones__estado='CONFIRMADO')),
        en_espera=Count('inscripciones', filter=Q(inscripciones__estado='EN_ESPERA')),
    ).order_by('fecha_inicio')
    # El participante solo ve los talleres abiertos: aprobados y no cancelados
    if request.user.rol == Usuario.Rol.PARTICIPANTE:
        talleres = talleres.filter(estado=Taller.Estado.APROBADO, cancelado=False,
                                   fecha_inicio__gt=timezone.now())
        # El coordinador solo ve los talleres que él pidió
    elif request.user.rol == Usuario.Rol.COORDINADOR:
        talleres = talleres.filter(coordinador=request.user)
    return render(request, 'inscripciones/lista_talleres.html',
                  {'talleres': talleres, 'ahora': timezone.now()})


@solo_para(Usuario.Rol.COORDINADOR, Usuario.Rol.OPERADOR)
def crear_taller(request):
    if request.method == 'POST':
        form = TallerForm(request.POST)
        if form.is_valid():
            try:
                Coordinador.crear_taller(
                    nombre=form.cleaned_data['nombre'],
                    cupo_maximo=form.cleaned_data['cupo_maximo'],
                    fecha_inicio=form.cleaned_data['fecha_inicio'],
                    fecha_fin=form.cleaned_data['fecha_fin'],
                    categoria=form.cleaned_data['categoria'],
                    usuario_creador=request.user,
                )
            except ValidationError as e:
                error_msg = e.messages[0] if hasattr(e, 'messages') else str(e)
                form.add_error(None, error_msg)
            else:
                return redirect('lista_talleres')
    else:
        form = TallerForm()
    return render(request, 'inscripciones/crear_taller.html', {'form': form})

@solo_para(Usuario.Rol.PARTICIPANTE, Usuario.Rol.OPERADOR)
def solicitar_inscripcion(request, pk):
    taller = get_object_or_404(Taller, pk=pk)
    participantes = Usuario.objects.filter(rol=Usuario.Rol.PARTICIPANTE).order_by('username')
    # HU-12: el participante solo puede inscribirse a sí mismo; el operador elige a quién
    es_participante = request.user.rol == Usuario.Rol.PARTICIPANTE
    error = None
    participante_seleccionado = ''

    if request.method == 'POST':
        participante = None
        if es_participante:
            participante = request.user
        else:
            participante_seleccionado = request.POST.get('participante', '')
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
        'limite_espera': Operador.capacidad_lista_de_espera(taller.cupo_maximo),
        'participantes': participantes,
        'es_participante': es_participante,
        'error': error,
        'participante_seleccionado': participante_seleccionado,
    }
    return render(request, 'inscripciones/solicitar_inscripcion.html', contexto)


@solo_para(Usuario.Rol.PARTICIPANTE, Usuario.Rol.OPERADOR)
def resultado_inscripcion(request, pk):
    inscripcion = get_object_or_404(Inscripcion, pk=pk)
    # HU-12: un participante no puede ver la inscripción de otra persona
    if request.user.rol == Usuario.Rol.PARTICIPANTE and inscripcion.participante != request.user:
        return HttpResponseForbidden("No tienes permiso para ver esta página.")
    return render(request, 'inscripciones/resultado_inscripcion.html', {'inscripcion': inscripcion})


@solo_para(Usuario.Rol.PARTICIPANTE, Usuario.Rol.OPERADOR)
def mis_inscripciones(request):
    participantes = Usuario.objects.filter(rol=Usuario.Rol.PARTICIPANTE).order_by('username')
    inscripciones = []
    # HU-12: el participante ve directo las suyas; el operador elige de la lista
    es_participante = request.user.rol == Usuario.Rol.PARTICIPANTE
    if es_participante:
        participante_seleccionado = str(request.user.pk)
    else:
        participante_seleccionado = request.GET.get('participante', '')

    if participante_seleccionado.isdigit():
        participante = participantes.filter(pk=participante_seleccionado).first()
        if participante:
            inscripciones = Inscripcion.objects.filter(participante=participante).select_related('taller').order_by('taller__fecha_inicio')

    contexto = {
        'participantes': participantes,
        'inscripciones': inscripciones,
        'es_participante': es_participante,
        'participante_seleccionado': participante_seleccionado,
        'ahora': timezone.now(),
    }
    return render(request, 'inscripciones/mis_inscripciones.html', contexto)


@solo_para(Usuario.Rol.OPERADOR)
def historial_cancelaciones(request):
    """
    Vista para consultar el historial de cancelaciones de un participante
    y verificar si se encuentra bloqueado (baneado) actualmente.
    """
    participante_id = request.GET.get('participante_id')

    participantes = Usuario.objects.filter(rol=Usuario.Rol.PARTICIPANTE)
    participante = None
    historial = []
    fin_bloqueo = None
    sigue_bloqueado = False

    if participante_id and participante_id.isdigit():
        participante = get_object_or_404(Usuario, pk=participante_id, rol=Usuario.Rol.PARTICIPANTE)

        # 1. Obtener historial usando el método del Operador
        historial = Operador.consultar_historial_cancelaciones(participante)

        # 2. Calcular si está bloqueado y cuándo termina
        fin_bloqueo = Operador.calcular_fin_del_bloqueo(participante)
        if fin_bloqueo and fin_bloqueo > timezone.now():
            sigue_bloqueado = True

    contexto = {
        'participantes': participantes,
        'participante': participante,
        'historial': historial,
        'fin_bloqueo': fin_bloqueo,
        'sigue_bloqueado': sigue_bloqueado,
    }

    return render(request, 'inscripciones/historial_cancelaciones.html', contexto)

@solo_para(*TODOS)
def ocupacion_taller(request, pk):
    # HU-07: consultar la ocupación de un taller (solo lectura, no cambia datos)
    taller = get_object_or_404(Taller, pk=pk)
    # El coordinador solo ve la ocupación de sus propios talleres
    if request.user.rol == Usuario.Rol.COORDINADOR and taller.coordinador_id != request.user.pk:
        return HttpResponseForbidden("No tienes permiso para ver esta página.")
    ocupacion = Operador.calcular_ocupacion(taller)
    return render(request, 'inscripciones/ocupacion_taller.html', {
        'taller': taller,
        'ocupacion': ocupacion,
    })



@solo_para(Usuario.Rol.COORDINADOR, Usuario.Rol.OPERADOR)
def editar_taller(request, pk):
    taller = get_object_or_404(Taller, pk=pk)
    if taller.cancelado:
        messages.error(
            request,
            "No puedes editar un taller que ha sido cancelado."
        )
        return redirect('lista_talleres')
    if not puede_manejar_el_taller(request.user, taller):
        return HttpResponseForbidden(
            "No tienes permiso para editar este taller."
        )
    if request.method == 'POST':
        form = EditarTallerForm(request.POST, instance=taller)

        if form.is_valid():
            try:
                Coordinador.editar_taller(
                    taller_id=taller.pk,
                    cupo_maximo=form.cleaned_data['cupo_maximo'],
                    fecha_inicio=form.cleaned_data['fecha_inicio'],
                    fecha_fin=form.cleaned_data['fecha_fin'],
                    motivo=form.cleaned_data['motivo'],
                    usuario=request.user,
                )
            except ValidationError as e:
                error_msg = e.messages[0] if hasattr(e, 'messages') else str(e)
                form.add_error(None, error_msg)
            else:
                return redirect('lista_talleres')
    else:
        form = EditarTallerForm(instance=taller)

    contexto = {
        'form': form,
        'taller': taller,
    }
    return render(request, 'inscripciones/editar_taller.html', contexto)


def iniciar_sesion(request):
    # HU-12 / CU-20: pantalla de entrar con código y contraseña
    if request.user.is_authenticated:
        return redirect(Sesion.pantalla_de_inicio(request.user))

    error = None
    codigo = ''
    if request.method == 'POST':
        codigo = request.POST.get('codigo', '')
        try:
            usuario, pantalla = Sesion.iniciar_sesion(codigo, request.POST.get('contrasena', ''))
        except ValidationError as e:
            error = e.messages[0]
        else:
            login(request, usuario)  # guarda la sesión en el navegador
            siguiente = request.GET.get('next', '')
            # Solo vuelve a una página de este mismo sitio (evita mandar a sitios falsos)
            if not url_has_allowed_host_and_scheme(siguiente, allowed_hosts={request.get_host()}):
                siguiente = pantalla
            return redirect(siguiente)

    return render(request, 'inscripciones/login.html', {'error': error, 'codigo': codigo})


@require_POST
def cerrar_sesion(request):
    logout(request)
    return redirect('login')


def registrarse(request):
    # Gantt 66-67: el estudiante crea su cuenta con su código y una contraseña
    if request.user.is_authenticated:
        return redirect(Sesion.pantalla_de_inicio(request.user))

    errores = []
    codigo = ''
    if request.method == 'POST':
        codigo = request.POST.get('codigo', '').strip()
        contrasena = request.POST.get('contrasena', '')
        if contrasena != request.POST.get('repetir_contrasena', ''):
            errores = ["Las dos contraseñas no son iguales."]
        else:
            try:
                usuario = Participante.registrar_cuenta(codigo, contrasena)
            except ValidationError as e:
                errores = e.messages  # puede traer varios motivos (contraseña corta, muy común...)
            else:
                login(request, usuario)  # entra directo después de registrarse
                return redirect(Sesion.pantalla_de_inicio(usuario))

    return render(request, 'inscripciones/registro.html', {'errores': errores, 'codigo': codigo})


@solo_para(Usuario.Rol.PARTICIPANTE, Usuario.Rol.OPERADOR)
@require_POST
def cancelar_inscripcion(request, pk):
    # Gantt 34-35 / 40-41: botón "Cancelar" en Mis inscripciones
    inscripcion = get_object_or_404(Inscripcion, pk=pk)
    participante = inscripcion.participante
    # HU-12: el participante solo puede cancelar lo suyo; el operador, cualquiera
    if request.user.rol == Usuario.Rol.PARTICIPANTE and participante != request.user:
        return HttpResponseForbidden("No tienes permiso para ver esta página.")

    try:
        Operador.cancelar_inscripcion(participante, inscripcion.taller)
    except ValidationError as e:
        messages.error(request, e.messages[0])  # ej: "Ya pasó el tiempo límite para cancelar."
    else:
        messages.success(request, f"Se canceló la inscripción en {inscripcion.taller.nombre}.")
        # Regla del baneo: si con esta cancelación queda bloqueado, se le avisa
        fin_bloqueo = Operador.calcular_fin_del_bloqueo(participante)
        if fin_bloqueo and fin_bloqueo > timezone.now():
            messages.warning(request, f"Por cancelar muchas veces quedó bloqueado hasta el "
                                      f"{fin_bloqueo:%d/%m %H:%M} y perdió sus otras inscripciones.")

    if request.user.rol == Usuario.Rol.OPERADOR:
        return redirect(f"/mis-inscripciones/?participante={participante.pk}")
    return redirect('mis_inscripciones')


@solo_para(Usuario.Rol.OPERADOR)
def buscar_inscripciones(request):
    # Gantt 72-73: el operador busca inscripciones por participante (código, nombre)
    # o por taller (código, nombre)
    texto = request.GET.get('q', '').strip()
    resultados = Operador.buscar_inscripciones(texto) if texto else []
    return render(request, 'inscripciones/buscar_inscripciones.html',
                  {'texto': texto, 'resultados': resultados})


@solo_para(Usuario.Rol.OPERADOR)
@require_POST
def decidir_taller(request, pk):
    # El operador aprueba o rechaza un taller que pidió un coordinador
    taller = get_object_or_404(Taller, pk=pk)
    decision = request.POST.get('decision')
    try:
        if decision == 'aprobar':
            Operador.aprobar_taller(request.user, taller)
            messages.success(request, f"Se aprobó el taller {taller.nombre}. Ya recibe inscripciones.")
        elif decision == 'rechazar':
            Operador.rechazar_taller(request.user, taller)
            messages.success(request, f"Se rechazó el taller {taller.nombre}. El coordinador fue avisado.")
        else:
            messages.error(request, "Elige aprobar o rechazar.")
    except ValidationError as e:
        messages.error(request, e.messages[0])  # ej: "Solo se puede aceptar o rechazar un taller que está pendiente."
    return redirect('lista_talleres')

@solo_para(Usuario.Rol.OPERADOR)
def talleres_pendientes(request):
    talleres = (
        Taller.objects
        .filter(estado=Taller.Estado.PENDIENTE, cancelado=False)
        .select_related('categoria', 'coordinador')
        .annotate(
            ocupadas=Count(
                'inscripciones',
                filter=Q(inscripciones__estado='CONFIRMADO')
            ),
            en_espera=Count(
                'inscripciones',
                filter=Q(inscripciones__estado='EN_ESPERA')
            ),
        )
        .order_by('fecha_inicio')
    )

    return render(
        request,
        'inscripciones/talleres_pendientes.html',
        {'talleres': talleres}
    )

@solo_para(Usuario.Rol.OPERADOR)
def gestionar_categorias_motivos(request):
    if request.method == 'POST':
        tipo = request.POST.get('tipo')

        try:
            if tipo == 'categoria':
                Operador.agregar_categoria(
                    request.user,
                    request.POST.get('nombre', '')
                )
                messages.success(request, "Categoría agregada correctamente.")

            elif tipo == 'motivo':
                Operador.agregar_motivo_edicion(
                    request.user,
                    request.POST.get('descripcion', '')
                )
                messages.success(request, "Motivo agregado correctamente.")

            else:
                messages.error(request, "Tipo de registro no válido.")

        except ValidationError as e:
            messages.error(request, e.messages[0])

        return redirect('gestionar_categorias_motivos')

    contexto = {
        'categorias': Categoria.objects.all().order_by('nombre'),
        'motivos': MotivoEdicion.objects.all().order_by('descripcion'),
    }

    return render(
        request,
        'inscripciones/gestionar_categorias_motivos.html',
        contexto
    )

@solo_para(Usuario.Rol.OPERADOR)
@require_POST
def levantar_bloqueo(request, participante_id):
    participante = get_object_or_404(
        Usuario,
        pk=participante_id,
        rol=Usuario.Rol.PARTICIPANTE
    )

    try:
        Operador.levantar_bloqueo(request.user, participante)
        messages.success(
            request,
            f"Se levantó el bloqueo de {participante.username}."
        )
    except ValidationError as e:
        messages.error(request, e.messages[0])

    return redirect(
        f"/historial-cancelaciones/?participante_id={participante.pk}"
    )

@solo_para(Usuario.Rol.COORDINADOR, Usuario.Rol.OPERADOR)
@require_POST
def cancelar_taller(request, pk):
    taller = get_object_or_404(Taller, pk=pk)

    try:
        Operador.cancelar_taller(request.user, taller)
        messages.success(
            request,
            f"Se canceló el taller {taller.nombre}."
        )
    except ValidationError as e:
        messages.error(request, e.messages[0])

    return redirect('lista_talleres')

@solo_para(*TODOS)
def notificaciones(request):
    # Cada usuario ve sus avisos, el más nuevo primero. Al abrir la pantalla quedan como leídos.
    avisos = list(listar_notificaciones(request.user))     # se leen ANTES de marcarlos, para resaltar los nuevos
    marcar_todas_como_leidas(request.user)
    return render(request, 'inscripciones/notificaciones.html', {'avisos': avisos})


@solo_para(*TODOS)
def talleres_por_categoria(request):
    # El participante elige una categoría (o "Todas") y ve los talleres a los que todavía se puede inscribir.
    categorias = Categoria.objects.order_by('nombre')
    categoria_elegida = request.GET.get('categoria', '')
    categoria = categorias.filter(pk=categoria_elegida).first() if categoria_elegida.isdigit() else None
    contexto = {
        'categorias': categorias,
        'categoria_elegida': categoria_elegida,
        'talleres': Participante.buscar_talleres_por_categoria(categoria),
    }
    return render(request, 'inscripciones/talleres_por_categoria.html', contexto)

