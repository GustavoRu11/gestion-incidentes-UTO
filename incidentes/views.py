from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Perfil, Incidente, Categoria, Bitacora, Notificacion
from .forms import IncidenteForm, AsignarTecnicoForm

# Función para obtener el rol del usuario
def get_rol(user):
    try:
        return Perfil.objects.get(usuario=user).rol
    except Perfil.DoesNotExist:
        return 'administrador'

# Función para obtener notificaciones no leídas
def get_notificaciones_count(user):
    return Notificacion.objects.filter(usuario=user, leida=False).count()

# Vista de login
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    return render(request, 'incidentes/login.html')

# Vista de logout
def logout_view(request):
    logout(request)
    return redirect('login')

# Vista del dashboard
@login_required(login_url='login')
def dashboard(request):
    from django.utils import timezone
    from datetime import timedelta

    rol = get_rol(request.user)
    total_abiertos = Incidente.objects.filter(estado='abierto').count()
    total_en_proceso = Incidente.objects.filter(estado='en_proceso').count()
    total_escalados = Incidente.objects.filter(estado='escalado').count()
    total_cerrados = Incidente.objects.filter(estado='cerrado').count()
    ultimos_incidentes = Incidente.objects.all().order_by('-fecha_creacion')[:5]

    categorias = Categoria.objects.all()
    categorias_data = []
    for cat in categorias:
        categorias_data.append({
            'nombre': cat.nombre,
            'total': Incidente.objects.filter(categoria=cat).count()
        })

    sla_horas = {'critica': 4, 'alta': 8, 'media': 24, 'baja': 72}
    ahora = timezone.now()
    total_vencidos = 0
    for incidente in Incidente.objects.exclude(estado='cerrado'):
        limite = sla_horas.get(incidente.prioridad, 72)
        if ahora > incidente.fecha_creacion + timedelta(hours=limite):
            total_vencidos += 1

    context = {
        'rol': rol,
        'total_abiertos': total_abiertos,
        'total_en_proceso': total_en_proceso,
        'total_escalados': total_escalados,
        'total_cerrados': total_cerrados,
        'ultimos_incidentes': ultimos_incidentes,
        'categorias_data': categorias_data,
        'total_vencidos': total_vencidos,
        'notificaciones_count': get_notificaciones_count(request.user),
    }
    return render(request, 'incidentes/dashboard.html', context)

# Vista para crear incidente
@login_required(login_url='login')
def crear_incidente(request):
    rol = get_rol(request.user)
    if request.method == 'POST':
        form = IncidenteForm(request.POST)
        if form.is_valid():
            incidente = form.save(commit=False)
            incidente.reportado_por = request.user
            incidente.save()
            Bitacora.objects.create(
                incidente=incidente,
                usuario=request.user,
                campo_modificado='estado',
                valor_anterior='',
                valor_nuevo='abierto'
            )
            # Notificar a administradores y jefe_dti
            admins = User.objects.filter(perfil__rol__in=['administrador', 'jefe_dti'])
            for admin in admins:
                Notificacion.objects.create(
                    usuario=admin,
                    mensaje=f'Nuevo incidente creado: "{incidente.titulo}" por {request.user.username}',
                    incidente=incidente
                )
            messages.success(request, 'Incidente creado exitosamente.')
            return redirect('lista_incidentes')
    else:
        form = IncidenteForm()
    return render(request, 'incidentes/crear_incidente.html', {'form': form, 'rol': rol, 'notificaciones_count': get_notificaciones_count(request.user)})

# Vista para listar incidentes
@login_required(login_url='login')
def lista_incidentes(request):
    from django.utils import timezone
    from datetime import timedelta

    rol = get_rol(request.user)
    if rol == 'usuario_final':
        incidentes = Incidente.objects.filter(reportado_por=request.user).order_by('-fecha_creacion')
    elif rol == 'tecnico':
        incidentes = Incidente.objects.filter(asignado_a=request.user).order_by('-fecha_creacion')
    else:
        incidentes = Incidente.objects.all().order_by('-fecha_creacion')

    sla_horas = {'critica': 4, 'alta': 8, 'media': 24, 'baja': 72}
    ahora = timezone.now()
    for incidente in incidentes:
        limite = sla_horas.get(incidente.prioridad, 72)
        if incidente.estado != 'cerrado' and ahora > incidente.fecha_creacion + timedelta(hours=limite):
            incidente.vencido = True
        else:
            incidente.vencido = False

    return render(request, 'incidentes/lista_incidentes.html', {
        'incidentes': incidentes,
        'rol': rol,
        'notificaciones_count': get_notificaciones_count(request.user)
    })

# Vista para ver detalle y gestionar incidente
@login_required(login_url='login')
def detalle_incidente(request, pk):
    rol = get_rol(request.user)
    incidente = get_object_or_404(Incidente, pk=pk)
    bitacora = Bitacora.objects.filter(incidente=incidente).order_by('-fecha')
    form = AsignarTecnicoForm(instance=incidente)
    if request.method == 'POST':
        if rol in ['administrador', 'jefe_dti', 'tecnico']:
            estado_anterior = incidente.estado
            asignado_anterior = str(incidente.asignado_a)
            form = AsignarTecnicoForm(request.POST, instance=incidente)
            if form.is_valid():
                incidente_actualizado = form.save()
                if estado_anterior != incidente_actualizado.estado:
                    Bitacora.objects.create(
                        incidente=incidente_actualizado,
                        usuario=request.user,
                        campo_modificado='estado',
                        valor_anterior=estado_anterior,
                        valor_nuevo=incidente_actualizado.estado
                    )
                    Notificacion.objects.create(
                        usuario=incidente_actualizado.reportado_por,
                        mensaje=f'Tu incidente "{incidente_actualizado.titulo}" cambió de estado a {incidente_actualizado.get_estado_display()}',
                        incidente=incidente_actualizado
                    )
                if incidente_actualizado.asignado_a and asignado_anterior != str(incidente_actualizado.asignado_a):
                    Bitacora.objects.create(
                        incidente=incidente_actualizado,
                        usuario=request.user,
                        campo_modificado='asignado_a',
                        valor_anterior=asignado_anterior,
                        valor_nuevo=str(incidente_actualizado.asignado_a)
                    )
                    Notificacion.objects.create(
                        usuario=incidente_actualizado.asignado_a,
                        mensaje=f'Se te asignó el incidente "{incidente_actualizado.titulo}"',
                        incidente=incidente_actualizado
                    )
                messages.success(request, 'Incidente actualizado correctamente.')
                return redirect('detalle_incidente', pk=pk)
    context = {
        'incidente': incidente,
        'bitacora': bitacora,
        'form': form,
        'rol': rol,
        'notificaciones_count': get_notificaciones_count(request.user),
    }
    return render(request, 'incidentes/detalle_incidente.html', context)

# Vista de reportes
@login_required(login_url='login')
def reportes(request):
    rol = get_rol(request.user)
    if rol not in ['administrador', 'jefe_dti']:
        return redirect('dashboard')

    incidentes = Incidente.objects.all().order_by('-fecha_creacion')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    estado = request.GET.get('estado')
    categoria = request.GET.get('categoria')

    if fecha_inicio:
        incidentes = incidentes.filter(fecha_creacion__date__gte=fecha_inicio)
    if fecha_fin:
        incidentes = incidentes.filter(fecha_creacion__date__lte=fecha_fin)
    if estado:
        incidentes = incidentes.filter(estado=estado)
    if categoria:
        incidentes = incidentes.filter(categoria__id=categoria)

    categorias = Categoria.objects.all()
    context = {
        'rol': rol,
        'incidentes': incidentes,
        'categorias': categorias,
        'total': incidentes.count(),
        'notificaciones_count': get_notificaciones_count(request.user),
    }
    return render(request, 'incidentes/reportes.html', context)

# Vista de bitácora
@login_required(login_url='login')
def bitacora(request):
    rol = get_rol(request.user)
    if rol not in ['administrador', 'jefe_dti']:
        return redirect('dashboard')

    registros = Bitacora.objects.all().order_by('-fecha')
    context = {
        'rol': rol,
        'registros': registros,
        'notificaciones_count': get_notificaciones_count(request.user),
    }
    return render(request, 'incidentes/bitacora.html', context)

# Vista de notificaciones
@login_required(login_url='login')
def notificaciones(request):
    rol = get_rol(request.user)
    notifs = Notificacion.objects.filter(usuario=request.user).order_by('-fecha')
    notifs.update(leida=True)
    return render(request, 'incidentes/notificaciones.html', {
        'notificaciones': notifs,
        'rol': rol,
        'notificaciones_count': 0,
    })