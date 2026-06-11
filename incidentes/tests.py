from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Perfil, Categoria, Incidente, Bitacora

class PruebasSistema(TestCase):

    def setUp(self):
        # Crear usuarios de prueba
        self.admin = User.objects.create_user(username='admin_test', password='admin123')
        Perfil.objects.create(usuario=self.admin, rol='administrador')

        self.tecnico = User.objects.create_user(username='tecnico_test', password='tecnico123')
        Perfil.objects.create(usuario=self.tecnico, rol='tecnico')

        self.usuario = User.objects.create_user(username='usuario_test', password='usuario123')
        Perfil.objects.create(usuario=self.usuario, rol='usuario_final')

        # Crear categoría de prueba
        self.categoria = Categoria.objects.create(nombre='Software', descripcion='Problemas de software')

        self.client = Client()

    def test_login_correcto(self):
        """Prueba que un usuario puede iniciar sesión correctamente"""
        response = self.client.post('/login/', {
            'username': 'admin_test',
            'password': 'admin123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/dashboard/')

    def test_login_fallido(self):
        """Prueba que un login con contraseña incorrecta falla"""
        response = self.client.post('/login/', {
            'username': 'admin_test',
            'password': 'incorrecta'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Usuario o contraseña incorrectos')

    def test_crear_incidente(self):
        """Prueba que se puede crear un incidente correctamente"""
        incidente = Incidente.objects.create(
            titulo='Fallo de red',
            descripcion='No hay conexión a internet',
            categoria=self.categoria,
            impacto=4,
            urgencia=5,
            reportado_por=self.usuario
        )
        self.assertEqual(Incidente.objects.count(), 1)
        self.assertEqual(incidente.titulo, 'Fallo de red')

    def test_calculo_prioridad(self):
        """Prueba que la prioridad se calcula correctamente según impacto x urgencia"""
        # Crítica: 4 x 5 = 20
        incidente = Incidente.objects.create(
            titulo='Prueba crítica',
            descripcion='Test',
            categoria=self.categoria,
            impacto=4,
            urgencia=5,
            reportado_por=self.usuario
        )
        self.assertEqual(incidente.prioridad, 'critica')

        # Baja: 1 x 1 = 1
        incidente2 = Incidente.objects.create(
            titulo='Prueba baja',
            descripcion='Test',
            categoria=self.categoria,
            impacto=1,
            urgencia=1,
            reportado_por=self.usuario
        )
        self.assertEqual(incidente2.prioridad, 'baja')

    def test_cambio_estado_registra_bitacora(self):
        """Prueba que al cambiar el estado se registra en la bitácora"""
        incidente = Incidente.objects.create(
            titulo='Prueba bitácora',
            descripcion='Test',
            categoria=self.categoria,
            impacto=3,
            urgencia=3,
            reportado_por=self.usuario
        )
        Bitacora.objects.create(
            incidente=incidente,
            usuario=self.admin,
            campo_modificado='estado',
            valor_anterior='abierto',
            valor_nuevo='en_proceso'
        )
        self.assertEqual(Bitacora.objects.filter(incidente=incidente).count(), 1)

    def test_acceso_dashboard_sin_login(self):
        """Prueba que el dashboard no es accesible sin iniciar sesión"""
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_usuario_final_no_ve_reportes(self):
        """Prueba que un usuario_final es redirigido si intenta acceder a reportes"""
        self.client.login(username='usuario_test', password='usuario123')
        response = self.client.get('/reportes/')
        self.assertEqual(response.status_code, 302)