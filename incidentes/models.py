from django.db import models
from django.contrib.auth.models import User

# Roles disponibles para los usuarios
class Perfil(models.Model):
    ROL_CHOICES = [
        ('usuario_final', 'Usuario Final'),
        ('tecnico', 'Técnico'),
        ('administrador', 'Administrador'),
        ('jefe_dti', 'Jefe DTI'),
    ]
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='usuario_final')

    def __str__(self):
        return f'{self.usuario.username} - {self.rol}'

# Categorías de incidentes
class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre

# Modelo principal de incidentes
class Incidente(models.Model):
    PRIORIDAD_CHOICES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('critica', 'Crítica'),
    ]
    ESTADO_CHOICES = [
        ('abierto', 'Abierto'),
        ('en_proceso', 'En Proceso'),
        ('escalado', 'Escalado'),
        ('cerrado', 'Cerrado'),
    ]
    IMPACTO_CHOICES = [(i, str(i)) for i in range(1, 6)]
    URGENCIA_CHOICES = [(i, str(i)) for i in range(1, 6)]

    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True)
    impacto = models.IntegerField(choices=IMPACTO_CHOICES, default=1)
    urgencia = models.IntegerField(choices=URGENCIA_CHOICES, default=1)
    prioridad = models.CharField(max_length=10, choices=PRIORIDAD_CHOICES, default='baja')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='abierto')
    reportado_por = models.ForeignKey(User, on_delete=models.CASCADE, related_name='incidentes_reportados')
    asignado_a = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='incidentes_asignados')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    fecha_cierre = models.DateTimeField(null=True, blank=True)

    def calcular_prioridad(self):
        valor = self.impacto * self.urgencia
        if valor <= 4:
            return 'baja'
        elif valor <= 9:
            return 'media'
        elif valor <= 19:
            return 'alta'
        else:
            return 'critica'

    def save(self, *args, **kwargs):
        self.prioridad = self.calcular_prioridad()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titulo

# Bitácora de auditoría
class Bitacora(models.Model):
    incidente = models.ForeignKey(Incidente, on_delete=models.CASCADE, related_name='bitacora')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    campo_modificado = models.CharField(max_length=100)
    valor_anterior = models.TextField(blank=True)
    valor_nuevo = models.TextField(blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.incidente} - {self.campo_modificado} - {self.fecha}'