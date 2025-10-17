# Estrutura de Diretórios do Projeto

## Visão Geral da Estrutura

```
Sistema-de-workflow/
│
├── workflow/                      # Configurações principais do Django
│   ├── __init__.py
│   ├── settings.py               # Configurações do projeto
│   ├── urls.py                   # URLs raiz do projeto
│   ├── asgi.py                   # Configuração ASGI
│   └── wsgi.py                   # Configuração WSGI
│
├── processos/                     # App principal - Gerenciamento de Processos
│   ├── migrations/               # Migrações do banco de dados
│   ├── management/               # Comandos customizados
│   │   └── commands/
│   │       └── popular_dados.py # Comando para popular dados de exemplo
│   ├── __init__.py
│   ├── admin.py                  # Configuração do Django Admin
│   ├── apps.py                   # Configuração da app
│   ├── forms.py                  # Formulários (Templates, Processos, etc)
│   ├── models.py                 # Models (Template, Etapa, Processo, etc)
│   ├── tests.py                  # Testes unitários
│   ├── urls.py                   # URLs da app
│   └── views.py                  # Views (CBV e FBV)
│
├── usuarios/                      # App de Usuários Customizados
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py                  # Admin customizado para usuários
│   ├── apps.py
│   ├── models.py                 # Model Usuario customizado
│   ├── tests.py
│   ├── urls.py                   # URLs de autenticação
│   └── views.py                  # Views de login/logout
│
├── templates/                     # Templates HTML
│   ├── base.html                 # Template base (navbar, footer, etc)
│   ├── processos/                # Templates da app processos
│   │   ├── dashboard.html        # Dashboard principal
│   │   ├── processo_list.html    # Lista de processos
│   │   ├── processo_detail.html  # Detalhes do processo
│   │   ├── processo_form.html    # Criar novo processo
│   │   ├── etapa_executar.html   # Executar etapa
│   │   ├── processo_encaminhar.html # Encaminhar processo
│   │   ├── meus_processos.html   # Processos do usuário
│   │   ├── template_list.html    # Lista de templates
│   │   ├── template_detail.html  # Detalhes do template
│   │   ├── template_form.html    # Criar/editar template
│   │   ├── etapa_form.html       # Criar/editar etapa
│   │   └── documento_form.html   # Upload de documento
│   └── usuarios/
│       └── login.html            # Página de login
│
├── static/                        # Arquivos estáticos (CSS, JS, Imagens)
│   ├── css/                      # (Para CSS customizado)
│   ├── js/                       # (Para JavaScript customizado)
│   └── img/                      # (Para imagens)
│
├── staticfiles/                   # Arquivos estáticos coletados (produção)
│
├── media/                         # Arquivos enviados por usuários
│   └── documentos/               # Documentos dos processos
│       └── YYYY/MM/              # Organizados por ano/mês
│
├── venv/                          # Ambiente virtual Python (não versionado)
│
├── .env                           # Variáveis de ambiente (não versionado)
├── .env.example                   # Exemplo de variáveis de ambiente
├── .gitignore                     # Arquivos ignorados pelo Git
├── requirements.txt               # Dependências Python
├── manage.py                      # Script de gerenciamento Django
├── README.md                      # Documentação principal
├── DEPLOY.md                      # Guia de deploy
├── ESTRUTURA.md                   # Este arquivo
├── setup.sh                       # Script de setup (Linux/Mac)
└── setup.ps1                      # Script de setup (Windows)
```

## Detalhamento dos Arquivos Principais

### Configuração (workflow/)

**settings.py**
- Configurações do Django
- Conexão com PostgreSQL
- Apps instaladas
- Middleware
- Configuração de templates
- Arquivos estáticos e mídia
- Internacionalização (pt-BR)
- Model de usuário customizado

**urls.py**
- Roteamento principal
- Inclui URLs das apps
- Configuração de arquivos estáticos

### Models (processos/models.py)

1. **TemplateProcesso**: Define templates reutilizáveis de processos
   - Campos: nome, descrição, ativo, criado_por
   - Métodos: get_primeira_etapa(), validar_fluxo()

2. **Etapa**: Define etapas dos templates
   - Campos: nome, descrição, tipo, ordem, prazo_dias
   - Relacionamentos: template, usuarios_permitidos
   - Métodos: get_proxima_etapa(), get_encaminhamentos_possiveis()

3. **Encaminhamento**: Define fluxo entre etapas
   - Campos: etapa_origem, etapa_destino, condicao

4. **ProcessoInstancia**: Instância em execução de um processo
   - Campos: numero_processo, titulo, status, etapa_atual
   - Métodos: iniciar(), pode_ser_executado_por(), concluir()

5. **EtapaExecutada**: Registro de execução de etapas
   - Campos: processo, etapa, executado_por, resultado
   - Métodos: concluir()

6. **Documento**: Documentos anexados às etapas
   - Campos: nome, tipo, arquivo, etapa_executada

7. **LogAuditoria**: Logs de todas as ações
   - Campos: processo, usuario, acao, descricao, data_hora

### Model Customizado (usuarios/models.py)

**Usuario**: Estende AbstractUser
- Campos adicionais: cpf, telefone, departamento, perfil
- Perfis: ADMIN, GESTOR, OPERADOR, VISUALIZADOR
- Métodos: pode_executar_etapa(), pode_visualizar_processo()

### Forms (processos/forms.py)

1. **TemplateProcessoForm**: Criar/editar templates
2. **EtapaForm**: Criar/editar etapas
3. **ProcessoInstanciaForm**: Iniciar novos processos
4. **EtapaExecutadaForm**: Executar etapas
5. **DocumentoForm**: Upload de documentos
6. **ProcessoFiltroForm**: Filtrar processos
7. **EncaminharProcessoForm**: Encaminhar para próxima etapa

### Views (processos/views.py)

**Function-Based Views (FBV)**:
- dashboard(): Dashboard principal
- etapa_create(): Criar etapa
- etapa_update(): Editar etapa
- processo_create(): Criar processo
- processo_executar_etapa(): Executar etapa
- processo_encaminhar(): Encaminhar processo
- documento_upload(): Upload de documento
- meus_processos(): Processos do usuário

**Class-Based Views (CBV)**:
- TemplateProcessoListView: Lista templates
- TemplateProcessoDetailView: Detalhes do template
- TemplateProcessoCreateView: Criar template
- TemplateProcessoUpdateView: Editar template
- ProcessoListView: Lista processos com filtros
- ProcessoDetailView: Detalhes do processo

### Admin (processos/admin.py)

Interfaces customizadas para:
- TemplateProcesso (com inline de etapas)
- Etapa (com filter_horizontal para usuários)
- Encaminhamento
- ProcessoInstancia (com inline de etapas executadas)
- EtapaExecutada
- Documento
- LogAuditoria (read-only)

### Templates HTML

**Base Template (base.html)**:
- Navbar responsiva com Bootstrap 5
- Sistema de mensagens
- Footer
- Bootstrap Icons

**Processos**:
- Dashboard com estatísticas e gráficos
- Listas com paginação e filtros
- Formulários com Crispy Forms
- Detalhes com histórico e logs

### Comandos de Management

**popular_dados.py**:
- Cria usuários de teste
- Cria 3 templates completos:
  1. Solicitação de Compra (5 etapas)
  2. Solicitação de Férias (3 etapas)
  3. Abertura de Chamado de TI (5 etapas)
- Cria processo de exemplo

## Fluxo de Dados

1. **Criação de Template**:
   - Admin/Gestor cria TemplateProcesso
   - Adiciona Etapas ordenadas
   - Define Encaminhamentos (opcional)
   - Configura permissões por etapa

2. **Execução de Processo**:
   - Usuário inicia ProcessoInstancia
   - Sistema define etapa_atual e usuario_atual
   - Usuário executa EtapaExecutada
   - Anexa Documentos (opcional)
   - Encaminha para próxima etapa
   - Sistema cria LogAuditoria

3. **Consulta e Monitoramento**:
   - Usuário consulta processos com filtros
   - Visualiza histórico de etapas
   - Acessa logs de auditoria
   - Dashboard mostra estatísticas

## Segurança

- Autenticação obrigatória em todas as rotas
- Permissões granulares por etapa
- Verificações em views e models
- CSRF protection
- Logs de auditoria com rastreamento

## Performance

- QuerySets otimizados com select_related e prefetch_related
- Paginação em listas
- Índices no banco de dados
- Cache de templates (produção)

## Testes

- Testes unitários para models
- Testes para views
- Testes de integração para fluxos
- Cobertura de código

## Convenções

- Models: PascalCase (TemplateProcesso)
- Views: snake_case (processo_create)
- URLs: kebab-case (processo-create)
- Templates: snake_case.html
- Variáveis: snake_case
- Constantes: UPPER_CASE

## Próximos Passos

Para expandir o projeto:
1. Adicionar API REST (Django REST Framework)
2. Implementar notificações por email
3. Criar dashboard com gráficos (Chart.js)
4. Adicionar webhooks
5. Implementar busca full-text
6. Criar aplicativo mobile
