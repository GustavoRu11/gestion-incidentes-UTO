from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('incidentes/', views.lista_incidentes, name='lista_incidentes'),
    path('incidentes/nuevo/', views.crear_incidente, name='crear_incidente'),
    path('incidentes/<int:pk>/', views.detalle_incidente, name='detalle_incidente'),
    path('reportes/', views.reportes, name='reportes'),
    path('bitacora/', views.bitacora, name='bitacora'),
    path('notificaciones/', views.notificaciones, name='notificaciones'),
]