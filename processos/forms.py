from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import (
    TemplateProcesso, Etapa, Encaminhamento, 
    ProcessoInstancia, EtapaExecutada, Documento
)
from usuarios.models import Usuario
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Div, Field


class TemplateProcessoForm(forms.ModelForm):
    """Form para criação/edição de templates de processo"""
    
    class Meta:
        model = TemplateProcesso
        fields = ['nome', 'descricao', 'ativo']
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Salvar Template', css_class='btn btn-primary'))


class EtapaForm(forms.ModelForm):
    """Form para criação/edição de etapas"""
    
    class Meta:
        model = Etapa
        fields = [
            'nome', 'descricao', 'tipo', 'ordem', 'prazo_dias',
            'permite_anexos', 'requer_aprovacao', 'usuarios_permitidos'
        ]
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 3}),
            'usuarios_permitidos': forms.CheckboxSelectMultiple(),
        }
    
    def __init__(self, *args, **kwargs):
        template = kwargs.pop('template', None)
        super().__init__(*args, **kwargs)
        
        if template:
            self.instance.template = template
            
            # Sugere automaticamente a próxima ordem
            if not self.instance.pk:  # Apenas para novas etapas
                ultima_etapa = Etapa.objects.filter(template=template).order_by('-ordem').first()
                proxima_ordem = (ultima_etapa.ordem + 1) if ultima_etapa else 1
                self.fields['ordem'].initial = proxima_ordem
                self.fields['ordem'].help_text = f'Deixe como {proxima_ordem} para adicionar ao final, ou escolha outra ordem'
        
        # Torna o campo ordem opcional (será auto-preenchido se vazio)
        self.fields['ordem'].required = False
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('nome', css_class='col-md-8'),
                Column('ordem', css_class='col-md-4'),
            ),
            'descricao',
            Row(
                Column('tipo', css_class='col-md-4'),
                Column('prazo_dias', css_class='col-md-4'),
                Column(
                    Div(
                        Field('permite_anexos', css_class='form-check-input'),
                        css_class='form-check'
                    ),
                    css_class='col-md-2'
                ),
                Column(
                    Div(
                        Field('requer_aprovacao', css_class='form-check-input'),
                        css_class='form-check'
                    ),
                    css_class='col-md-2'
                ),
            ),
            'usuarios_permitidos',
        )
        self.helper.add_input(Submit('submit', 'Salvar Etapa', css_class='btn btn-primary'))


class EncaminhamentoForm(forms.ModelForm):
    """Form para criação de encaminhamentos"""
    
    class Meta:
        model = Encaminhamento
        fields = ['etapa_origem', 'etapa_destino', 'condicao', 'ativo']
    
    def __init__(self, *args, **kwargs):
        template = kwargs.pop('template', None)
        super().__init__(*args, **kwargs)
        
        if template:
            self.fields['etapa_origem'].queryset = Etapa.objects.filter(template=template)
            self.fields['etapa_destino'].queryset = Etapa.objects.filter(template=template)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Salvar Encaminhamento', css_class='btn btn-primary'))


class ProcessoInstanciaForm(forms.ModelForm):
    """Form para criação de nova instância de processo"""
    
    class Meta:
        model = ProcessoInstancia
        fields = ['template', 'titulo', 'descricao']
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['template'].queryset = TemplateProcesso.objects.filter(ativo=True)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'template',
            'titulo',
            'descricao',
        )
        self.helper.add_input(Submit('submit', 'Iniciar Processo', css_class='btn btn-success'))


class EtapaExecutadaForm(forms.ModelForm):
    """Form para execução de etapa"""
    
    class Meta:
        model = EtapaExecutada
        fields = ['observacoes', 'resultado']
        widgets = {
            'observacoes': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Observações sobre a execução...'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Concluir Etapa', css_class='btn btn-success'))


class DocumentoForm(forms.ModelForm):
    """Form para upload de documentos"""
    
    class Meta:
        model = Documento
        fields = ['nome', 'tipo', 'arquivo', 'descricao']
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.add_input(Submit('submit', 'Enviar Documento', css_class='btn btn-primary'))


class ProcessoFiltroForm(forms.Form):
    """Form para filtrar processos"""
    
    STATUS_CHOICES = [('', 'Todos')] + list(ProcessoInstancia.STATUS_CHOICES)
    
    numero_processo = forms.CharField(
        label='Número do Processo',
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Ex: 000001/2025'})
    )
    template = forms.ModelChoiceField(
        label='Template',
        queryset=TemplateProcesso.objects.all(),
        required=False,
        empty_label='Todos'
    )
    status = forms.ChoiceField(
        label='Status',
        choices=STATUS_CHOICES,
        required=False
    )
    criado_por = forms.ModelChoiceField(
        label='Criado por',
        queryset=Usuario.objects.filter(is_active=True),
        required=False,
        empty_label='Todos'
    )
    usuario_atual = forms.ModelChoiceField(
        label='Usuário Atual',
        queryset=Usuario.objects.filter(is_active=True),
        required=False,
        empty_label='Todos'
    )
    data_inicio = forms.DateField(
        label='Data Início',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    data_fim = forms.DateField(
        label='Data Fim',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.layout = Layout(
            Row(
                Column('numero_processo', css_class='col-md-4'),
                Column('template', css_class='col-md-4'),
                Column('status', css_class='col-md-4'),
            ),
            Row(
                Column('criado_por', css_class='col-md-4'),
                Column('usuario_atual', css_class='col-md-4'),
            ),
            Row(
                Column('data_inicio', css_class='col-md-6'),
                Column('data_fim', css_class='col-md-6'),
            ),
        )
        self.helper.add_input(Submit('submit', 'Filtrar', css_class='btn btn-primary'))
        self.helper.add_input(Submit('limpar', 'Limpar Filtros', css_class='btn btn-secondary'))


class EncaminharProcessoForm(forms.Form):
    """Form para encaminhar processo para próxima etapa"""
    
    proxima_etapa = forms.ModelChoiceField(
        label='Encaminhar para',
        queryset=Etapa.objects.none(),
        required=True
    )
    usuario_destino = forms.ModelChoiceField(
        label='Usuário Responsável',
        queryset=Usuario.objects.filter(is_active=True),
        required=True
    )
    observacoes = forms.CharField(
        label='Observações',
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False
    )
    
    def __init__(self, *args, **kwargs):
        etapa_atual = kwargs.pop('etapa_atual', None)
        super().__init__(*args, **kwargs)
        
        if etapa_atual:
            # Busca encaminhamentos possíveis
            encaminhamentos = etapa_atual.get_encaminhamentos_possiveis()
            etapas_destino = [enc.etapa_destino.id for enc in encaminhamentos]
            
            if etapas_destino:
                self.fields['proxima_etapa'].queryset = Etapa.objects.filter(id__in=etapas_destino)
            else:
                # Se não há encaminhamentos definidos, permite ir para próxima etapa sequencial
                proxima = etapa_atual.get_proxima_etapa()
                if proxima:
                    self.fields['proxima_etapa'].queryset = Etapa.objects.filter(id=proxima.id)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Encaminhar', css_class='btn btn-success'))
