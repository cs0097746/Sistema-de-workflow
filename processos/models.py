from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone


class TemplateProcesso(models.Model):
    """
    Template de processo que define o fluxo de trabalho
    """
    nome = models.CharField('Nome', max_length=200)
    descricao = models.TextField('Descrição')
    ativo = models.BooleanField('Ativo', default=True)
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='templates_criados',
        verbose_name='Criado por'
    )
    data_criacao = models.DateTimeField('Data de Criação', auto_now_add=True)
    data_atualizacao = models.DateTimeField('Última Atualização', auto_now=True)
    
    class Meta:
        verbose_name = 'Template de Processo'
        verbose_name_plural = 'Templates de Processos'
        ordering = ['nome']
    
    def __str__(self):
        return self.nome
    
    def get_primeira_etapa(self):
        """Retorna a primeira etapa do template"""
        return self.etapas.filter(ordem=1).first()
    
    def validar_fluxo(self):
        """Valida se o fluxo do template está correto"""
        etapas = self.etapas.all().order_by('ordem')
        
        if not etapas.exists():
            raise ValidationError("O template deve ter pelo menos uma etapa.")
        
        # Verifica se as ordens são sequenciais
        ordens = list(etapas.values_list('ordem', flat=True))
        if ordens != list(range(1, len(ordens) + 1)):
            raise ValidationError("As etapas devem estar em ordem sequencial começando de 1.")
        
        return True


class Etapa(models.Model):
    """
    Etapa de um template de processo
    """
    TIPO_CHOICES = [
        ('ANALISE', 'Análise'),
        ('APROVACAO', 'Aprovação'),
        ('EXECUCAO', 'Execução'),
        ('REVISAO', 'Revisão'),
        ('FINALIZACAO', 'Finalização'),
    ]
    
    template = models.ForeignKey(
        TemplateProcesso,
        on_delete=models.CASCADE,
        related_name='etapas',
        verbose_name='Template'
    )
    nome = models.CharField('Nome', max_length=200)
    descricao = models.TextField('Descrição', blank=True)
    tipo = models.CharField('Tipo', max_length=20, choices=TIPO_CHOICES, default='EXECUCAO')
    ordem = models.PositiveIntegerField('Ordem')
    prazo_dias = models.PositiveIntegerField('Prazo (dias)', default=5)
    permite_anexos = models.BooleanField('Permite Anexos', default=True)
    requer_aprovacao = models.BooleanField('Requer Aprovação', default=False)
    usuarios_permitidos = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='etapas_permitidas',
        verbose_name='Usuários Permitidos',
        blank=True
    )
    
    class Meta:
        verbose_name = 'Etapa'
        verbose_name_plural = 'Etapas'
        ordering = ['template', 'ordem']
        unique_together = ['template', 'ordem']
    
    def __str__(self):
        return f"{self.template.nome} - Etapa {self.ordem}: {self.nome}"
    
    def save(self, *args, **kwargs):
        from django.db import transaction
        
        if not self.ordem or self.ordem == 0:
            # Calcula automaticamente a próxima ordem disponível
            with transaction.atomic():
                # Lock nas etapas do mesmo template
                ultima = Etapa.objects.select_for_update().filter(
                    template=self.template
                ).order_by('-ordem').first()
                
                if ultima:
                    self.ordem = ultima.ordem + 1
                else:
                    self.ordem = 1
        
        super().save(*args, **kwargs)
    
    def get_proxima_etapa(self):
        """Retorna a próxima etapa no fluxo"""
        return Etapa.objects.filter(
            template=self.template,
            ordem=self.ordem + 1
        ).first()
    
    def get_encaminhamentos_possiveis(self):
        """Retorna os encaminhamentos possíveis desta etapa"""
        return self.encaminhamentos_origem.filter(ativo=True)


class Encaminhamento(models.Model):
    """
    Define os possíveis encaminhamentos entre etapas
    """
    etapa_origem = models.ForeignKey(
        Etapa,
        on_delete=models.CASCADE,
        related_name='encaminhamentos_origem',
        verbose_name='Etapa de Origem'
    )
    etapa_destino = models.ForeignKey(
        Etapa,
        on_delete=models.CASCADE,
        related_name='encaminhamentos_destino',
        verbose_name='Etapa de Destino'
    )
    condicao = models.CharField(
        'Condição',
        max_length=200,
        blank=True,
        help_text='Ex: Aprovado, Rejeitado, Precisa Revisão'
    )
    ativo = models.BooleanField('Ativo', default=True)
    
    class Meta:
        verbose_name = 'Encaminhamento'
        verbose_name_plural = 'Encaminhamentos'
        unique_together = ['etapa_origem', 'etapa_destino', 'condicao']
    
    def __str__(self):
        condicao_str = f" ({self.condicao})" if self.condicao else ""
        return f"{self.etapa_origem.nome} → {self.etapa_destino.nome}{condicao_str}"
    
    def clean(self):
        """Valida o encaminhamento"""
        if self.etapa_origem.template != self.etapa_destino.template:
            raise ValidationError("As etapas devem pertencer ao mesmo template.")


class ProcessoInstancia(models.Model):
    """
    Instância de um processo em execução
    """
    STATUS_CHOICES = [
        ('INICIADO', 'Iniciado'),
        ('EM_ANDAMENTO', 'Em Andamento'),
        ('AGUARDANDO', 'Aguardando'),
        ('CONCLUIDO', 'Concluído'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    template = models.ForeignKey(
        TemplateProcesso,
        on_delete=models.PROTECT,
        related_name='instancias',
        verbose_name='Template'
    )
    numero_processo = models.CharField(
        'Número do Processo',
        max_length=50,
        unique=True,
        help_text='Gerado automaticamente'
    )
    titulo = models.CharField('Título', max_length=200)
    descricao = models.TextField('Descrição', blank=True)
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='INICIADO')
    etapa_atual = models.ForeignKey(
        Etapa,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processos_nesta_etapa',
        verbose_name='Etapa Atual'
    )
    usuario_atual = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processos_atuais',
        verbose_name='Usuário Atual'
    )
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='processos_criados',
        verbose_name='Criado por'
    )
    data_criacao = models.DateTimeField('Data de Criação', auto_now_add=True)
    data_conclusao = models.DateTimeField('Data de Conclusão', null=True, blank=True)
    data_atualizacao = models.DateTimeField('Última Atualização', auto_now=True)
    
    class Meta:
        verbose_name = 'Processo'
        verbose_name_plural = 'Processos'
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"{self.numero_processo} - {self.titulo}"
    
    def save(self, *args, **kwargs):
        from django.db import transaction
        
        if not self.numero_processo:
            # Gera número do processo dentro de uma transação atômica
            with transaction.atomic():
                ano = timezone.now().year
                
                # Lock em toda a tabela para garantir unicidade
                ultimo = ProcessoInstancia.objects.select_for_update().filter(
                    numero_processo__startswith=f"{ano}/"
                ).order_by('-numero_processo').first()
                
                if ultimo:
                    try:
                        # Extrai o número sequencial
                        ultimo_num = int(ultimo.numero_processo.split('/')[0])
                        proximo_num = ultimo_num + 1
                    except (ValueError, IndexError):
                        # Se falhar, conta quantos existem e adiciona 1
                        count = ProcessoInstancia.objects.filter(
                            numero_processo__startswith=f"{ano}/"
                        ).count()
                        proximo_num = count + 1
                else:
                    proximo_num = 1
                
                # Tenta até 10 vezes se houver conflito
                max_tentativas = 10
                for tentativa in range(max_tentativas):
                    numero_tentativa = f"{proximo_num:06d}/{ano}"
                    
                    # Verifica se já existe
                    if not ProcessoInstancia.objects.filter(
                        numero_processo=numero_tentativa
                    ).exists():
                        self.numero_processo = numero_tentativa
                        break
                    
                    proximo_num += 1
                else:
                    # Se após 10 tentativas ainda falhar, usa timestamp
                    import time
                    timestamp = int(time.time() * 1000) % 1000000
                    self.numero_processo = f"{timestamp:06d}/{ano}"
        
        super().save(*args, **kwargs)
    
    def iniciar(self, usuario):
        """Inicia o processo na primeira etapa"""
        primeira_etapa = self.template.get_primeira_etapa()
        if not primeira_etapa:
            raise ValidationError("Template sem etapas definidas.")
        
        self.etapa_atual = primeira_etapa
        self.usuario_atual = usuario
        self.status = 'EM_ANDAMENTO'
        self.save()
        
        # Cria log de início
        LogAuditoria.objects.create(
            processo=self,
            usuario=usuario,
            acao='INICIO',
            descricao=f'Processo iniciado na etapa: {primeira_etapa.nome}'
        )
    
    def pode_ser_executado_por(self, usuario):
        """Verifica se o usuário pode executar a etapa atual"""
        if not self.etapa_atual:
            return False
        return usuario.pode_executar_etapa(self.etapa_atual)
    
    def concluir(self):
        """Conclui o processo"""
        self.status = 'CONCLUIDO'
        self.data_conclusao = timezone.now()
        self.etapa_atual = None
        self.usuario_atual = None
        self.save()


class EtapaExecutada(models.Model):
    """
    Registro de execução de uma etapa
    """
    RESULTADO_CHOICES = [
        ('APROVADO', 'Aprovado'),
        ('REJEITADO', 'Rejeitado'),
        ('PENDENTE', 'Pendente'),
        ('CONCLUIDO', 'Concluído'),
    ]
    
    processo = models.ForeignKey(
        ProcessoInstancia,
        on_delete=models.CASCADE,
        related_name='etapas_executadas',
        verbose_name='Processo'
    )
    etapa = models.ForeignKey(
        Etapa,
        on_delete=models.PROTECT,
        related_name='execucoes',
        verbose_name='Etapa'
    )
    executado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='etapas_executadas',
        verbose_name='Executado por'
    )
    observacoes = models.TextField('Observações', blank=True)
    resultado = models.CharField('Resultado', max_length=20, choices=RESULTADO_CHOICES, default='CONCLUIDO')
    data_inicio = models.DateTimeField('Data de Início', auto_now_add=True)
    data_conclusao = models.DateTimeField('Data de Conclusão', null=True, blank=True)
    tempo_execucao = models.DurationField('Tempo de Execução', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Etapa Executada'
        verbose_name_plural = 'Etapas Executadas'
        ordering = ['-data_inicio']
    
    def __str__(self):
        return f"{self.processo.numero_processo} - {self.etapa.nome}"
    
    def concluir(self, resultado='CONCLUIDO', observacoes=''):
        """Conclui a execução da etapa"""
        self.resultado = resultado
        self.observacoes = observacoes
        self.data_conclusao = timezone.now()
        self.tempo_execucao = self.data_conclusao - self.data_inicio
        self.save()
        
        # Cria log
        LogAuditoria.objects.create(
            processo=self.processo,
            etapa_executada=self,
            usuario=self.executado_por,
            acao='EXECUCAO_ETAPA',
            descricao=f'Etapa "{self.etapa.nome}" concluída com resultado: {self.get_resultado_display()}'
        )


class Documento(models.Model):
    """
    Documento anexado a uma etapa executada
    """
    TIPO_CHOICES = [
        ('DOCUMENTO', 'Documento'),
        ('IMAGEM', 'Imagem'),
        ('PLANILHA', 'Planilha'),
        ('PDF', 'PDF'),
        ('OUTRO', 'Outro'),
    ]
    
    etapa_executada = models.ForeignKey(
        EtapaExecutada,
        on_delete=models.CASCADE,
        related_name='documentos',
        verbose_name='Etapa Executada'
    )
    nome = models.CharField('Nome', max_length=200)
    tipo = models.CharField('Tipo', max_length=20, choices=TIPO_CHOICES, default='DOCUMENTO')
    arquivo = models.FileField('Arquivo', upload_to='documentos/%Y/%m/')
    descricao = models.TextField('Descrição', blank=True)
    enviado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='documentos_enviados',
        verbose_name='Enviado por'
    )
    data_envio = models.DateTimeField('Data de Envio', auto_now_add=True)
    tamanho = models.BigIntegerField('Tamanho (bytes)', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'
        ordering = ['-data_envio']
    
    def __str__(self):
        return f"{self.nome} - {self.etapa_executada.processo.numero_processo}"
    
    def save(self, *args, **kwargs):
        if self.arquivo:
            self.tamanho = self.arquivo.size
        super().save(*args, **kwargs)
    
    def get_tamanho_formatado(self):
        """Retorna o tamanho do arquivo formatado"""
        if not self.tamanho:
            return "0 bytes"
        
        for unit in ['bytes', 'KB', 'MB', 'GB']:
            if self.tamanho < 1024.0:
                return f"{self.tamanho:.1f} {unit}"
            self.tamanho /= 1024.0
        return f"{self.tamanho:.1f} TB"


class LogAuditoria(models.Model):
    """
    Log de auditoria para rastreamento de ações
    """
    ACAO_CHOICES = [
        ('INICIO', 'Início de Processo'),
        ('EXECUCAO_ETAPA', 'Execução de Etapa'),
        ('ENCAMINHAMENTO', 'Encaminhamento'),
        ('ANEXO_DOCUMENTO', 'Anexo de Documento'),
        ('APROVACAO', 'Aprovação'),
        ('REJEICAO', 'Rejeição'),
        ('CANCELAMENTO', 'Cancelamento'),
        ('CONCLUSAO', 'Conclusão'),
    ]
    
    processo = models.ForeignKey(
        ProcessoInstancia,
        on_delete=models.CASCADE,
        related_name='logs',
        verbose_name='Processo'
    )
    etapa_executada = models.ForeignKey(
        EtapaExecutada,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='logs',
        verbose_name='Etapa Executada'
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='logs_auditoria',
        verbose_name='Usuário'
    )
    acao = models.CharField('Ação', max_length=30, choices=ACAO_CHOICES)
    descricao = models.TextField('Descrição')
    data_hora = models.DateTimeField('Data/Hora', auto_now_add=True)
    ip_address = models.GenericIPAddressField('IP Address', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Log de Auditoria'
        verbose_name_plural = 'Logs de Auditoria'
        ordering = ['-data_hora']
    
    def __str__(self):
        return f"{self.processo.numero_processo} - {self.get_acao_display()} - {self.data_hora}"
