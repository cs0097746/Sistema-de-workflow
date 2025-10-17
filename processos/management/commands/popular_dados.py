from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from processos.models import (
    TemplateProcesso, Etapa, Encaminhamento,
    ProcessoInstancia
)

User = get_user_model()


class Command(BaseCommand):
    help = 'Popula o banco de dados com dados de exemplo'

    def handle(self, *args, **kwargs):
        self.stdout.write('Criando dados de exemplo...')
        
        # Criar usuários
        self.stdout.write('Criando usuários...')
        
        # Admin
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@workflow.com',
                'first_name': 'Administrador',
                'last_name': 'Sistema',
                'perfil': 'ADMIN',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write(self.style.SUCCESS(f'✓ Usuário {admin.username} criado'))
        
        # Gestor
        gestor, created = User.objects.get_or_create(
            username='gestor',
            defaults={
                'email': 'gestor@workflow.com',
                'first_name': 'Carlos',
                'last_name': 'Gestor',
                'perfil': 'GESTOR',
                'departamento': 'Gestão',
            }
        )
        if created:
            gestor.set_password('gestor123')
            gestor.save()
            self.stdout.write(self.style.SUCCESS(f'✓ Usuário {gestor.username} criado'))
        
        # Operadores
        operador1, created = User.objects.get_or_create(
            username='operador1',
            defaults={
                'email': 'operador1@workflow.com',
                'first_name': 'Maria',
                'last_name': 'Silva',
                'perfil': 'OPERADOR',
                'departamento': 'Financeiro',
            }
        )
        if created:
            operador1.set_password('operador123')
            operador1.save()
            self.stdout.write(self.style.SUCCESS(f'✓ Usuário {operador1.username} criado'))
        
        operador2, created = User.objects.get_or_create(
            username='operador2',
            defaults={
                'email': 'operador2@workflow.com',
                'first_name': 'João',
                'last_name': 'Santos',
                'perfil': 'OPERADOR',
                'departamento': 'RH',
            }
        )
        if created:
            operador2.set_password('operador123')
            operador2.save()
            self.stdout.write(self.style.SUCCESS(f'✓ Usuário {operador2.username} criado'))
        
        # Criar templates
        self.stdout.write('\nCriando templates de processos...')
        
        # Template 1: Solicitação de Compra
        template1, created = TemplateProcesso.objects.get_or_create(
            nome='Solicitação de Compra',
            defaults={
                'descricao': 'Processo para solicitação e aprovação de compras',
                'criado_por': admin,
                'ativo': True,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Template "{template1.nome}" criado'))
            
            # Criar etapas
            etapa1 = Etapa.objects.create(
                template=template1,
                nome='Solicitação Inicial',
                descricao='Preencher formulário de solicitação de compra',
                tipo='EXECUCAO',
                ordem=1,
                prazo_dias=2,
                permite_anexos=True,
            )
            etapa1.usuarios_permitidos.add(operador1, operador2)
            
            etapa2 = Etapa.objects.create(
                template=template1,
                nome='Análise do Gestor',
                descricao='Análise e validação da solicitação',
                tipo='ANALISE',
                ordem=2,
                prazo_dias=3,
                requer_aprovacao=True,
            )
            etapa2.usuarios_permitidos.add(gestor)
            
            etapa3 = Etapa.objects.create(
                template=template1,
                nome='Aprovação Final',
                descricao='Aprovação final da compra',
                tipo='APROVACAO',
                ordem=3,
                prazo_dias=2,
                requer_aprovacao=True,
            )
            etapa3.usuarios_permitidos.add(admin)
            
            etapa4 = Etapa.objects.create(
                template=template1,
                nome='Execução da Compra',
                descricao='Realizar a compra aprovada',
                tipo='EXECUCAO',
                ordem=4,
                prazo_dias=7,
                permite_anexos=True,
            )
            etapa4.usuarios_permitidos.add(operador1)
            
            etapa5 = Etapa.objects.create(
                template=template1,
                nome='Finalização',
                descricao='Confirmação de recebimento',
                tipo='FINALIZACAO',
                ordem=5,
                prazo_dias=2,
            )
            etapa5.usuarios_permitidos.add(operador1, operador2)
            
            # Criar encaminhamentos
            Encaminhamento.objects.create(
                etapa_origem=etapa1,
                etapa_destino=etapa2,
                condicao='Solicitação Enviada',
            )
            Encaminhamento.objects.create(
                etapa_origem=etapa2,
                etapa_destino=etapa3,
                condicao='Aprovado pelo Gestor',
            )
            Encaminhamento.objects.create(
                etapa_origem=etapa3,
                etapa_destino=etapa4,
                condicao='Aprovado',
            )
            Encaminhamento.objects.create(
                etapa_origem=etapa4,
                etapa_destino=etapa5,
                condicao='Compra Realizada',
            )
            
            self.stdout.write(self.style.SUCCESS(f'  ✓ 5 etapas criadas'))
        
        # Template 2: Solicitação de Férias
        template2, created = TemplateProcesso.objects.get_or_create(
            nome='Solicitação de Férias',
            defaults={
                'descricao': 'Processo para solicitação e aprovação de férias',
                'criado_por': admin,
                'ativo': True,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Template "{template2.nome}" criado'))
            
            etapa1 = Etapa.objects.create(
                template=template2,
                nome='Solicitação de Férias',
                descricao='Funcionário solicita férias',
                tipo='EXECUCAO',
                ordem=1,
                prazo_dias=1,
            )
            etapa1.usuarios_permitidos.add(operador1, operador2)
            
            etapa2 = Etapa.objects.create(
                template=template2,
                nome='Aprovação do Gestor',
                descricao='Gestor aprova ou rejeita',
                tipo='APROVACAO',
                ordem=2,
                prazo_dias=2,
                requer_aprovacao=True,
            )
            etapa2.usuarios_permitidos.add(gestor)
            
            etapa3 = Etapa.objects.create(
                template=template2,
                nome='Registro no RH',
                descricao='RH registra as férias',
                tipo='FINALIZACAO',
                ordem=3,
                prazo_dias=1,
            )
            etapa3.usuarios_permitidos.add(operador2)
            
            self.stdout.write(self.style.SUCCESS(f'  ✓ 3 etapas criadas'))
        
        # Template 3: Abertura de Chamado
        template3, created = TemplateProcesso.objects.get_or_create(
            nome='Abertura de Chamado de TI',
            defaults={
                'descricao': 'Processo para abertura e resolução de chamados de TI',
                'criado_por': admin,
                'ativo': True,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Template "{template3.nome}" criado'))
            
            etapa1 = Etapa.objects.create(
                template=template3,
                nome='Abertura do Chamado',
                descricao='Usuário abre chamado',
                tipo='EXECUCAO',
                ordem=1,
                prazo_dias=1,
                permite_anexos=True,
            )
            etapa1.usuarios_permitidos.set(User.objects.all())
            
            etapa2 = Etapa.objects.create(
                template=template3,
                nome='Análise Técnica',
                descricao='Análise técnica do problema',
                tipo='ANALISE',
                ordem=2,
                prazo_dias=2,
            )
            etapa2.usuarios_permitidos.add(operador1)
            
            etapa3 = Etapa.objects.create(
                template=template3,
                nome='Resolução',
                descricao='Resolução do problema',
                tipo='EXECUCAO',
                ordem=3,
                prazo_dias=5,
            )
            etapa3.usuarios_permitidos.add(operador1)
            
            etapa4 = Etapa.objects.create(
                template=template3,
                nome='Validação do Usuário',
                descricao='Usuário valida a resolução',
                tipo='REVISAO',
                ordem=4,
                prazo_dias=2,
            )
            etapa4.usuarios_permitidos.set(User.objects.all())
            
            etapa5 = Etapa.objects.create(
                template=template3,
                nome='Fechamento',
                descricao='Fechamento do chamado',
                tipo='FINALIZACAO',
                ordem=5,
                prazo_dias=1,
            )
            etapa5.usuarios_permitidos.add(operador1)
            
            self.stdout.write(self.style.SUCCESS(f'  ✓ 5 etapas criadas'))
        
        # Criar processo de exemplo
        self.stdout.write('\nCriando processo de exemplo...')
        processo, created = ProcessoInstancia.objects.get_or_create(
            numero_processo='000001/2025',
            defaults={
                'template': template1,
                'titulo': 'Compra de Notebooks para TI',
                'descricao': 'Solicitação de compra de 5 notebooks para o departamento de TI',
                'criado_por': operador1,
            }
        )
        if created:
            processo.iniciar(operador1)
            self.stdout.write(self.style.SUCCESS(f'✓ Processo {processo.numero_processo} criado'))
        
        self.stdout.write(self.style.SUCCESS('\n✅ Dados de exemplo criados com sucesso!'))
        self.stdout.write('\n=== CREDENCIAIS DE ACESSO ===')
        self.stdout.write('Admin: admin / admin123')
        self.stdout.write('Gestor: gestor / gestor123')
        self.stdout.write('Operador: operador1 / operador123')
        self.stdout.write('Operador: operador2 / operador123')
