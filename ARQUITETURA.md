# Arquitetura do Sistema de Workflow

## Visão Geral da Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│                        CAMADA DE APRESENTAÇÃO                    │
│                          (Templates HTML)                        │
├─────────────────────────────────────────────────────────────────┤
│  Dashboard  │  Templates  │  Processos  │  Etapas  │  Docs     │
│    .html    │    .html    │    .html    │  .html   │  .html    │
└─────────────────────────────────────────────────────────────────┘
                              ↑↓
┌─────────────────────────────────────────────────────────────────┐
│                      CAMADA DE CONTROLE                          │
│                          (Views)                                 │
├─────────────────────────────────────────────────────────────────┤
│  Class-Based Views        │       Function-Based Views          │
│  - TemplateListView       │       - dashboard()                 │
│  - ProcessoListView       │       - processo_executar()         │
│  - CreateView             │       - etapa_create()              │
│  - UpdateView             │       - documento_upload()          │
│  - DetailView             │       - processo_encaminhar()       │
└─────────────────────────────────────────────────────────────────┘
                              ↑↓
┌─────────────────────────────────────────────────────────────────┐
│                      CAMADA DE NEGÓCIO                           │
│                     (Models & Forms)                             │
├─────────────────────────────────────────────────────────────────┤
│  Models:                  │       Forms:                        │
│  - Usuario                │       - TemplateProcessoForm        │
│  - TemplateProcesso       │       - EtapaForm                   │
│  - Etapa                  │       - ProcessoInstanciaForm       │
│  - ProcessoInstancia      │       - EtapaExecutadaForm          │
│  - EtapaExecutada         │       - DocumentoForm               │
│  - Documento              │       - ProcessoFiltroForm          │
│  - LogAuditoria           │       - EncaminharProcessoForm      │
└─────────────────────────────────────────────────────────────────┘
                              ↑↓
┌─────────────────────────────────────────────────────────────────┐
│                      CAMADA DE PERSISTÊNCIA                      │
│                     (Django ORM + PostgreSQL)                    │
├─────────────────────────────────────────────────────────────────┤
│  PostgreSQL Database                                            │
│  - Tables com relacionamentos                                   │
│  - Constraints e índices                                        │
│  - Transações ACID                                              │
└─────────────────────────────────────────────────────────────────┘
```

## Fluxo de Dados

### 1. Criação de Processo

```
Usuário
  │
  ↓ (HTTP Request)
┌─────────────────┐
│ processo_create │ ← View (FBV)
│     (view)      │
└─────────────────┘
  │
  ↓ (valida dados)
┌──────────────────────┐
│ProcessoInstanciaForm │ ← Form
└──────────────────────┘
  │
  ↓ (save)
┌──────────────────────┐
│  ProcessoInstancia   │ ← Model
│       (model)        │
└──────────────────────┘
  │
  ↓ (SQL INSERT)
┌──────────────────────┐
│    PostgreSQL        │ ← Database
└──────────────────────┘
  │
  ↓ (iniciar processo)
┌──────────────────────┐
│   LogAuditoria       │ ← Model (log)
└──────────────────────┘
  │
  ↓ (redirect)
┌──────────────────────┐
│  processo_detail     │ ← View
│    (template)        │
└──────────────────────┘
```

### 2. Execução de Etapa

```
Usuário clica "Executar"
  │
  ↓
processo_executar_etapa (view)
  │
  ├─→ Verifica permissão (pode_ser_executado_por)
  │
  ├─→ Renderiza EtapaExecutadaForm
  │
  ↓ (POST)
  ├─→ Cria EtapaExecutada
  │
  ├─→ Chama etapa_executada.concluir()
  │
  ├─→ Cria LogAuditoria
  │
  ├─→ Verifica próxima etapa
  │
  └─→ Redirect para encaminhamento ou conclusão
```

### 3. Sistema de Permissões

```
┌─────────────────────────────────────────┐
│           Verificação Multi-Camada       │
├─────────────────────────────────────────┤
│  1. View (LoginRequiredMixin)           │
│     ↓                                    │
│  2. View (perfil do usuário)            │
│     ↓                                    │
│  3. Model (pode_ser_executado_por)      │
│     ↓                                    │
│  4. Model (pode_executar_etapa)         │
│     ↓                                    │
│  5. Etapa (usuarios_permitidos)         │
└─────────────────────────────────────────┘
```

## Relacionamentos entre Models

```
                    ┌──────────────┐
                    │   Usuario    │
                    └──────┬───────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        │ criado_por   criado_por   executado_por
        │                  │                  │
        ↓                  ↓                  ↓
┌───────────────┐  ┌──────────────────┐  ┌─────────────────┐
│ Template      │  │ ProcessoInstancia│  │ EtapaExecutada  │
│ Processo      │  └────────┬─────────┘  └────────┬────────┘
└───────┬───────┘           │                     │
        │                   │                     │
        │ template          │ processo            │ etapa_executada
        │                   │                     │
        ↓                   ↓                     ↓
┌───────────────┐  ┌──────────────────┐  ┌─────────────────┐
│    Etapa      │  │  LogAuditoria    │  │   Documento     │
└───────┬───────┘  └──────────────────┘  └─────────────────┘
        │
        │ etapa_origem/destino
        │
        ↓
┌───────────────┐
│Encaminhamento │
└───────────────┘
```

## Estrutura de Diretórios Detalhada

```
workflow/
├── settings.py              → Configurações centralizadas
├── urls.py                  → Roteamento raiz
└── wsgi.py                  → Interface WSGI

processos/
├── models.py               → 7 models principais
├── views.py                → 15+ views (CBV e FBV)
├── forms.py                → 7 forms completos
├── admin.py                → Admin customizado
├── urls.py                 → 20+ rotas
└── management/
    └── commands/
        └── popular_dados.py → Comando de seed

usuarios/
├── models.py               → Usuario (AbstractUser)
├── views.py                → Login/Logout
├── admin.py                → Admin de usuários
└── urls.py                 → Rotas de auth

templates/
├── base.html               → Template pai
├── processos/
│   ├── dashboard.html      → Dashboard
│   ├── processo_*.html     → Templates de processo
│   ├── template_*.html     → Templates de template
│   ├── etapa_*.html        → Templates de etapa
│   └── documento_*.html    → Templates de documento
└── usuarios/
    └── login.html          → Login

static/                     → CSS, JS, Imagens
media/                      → Uploads de usuários
```

## Tecnologias por Camada

### Frontend (Apresentação)
- HTML5
- Bootstrap 5.3
- Bootstrap Icons 1.11
- Django Template Language

### Backend (Lógica)
- Python 3.10+
- Django 4.2+
- Django ORM
- Crispy Forms + Bootstrap5

### Banco de Dados
- PostgreSQL 13+
- psycopg2-binary

### Segurança
- Django Auth System
- CSRF Protection
- Password Hashing (PBKDF2)
- Permissões customizadas

### Deployment
- Gunicorn (WSGI)
- Nginx (Reverse Proxy)
- Systemd (Service)
- Docker (Container)

## Patterns Utilizados

### Design Patterns
- **MVC**: Model-View-Controller/Template
- **Repository**: Django ORM como abstração
- **Factory**: User.objects.create_user()
- **Decorator**: @login_required
- **Mixin**: LoginRequiredMixin
- **Template Method**: Class-Based Views

### Best Practices
- DRY (Don't Repeat Yourself)
- SOLID principles
- Clean Code
- PEP 8
- Separation of Concerns
- Single Responsibility

## Escalabilidade

### Horizontal
- Múltiplos workers Gunicorn
- Load balancing com Nginx
- Database connection pooling
- Cache com Redis (preparado)

### Vertical
- QuerySet optimization
- select_related / prefetch_related
- Database indexes
- Paginação

## Segurança em Camadas

```
┌─────────────────────────────────────┐
│  1. Nginx (SSL, Rate Limiting)      │
├─────────────────────────────────────┤
│  2. Django Middleware (CSRF, XSS)   │
├─────────────────────────────────────┤
│  3. View (Authentication Required)   │
├─────────────────────────────────────┤
│  4. Model (Authorization)           │
├─────────────────────────────────────┤
│  5. Database (Constraints)          │
└─────────────────────────────────────┘
```

## Performance

### Otimizações Implementadas
- QuerySet optimization
- Select related / Prefetch related
- Paginação (15 itens/página)
- Static files compression (produção)
- Database indexes
- Template caching (produção)

### Métricas Esperadas
- Tempo de resposta: < 200ms (maioria)
- Queries por request: < 10 (otimizado)
- Tamanho de página: < 500KB
- Concurrent users: 100+ (produção)

---

**Arquitetura Modular, Escalável e Segura**
