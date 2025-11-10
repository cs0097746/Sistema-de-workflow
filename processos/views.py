from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.db.models import Q, Count
from django.utils import timezone
from django.http import HttpResponseForbidden
from .models import (
    TemplateProcesso, Etapa, Encaminhamento,
    ProcessoInstancia, EtapaExecutada, Documento, LogAuditoria
)
from processos.services import *
from .forms import (
    TemplateProcessoForm, EtapaForm, EncaminhamentoForm,
    ProcessoInstanciaForm, EtapaExecutadaForm, DocumentoForm,
    ProcessoFiltroForm, EncaminharProcessoForm
)


# ==================== DASHBOARD ====================

@login_required
def dashboard(request):
    """Dashboard principal do sistema"""
    usuario = request.user

    # Estatísticas
    processos_meus = ProcessoInstancia.objects.filter(usuario_atual=usuario)
    processos_criados = ProcessoInstancia.objects.filter(criado_por=usuario)
    processos_aguardando = processos_meus.filter(status='EM_ANDAMENTO').count()
    processos_concluidos = processos_criados.filter(status='CONCLUIDO').count()

    # Processos recentes
    processos_recentes = processos_meus.order_by('-data_atualizacao')[:5]

    # Templates disponíveis
    templates_disponiveis = TemplateProcesso.objects.filter(ativo=True)

    # Logs recentes
    logs_recentes = LogAuditoria.objects.filter(
        Q(processo__usuario_atual=usuario) | Q(processo__criado_por=usuario)
    ).distinct().order_by('-data_hora')[:10]

    context = {
        'processos_aguardando': processos_aguardando,
        'processos_concluidos': processos_concluidos,
        'processos_recentes': processos_recentes,
        'templates_disponiveis': templates_disponiveis,
        'logs_recentes': logs_recentes,
    }

    return render(request, 'processos/dashboard.html', context)


# ==================== TEMPLATES DE PROCESSO ====================

class TemplateProcessoListView(LoginRequiredMixin, ListView):
    """Lista todos os templates de processo"""
    model = TemplateProcesso
    template_name = 'processos/template_list.html'
    context_object_name = 'templates'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.perfil in ['ADMIN', 'GESTOR']:
            queryset = queryset.filter(ativo=True)
        return queryset.annotate(num_etapas=Count('etapas'))


class TemplateProcessoDetailView(LoginRequiredMixin, DetailView):
    """Detalhes de um template de processo"""
    model = TemplateProcesso
    template_name = 'processos/template_detail.html'
    context_object_name = 'template'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['etapas'] = self.object.etapas.all().order_by('ordem')
        return context


class TemplateProcessoCreateView(LoginRequiredMixin, CreateView):
    """Criar novo template de processo"""
    model = TemplateProcesso
    form_class = TemplateProcessoForm
    template_name = 'processos/template_form.html'
    success_url = reverse_lazy('template_list')

    def form_valid(self, form):
        form.instance.criado_por = self.request.user
        messages.success(self.request, 'Template criado com sucesso!')
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if not request.user.perfil in ['ADMIN', 'GESTOR']:
            messages.error(request, 'Você não tem permissão para criar templates.')
            return redirect('template_list')
        return super().dispatch(request, *args, **kwargs)


class TemplateProcessoUpdateView(LoginRequiredMixin, UpdateView):
    """Editar template de processo"""
    model = TemplateProcesso
    form_class = TemplateProcessoForm
    template_name = 'processos/template_form.html'
    success_url = reverse_lazy('template_list')

    def form_valid(self, form):
        messages.success(self.request, 'Template atualizado com sucesso!')
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if not request.user.perfil in ['ADMIN', 'GESTOR']:
            messages.error(request, 'Você não tem permissão para editar templates.')
            return redirect('template_list')
        return super().dispatch(request, *args, **kwargs)


# ==================== ETAPAS ====================

@login_required
def etapa_create(request, template_pk):
    """Criar nova etapa para um template"""
    template = get_object_or_404(TemplateProcesso, pk=template_pk)

    if not request.user.perfil in ['ADMIN', 'GESTOR']:
        messages.error(request, 'Você não tem permissão para criar etapas.')
        return redirect('template_detail', pk=template_pk)

    if request.method == 'POST':
        form = EtapaForm(request.POST, template=template)
        if form.is_valid():
            try:
                criar_etapa_via_sp(
                    template_id=template.id,
                    nome=form.cleaned_data['nome'],
                    ordem=form.cleaned_data['ordem'],
                    responsavel_id=form.cleaned_data['responsavel'].id,
                    prazo_dias=form.cleaned_data['prazo_dias'],
                    descricao=form.cleaned_data['descricao'],
                    usuario_id=request.user.id
                )
                messages.success(request, 'Etapa criada com sucesso (via procedure)!')
                return redirect('template_detail', pk=template_pk)
            except Exception as e:
                messages.error(request, f'Erro ao criar etapa: {str(e)}')
    else:
        # Sugere a próxima ordem
        ultima_ordem = template.etapas.count()
        form = EtapaForm(template=template, initial={'ordem': ultima_ordem + 1})

    return render(request, 'processos/etapa_form.html', {
        'form': form,
        'template': template,
        'action': 'Criar'
    })


@login_required
def etapa_update(request, pk):
    """Editar etapa via stored procedure"""
    etapa = get_object_or_404(Etapa, pk=pk)
    template = etapa.template

    if not request.user.perfil in ['ADMIN', 'GESTOR']:
        messages.error(request, 'Você não tem permissão para editar etapas.')
        return redirect('template_detail', pk=template.pk)

    if request.method == 'POST':
        form = EtapaForm(request.POST, instance=etapa, template=template)
        if form.is_valid():
            try:
                atualizar_etapa_via_sp(
                    etapa_id=etapa.id,
                    nome=form.cleaned_data['nome'],
                    ordem=form.cleaned_data['ordem'],
                    responsavel_id=form.cleaned_data['responsavel'].id,
                    prazo_dias=form.cleaned_data['prazo_dias'],
                    descricao=form.cleaned_data['descricao'],
                    usuario_id=request.user.id
                )
                messages.success(request, 'Etapa atualizada com sucesso (via procedure)!')
                return redirect('template_detail', pk=template.pk)
            except Exception as e:
                messages.error(request, f'Erro ao atualizar etapa: {str(e)}')
    else:
        form = EtapaForm(instance=etapa, template=template)

    return render(request, 'processos/etapa_form.html', {
        'form': form,
        'template': template,
        'action': 'Editar'
    })

# ==================== PROCESSOS ====================

class ProcessoListView(LoginRequiredMixin, ListView):
    """Lista processos com filtros"""
    model = ProcessoInstancia
    template_name = 'processos/processo_list.html'
    context_object_name = 'processos'
    paginate_by = 15

    def get_queryset(self):
        queryset = ProcessoInstancia.objects.all()

        # Filtra por usuário se não for admin/gestor
        if not self.request.user.perfil in ['ADMIN', 'GESTOR']:
            queryset = queryset.filter(
                Q(criado_por=self.request.user) |
                Q(usuario_atual=self.request.user) |
                Q(etapas_executadas__executado_por=self.request.user)
            ).distinct()

        # Aplica filtros do formulário
        form = ProcessoFiltroForm(self.request.GET)
        if form.is_valid():
            if form.cleaned_data.get('numero_processo'):
                queryset = queryset.filter(
                    numero_processo__icontains=form.cleaned_data['numero_processo']
                )
            if form.cleaned_data.get('template'):
                queryset = queryset.filter(template=form.cleaned_data['template'])
            if form.cleaned_data.get('status'):
                queryset = queryset.filter(status=form.cleaned_data['status'])
            if form.cleaned_data.get('criado_por'):
                queryset = queryset.filter(criado_por=form.cleaned_data['criado_por'])
            if form.cleaned_data.get('usuario_atual'):
                queryset = queryset.filter(usuario_atual=form.cleaned_data['usuario_atual'])
            if form.cleaned_data.get('data_inicio'):
                queryset = queryset.filter(data_criacao__gte=form.cleaned_data['data_inicio'])
            if form.cleaned_data.get('data_fim'):
                queryset = queryset.filter(data_criacao__lte=form.cleaned_data['data_fim'])

        return queryset.select_related('template', 'etapa_atual', 'usuario_atual', 'criado_por').order_by('-data_criacao')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filtro_form'] = ProcessoFiltroForm(self.request.GET)
        return context


class ProcessoDetailView(LoginRequiredMixin, DetailView):
    """Detalhes de um processo com validação no banco"""
    model = ProcessoInstancia
    template_name = 'processos/processo_detail.html'
    context_object_name = 'processo'

    def get_object(self):
        obj = super().get_object()
        usuario_id = getattr(self.request.user, "pk", None)

        if not usuario_id or not pode_ver_processo(obj.id, usuario_id):
            messages.error(self.request, 'Você não tem permissão para visualizar este processo.')
            return redirect('processo_list')

        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['etapas_executadas'] = self.object.etapas_executadas.all().order_by('-data_inicio')
        context['logs'] = self.object.logs.all().order_by('-data_hora')[:20]
        context['pode_executar'] = self.object.pode_ser_executado_por(self.request.user)
        return context


@login_required
def processo_create(request):
    """Criar novo processo"""
    if request.method == 'POST':
        form = ProcessoInstanciaForm(request.POST)
        if form.is_valid():
            processo = form.save(commit=False)
            processo.criado_por = request.user
            processo.save()

            # Inicia o processo
            try:
                processo.iniciar(request.user)
                messages.success(request, f'Processo {processo.numero_processo} iniciado com sucesso!')
                return redirect('processo_detail', pk=processo.pk)
            except Exception as e:
                messages.error(request, f'Erro ao iniciar processo: {str(e)}')
                processo.delete()
    else:
        form = ProcessoInstanciaForm()

    return render(request, 'processos/processo_form.html', {'form': form})


@login_required
def processo_executar_etapa(request, pk):
    """Executar etapa do processo"""
    processo = get_object_or_404(ProcessoInstancia, pk=pk)

    # Verifica permissão
    if not processo.pode_ser_executado_por(request.user):
        messages.error(request, 'Você não tem permissão para executar esta etapa.')
        return redirect('processo_detail', pk=pk)

    if request.method == 'POST':
        form = EtapaExecutadaForm(request.POST)
        if form.is_valid():
            etapa_exec = form.save(commit=False)
            etapa_exec.processo = processo
            etapa_exec.etapa = processo.etapa_atual
            etapa_exec.executado_por = request.user
            etapa_exec.save()

            # Conclui a etapa
            etapa_exec.concluir(
                resultado=form.cleaned_data['resultado'],
                observacoes=form.cleaned_data['observacoes']
            )

            messages.success(request, 'Etapa executada com sucesso!')

            # Verifica se há próxima etapa
            proxima_etapa = processo.etapa_atual.get_proxima_etapa()
            if proxima_etapa:
                # Avança automaticamente para próxima etapa
                processo.etapa_atual = proxima_etapa
                # Mantém o usuário atual (ou pode ser alterado conforme regra de negócio)
                processo.usuario_atual = request.user
                processo.save()

                # Cria log de encaminhamento automático
                LogAuditoria.objects.create(
                    processo=processo,
                    usuario=request.user,
                    acao='ENCAMINHAMENTO',
                    descricao=f'Processo avançou automaticamente para: {proxima_etapa.nome}'
                )

                messages.info(request, f'Processo avançou para: {proxima_etapa.nome}')
                return redirect('processo_detail', pk=pk)
            else:
                # Última etapa - conclui o processo
                processo.concluir()
                messages.success(request, 'Processo concluído com sucesso!')
                return redirect('processo_detail', pk=pk)
    else:
        form = EtapaExecutadaForm()

    return render(request, 'processos/etapa_executar.html', {
        'form': form,
        'processo': processo,
        'etapa': processo.etapa_atual
    })


@login_required
def processo_encaminhar(request, pk):
    """Encaminhar processo para próxima etapa via stored procedure"""
    processo = get_object_or_404(ProcessoInstancia, pk=pk)

    # Verifica permissão
    if not processo.pode_ser_executado_por(request.user):
        messages.error(request, 'Você não tem permissão para encaminhar este processo.')
        return redirect('processo_detail', pk=pk)

    if request.method == 'POST':
        form = EncaminharProcessoForm(request.POST, etapa_atual=processo.etapa_atual)
        if form.is_valid():
            proxima_etapa = form.cleaned_data['proxima_etapa']
            usuario_destino = form.cleaned_data['usuario_destino']
            observacoes = form.cleaned_data['observacoes'] or 'Encaminhado'

            try:
                with transaction.atomic():
                    encaminhar_processo(
                        processo_id=processo.id,
                        proxima_etapa_id=proxima_etapa.id,
                        usuario_id=request.user.id,
                        observacao=observacoes
                    )

                messages.success(
                    request,
                    f'Processo {processo.numero_processo} encaminhado para {usuario_destino.get_full_name()}!'
                )
                return redirect('processo_detail', pk=pk)

            except Exception as e:
                messages.error(request, f'Erro ao encaminhar processo: {str(e)}')
    else:
        form = EncaminharProcessoForm(etapa_atual=processo.etapa_atual)

    return render(request, 'processos/processo_encaminhar.html', {
        'form': form,
        'processo': processo
    })

@login_required
def documento_upload(request, etapa_executada_pk):
    """Upload de documento em etapa executada"""
    etapa_executada = get_object_or_404(EtapaExecutada, pk=etapa_executada_pk)
    processo = etapa_executada.processo

    # Verifica permissão
    if etapa_executada.executado_por != request.user and not request.user.perfil in ['ADMIN', 'GESTOR']:
        messages.error(request, 'Você não tem permissão para anexar documentos nesta etapa.')
        return redirect('processo_detail', pk=processo.pk)

    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES)
        if form.is_valid():
            documento = form.save(commit=False)
            documento.etapa_executada = etapa_executada
            documento.enviado_por = request.user
            documento.save()

            # Cria log
            LogAuditoria.objects.create(
                processo=processo,
                etapa_executada=etapa_executada,
                usuario=request.user,
                acao='ANEXO_DOCUMENTO',
                descricao=f'Documento "{documento.nome}" anexado à etapa {etapa_executada.etapa.nome}'
            )

            messages.success(request, 'Documento enviado com sucesso!')
            return redirect('processo_detail', pk=processo.pk)
    else:
        form = DocumentoForm()

    return render(request, 'processos/documento_form.html', {
        'form': form,
        'etapa_executada': etapa_executada,
        'processo': processo
    })


@login_required
def meus_processos(request):
    """Lista processos do usuário atual"""
    processos = ProcessoInstancia.objects.filter(
        usuario_atual=request.user,
        status='EM_ANDAMENTO'
    ).select_related('template', 'etapa_atual').order_by('-data_atualizacao')

    return render(request, 'processos/meus_processos.html', {
        'processos': processos
    })
