from django import forms
from .models import Incidente, Categoria
from django.contrib.auth.models import User

class IncidenteForm(forms.ModelForm):
    class Meta:
        model = Incidente
        fields = ['titulo', 'descripcion', 'categoria', 'impacto', 'urgencia']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título del incidente'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe el problema detalladamente'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'impacto': forms.Select(attrs={'class': 'form-select'}),
            'urgencia': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'titulo': 'Título',
            'descripcion': 'Descripción',
            'categoria': 'Categoría',
            'impacto': 'Impacto (1=Bajo, 5=Crítico)',
            'urgencia': 'Urgencia (1=Baja, 5=Crítica)',
        }

class AsignarTecnicoForm(forms.ModelForm):
    class Meta:
        model = Incidente
        fields = ['asignado_a', 'estado']
        widgets = {
            'asignado_a': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'asignado_a': 'Asignar Técnico',
            'estado': 'Estado',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['asignado_a'].queryset = User.objects.filter(perfil__rol='tecnico')