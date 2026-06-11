from django.contrib import admin
from .models import Perfil, Categoria, Incidente, Bitacora

admin.site.register(Perfil)
admin.site.register(Categoria)
admin.site.register(Incidente)
admin.site.register(Bitacora)