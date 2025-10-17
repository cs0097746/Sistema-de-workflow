from django.contrib import admin
from .models import (
    TemplateProcesso, Etapa, Encaminhamento,
    ProcessoInstancia, EtapaExecutada, Documento, LogAuditoria
)


class EtapaInline(admin.TabularInline):
    """Inline para etapas no template"""
    model = Etapa
    extra = 1
    fields = ['ordem', 'nome', 'tipo', 'prazo_dias']
    ordering = ['ordem']


@admin.register(TemplateProcesso)
class TemplateProcessoAdmin(admin.ModelAdmin):
    """Admin para templates de processo"""
    list_display = ['nome', 'ativo', 'criado_por', 'data_criacao', 'numero_etapas']
    list_filter = ['ativo', 'data_criacao']
    search_fields = ['nome', 'descricao']
    readonly_fields = ['data_criacao', 'data_atualizacao']
    inlines = [EtapaInline]
    
    def numero_etapas(self, obj):
        return obj.etapas.count()
    numero_etapas.short_description = 'Nº Etapas'
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.criado_por = request.user
        super().save_model(request, obj, form, change)


@admin.register(Etapa)
class EtapaAdmin(admin.ModelAdmin):
    """Admin para etapas"""
    list_display = ['nome', 'template', 'ordem', 'tipo', 'prazo_dias', 'requer_aprovacao']
    list_filter = ['tipo', 'requer_aprovacao', 'template']
    search_fields = ['nome', 'descricao', 'template__nome']
    filter_horizontal = ['usuarios_permitidos']
    ordering = ['template', 'ordem']


@admin.register(Encaminhamento)
class EncaminhamentoAdmin(admin.ModelAdmin):
    """Admin para encaminhamentos"""
    list_display = ['etapa_origem', 'etapa_destino', 'condicao', 'ativo']
    list_filter = ['ativo', 'etapa_origem__template']
    search_fields = ['etapa_origem__nome', 'etapa_destino__nome', 'condicao']


class EtapaExecutadaInline(admin.TabularInline):
    """Inline para etapas executadas"""
    model = EtapaExecutada
    extra = 0
    readonly_fields = ['etapa', 'executado_por', 'resultado', 'data_inicio', 'data_conclusao']
    can_delete = False


@admin.register(ProcessoInstancia)
class ProcessoInstanciaAdmin(admin.ModelAdmin):
    """Admin para processos"""
    list_display = ['numero_processo', 'titulo', 'template', 'status', 'etapa_atual', 'usuario_atual', 'data_criacao']
    list_filter = ['status', 'template', 'data_criacao']
    search_fields = ['numero_processo', 'titulo', 'descricao']
    readonly_fields = ['numero_processo', 'data_criacao', 'data_conclusao', 'data_atualizacao']
    inlines = [EtapaExecutadaInline]
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('numero_processo', 'template', 'titulo', 'descricao')
        }),
        ('Status e Fluxo', {
            'fields': ('status', 'etapa_atual', 'usuario_atual')
        }),
        ('Auditoria', {
            'fields': ('criado_por', 'data_criacao', 'data_conclusao', 'data_atualizacao')
        }),
    )


@admin.register(EtapaExecutada)
class EtapaExecutadaAdmin(admin.ModelAdmin):
    """Admin para etapas executadas"""
    list_display = ['processo', 'etapa', 'executado_por', 'resultado', 'data_inicio', 'data_conclusao']
    list_filter = ['resultado', 'etapa__template', 'data_inicio']
    search_fields = ['processo__numero_processo', 'etapa__nome', 'executado_por__username']
    readonly_fields = ['data_inicio', 'tempo_execucao']


@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    """Admin para documentos"""
    list_display = ['nome', 'tipo', 'etapa_executada', 'enviado_por', 'data_envio', 'tamanho_formatado']
    list_filter = ['tipo', 'data_envio']
    search_fields = ['nome', 'descricao', 'etapa_executada__processo__numero_processo']
    readonly_fields = ['data_envio', 'tamanho']
    
    def tamanho_formatado(self, obj):
        return obj.get_tamanho_formatado()
    tamanho_formatado.short_description = 'Tamanho'


@admin.register(LogAuditoria)
class LogAuditoriaAdmin(admin.ModelAdmin):
    """Admin para logs de auditoria"""
    list_display = ['processo', 'acao', 'usuario', 'data_hora']
    list_filter = ['acao', 'data_hora']
    search_fields = ['processo__numero_processo', 'usuario__username', 'descricao']
    readonly_fields = ['processo', 'etapa_executada', 'usuario', 'acao', 'descricao', 'data_hora', 'ip_address']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
