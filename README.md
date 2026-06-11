# Sistema Web de Gestión de Incidentes Tecnológicos - UTO

Sistema desarrollado como proyecto académico para la Universidad Tecnológica del Occidente (UTO), bajo el enfoque del Project Management Institute (PMI/PMBOK).

## Descripción
Plataforma web que permite al Departamento de Tecnología de la Información (DTI) gestionar incidentes tecnológicos de forma centralizada, con trazabilidad, control de SLA y reportes estadísticos.

## Tecnologías utilizadas
- Python 3.14
- Django 6.0.6
- SQLite
- Bootstrap 5
- Chart.js

## Roles del sistema
- Administrador: acceso total al sistema
- Jefe DTI: acceso total al sistema
- Técnico: gestiona incidentes asignados
- Usuario Final: reporta y consulta sus incidentes

## Requisitos previos
- Python 3.11 o superior
- pip

## Instalación

1. Clona el repositorio
git clone https://github.com/GustavoRu11/gestion-incidentes-UTO.git
cd gestion-incidentes-UTO

2. Crea y activa el entorno virtual
python -m venv venv
venv\Scripts\activate

3. Instala las dependencias
pip install django

4. Aplica las migraciones
python manage.py migrate

5. Crea el superusuario
python manage.py createsuperuser

6. Ejecuta el servidor
python manage.py runserver

7. Abre el navegador en http://127.0.0.1:8000

## Ejecutar pruebas
python manage.py test incidentes

## Autor
Gustavo - Universidad Mariano Gálvez de Guatemala (UMG)