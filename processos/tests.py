from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import (
    TemplateProcesso, Etapa, Encaminhamento,
    ProcessoInstancia, EtapaExecutada, LogAuditoria
)

User = get_user_model()


class TemplateProcessoTestCase(TestCase):
    """Testes para o model TemplateProcesso"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            perfil='ADMIN'
        )
        self.template = TemplateProcesso.objects.create(
            nome='Template Teste',
            descricao='Descrição de teste',
            criado_por=self.user
        )
    
    def test_template_creation(self):
        """Testa criação de template"""
        self.assertEqual(self.template.nome, 'Template Teste')
        self.assertTrue(self.template.ativo)
    
    def test_template_str(self):
        """Testa representação string do template"""
        self.assertEqual(str(self.template), 'Template Teste')


class EtapaTestCase(TestCase):
    """Testes para o model Etapa"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.template = TemplateProcesso.objects.create(
            nome='Template Teste',
            criado_por=self.user
        )
        self.etapa1 = Etapa.objects.create(
            template=self.template,
            nome='Etapa 1',
            ordem=1,
            prazo_dias=5
        )
        self.etapa2 = Etapa.objects.create(
            template=self.template,
            nome='Etapa 2',
            ordem=2,
            prazo_dias=3
        )
    
    def test_etapa_creation(self):
        """Testa criação de etapa"""
        self.assertEqual(self.etapa1.ordem, 1)
        self.assertEqual(self.etapa1.prazo_dias, 5)
    
    def test_get_proxima_etapa(self):
        """Testa busca de próxima etapa"""
        proxima = self.etapa1.get_proxima_etapa()
        self.assertEqual(proxima, self.etapa2)


class ProcessoInstanciaTestCase(TestCase):
    """Testes para o model ProcessoInstancia"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            perfil='OPERADOR'
        )
        self.template = TemplateProcesso.objects.create(
            nome='Template Teste',
            criado_por=self.user
        )
        self.etapa = Etapa.objects.create(
            template=self.template,
            nome='Etapa 1',
            ordem=1,
            prazo_dias=5
        )
        self.etapa.usuarios_permitidos.add(self.user)
    
    def test_processo_numero_gerado(self):
        """Testa geração automática de número do processo"""
        processo = ProcessoInstancia.objects.create(
            template=self.template,
            titulo='Processo Teste',
            criado_por=self.user
        )
        self.assertIsNotNone(processo.numero_processo)
        self.assertIn('/', processo.numero_processo)
    
    def test_processo_iniciar(self):
        """Testa inicialização de processo"""
        processo = ProcessoInstancia.objects.create(
            template=self.template,
            titulo='Processo Teste',
            criado_por=self.user
        )
        processo.iniciar(self.user)
        
        self.assertEqual(processo.status, 'EM_ANDAMENTO')
        self.assertEqual(processo.etapa_atual, self.etapa)
        self.assertEqual(processo.usuario_atual, self.user)
    
    def test_processo_concluir(self):
        """Testa conclusão de processo"""
        processo = ProcessoInstancia.objects.create(
            template=self.template,
            titulo='Processo Teste',
            criado_por=self.user
        )
        processo.iniciar(self.user)
        processo.concluir()
        
        self.assertEqual(processo.status, 'CONCLUIDO')
        self.assertIsNotNone(processo.data_conclusao)
        self.assertIsNone(processo.etapa_atual)


class LogAuditoriaTestCase(TestCase):
    """Testes para o model LogAuditoria"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.template = TemplateProcesso.objects.create(
            nome='Template Teste',
            criado_por=self.user
        )
        self.processo = ProcessoInstancia.objects.create(
            template=self.template,
            titulo='Processo Teste',
            criado_por=self.user
        )
    
    def test_log_creation(self):
        """Testa criação de log de auditoria"""
        log = LogAuditoria.objects.create(
            processo=self.processo,
            usuario=self.user,
            acao='INICIO',
            descricao='Processo iniciado'
        )
        
        self.assertEqual(log.acao, 'INICIO')
        self.assertEqual(log.usuario, self.user)
        self.assertIsNotNone(log.data_hora)


class ViewsTestCase(TestCase):
    """Testes para as views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            perfil='ADMIN',
            first_name='Test',
            last_name='User'
        )
        self.template = TemplateProcesso.objects.create(
            nome='Template Teste',
            criado_por=self.user
        )
    
    def test_login_required(self):
        """Testa se dashboard requer login"""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_dashboard_authenticated(self):
        """Testa acesso ao dashboard autenticado"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
    
    def test_template_list_view(self):
        """Testa listagem de templates"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('template_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Template Teste')
    
    def test_processo_create_view(self):
        """Testa criação de processo"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('processo_create'))
        self.assertEqual(response.status_code, 200)
