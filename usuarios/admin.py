from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Usuario
from typing import Any


@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    """Admin para modelo de usuário customizado"""
    list_display = ['username', 'email', 'first_name', 'last_name', 'perfil', 'departamento', 'ativo', 'is_staff']
    list_filter = ['perfil', 'ativo', 'is_staff', 'is_superuser', 'departamento']
    search_fields = ['username', 'first_name', 'last_name', 'email', 'cpf']
    ordering = ['username']
    
    fieldsets: Any = BaseUserAdmin.fieldsets + (  # type: ignore[assignment]
        ('Informações Adicionais', {
            'fields': ('cpf', 'telefone', 'departamento', 'perfil', 'ativo')
        }),
    )
    
    add_fieldsets: Any = BaseUserAdmin.add_fieldsets + (  # type: ignore[assignment]
        ('Informações Adicionais', {
            'fields': ('email', 'first_name', 'last_name', 'cpf', 'telefone', 'departamento', 'perfil')
        }),
    )
