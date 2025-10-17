from django.db import models
from django.contrib.auth.models import AbstractUser
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from processos.models import Etapa, ProcessoInstancia


class Usuario(AbstractUser):
    """
    Modelo de usuário customizado com informações adicionais
    """
    PERFIL_CHOICES = [
        ('ADMIN', 'Administrador'),
        ('GESTOR', 'Gestor'),
        ('OPERADOR', 'Operador'),
        ('VISUALIZADOR', 'Visualizador'),
    ]
    
    cpf = models.CharField('CPF', max_length=14, unique=True, null=True, blank=True)
    telefone = models.CharField('Telefone', max_length=20, blank=True)
    departamento = models.CharField('Departamento', max_length=100, blank=True)
    perfil = models.CharField('Perfil', max_length=20, choices=PERFIL_CHOICES, default='OPERADOR')
    ativo = models.BooleanField('Ativo', default=True)
    data_criacao = models.DateTimeField('Data de Criação', auto_now_add=True)
    data_atualizacao = models.DateTimeField('Última Atualização', auto_now=True)
    
    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        ordering = ['username']
    
    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_perfil_display()})"  # type: ignore[attr-defined]
    
    def pode_executar_etapa(self, etapa: 'Etapa') -> bool:
        """
        Verifica se o usuário tem permissão para executar uma etapa específica
        """
        # Administradores podem executar qualquer etapa
        if self.perfil == 'ADMIN':
            return True
        
        # Verifica se o usuário está na lista de usuários permitidos da etapa
        return self in etapa.usuarios_permitidos.all()
    
    def pode_visualizar_processo(self, processo: 'ProcessoInstancia') -> bool:
        """
        Verifica se o usuário pode visualizar um processo
        """
        # Administradores e gestores podem visualizar qualquer processo
        if self.perfil in ['ADMIN', 'GESTOR']:
            return True
        
        # Usuário criador pode visualizar
        if processo.criado_por == self:
            return True
        
        # Usuário atual responsável pode visualizar
        if processo.usuario_atual == self:
            return True
        
        # Usuários que já executaram etapas podem visualizar
        if processo.etapas_executadas.filter(executado_por=self).exists():  # type: ignore[attr-defined]
            return True
        
        return False
