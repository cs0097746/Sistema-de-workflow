# Sistema de Gerenciamento de Workflows

Sistema web completo desenvolvido em Python com Django para gerenciamento de workflows de processos administrativos.

## Descrição

Sistema robusto e escalável para criação de templates de processos, execução de instâncias, controle de etapas, encaminhamento entre usuários e consultas filtradas. Ideal para automatizar e acompanhar processos administrativos em empresas.

** Banco de Dados:** Atualmente configurado com **Postgresql**;

## Funcionalidades

### Principais Features

- ✅ **Cadastro de Templates de Processos**: Crie templates reutilizáveis com etapas ordenadas e regras customizadas
- ✅ **Execução de Processos**: Inicie instâncias, execute etapas, anexe documentos e encaminhe para usuários
- ✅ **Gestão de Usuários**: Sistema completo de autenticação com perfis (Admin, Gestor, Operador, Visualizador)
- ✅ **Controle de Fluxo**: Acompanhamento detalhado da execução entre etapas
- ✅ **Anexos e Documentos**: Upload e gerenciamento de arquivos em cada etapa
- ✅ **Consultas Avançadas**: Filtros por status, usuário, template, data e mais
- ✅ **Sistema de Permissões**: Controle granular de quem pode executar cada etapa
- ✅ **Logs de Auditoria**: Rastreamento completo de todas as ações nos processos
- ✅ **Dashboard Intuitivo**: Visão geral dos processos e estatísticas
- ✅ **Interface Responsiva**: Design moderno e funcional com Bootstrap 5

## 🛠️ Tecnologias Utilizadas

- **Backend**: Python 3.10+, Django 4.2+
- **Banco de Dados**: PostgreSQL
- **Monitoria**: Prometheus / Prometheus SQL Exporter / Grafana
- **Frontend**: HTML5, Bootstrap 5, Bootstrap Icons
- **Forms**: Django Crispy Forms + Bootstrap 5
- **Autenticação**: Django Auth System (customizado)

## Estrutura do Projeto

```
Sistema-de-workflow/
├── workflow/              # Configurações do projeto Django
│   ├── settings.py       # Configurações principais
│   ├── urls.py           # URLs raiz
│   └── wsgi.py
├── processos/            # App principal de processos
│   ├── models.py         # Models (Template, Etapa, Processo, etc)
│   ├── views.py          # Views CBV e FBV
│   ├── forms.py          # Formulários
│   ├── admin.py          # Configuração do Django Admin
│   ├── urls.py           # URLs da app
│   └── management/       # Comandos customizados
│       └── commands/
│           └── popular_dados.py
├── usuarios/             # App de usuários customizados
│   ├── models.py         # Model Usuario customizado
│   ├── views.py          # Views de autenticação
│   └── admin.py
├── templates/            # Templates HTML
│   ├── base.html         # Template base
│   ├── processos/        # Templates de processos
│   └── usuarios/         # Templates de autenticação
├── static/               # Arquivos estáticos (CSS, JS, imagens)
├── media/                # Arquivos enviados por usuários
├── requirements.txt      # Dependências Python
├── .env.example          # Exemplo de variáveis de ambiente
└── README.md            # Este arquivo
```

## 🚀 Instalação e Configuração

### Pré-requisitos

- Python 3.10 ou superior
- PostgreSQL 13 ou superior
- pip (gerenciador de pacotes Python)
- virtualenv (recomendado)

### Passo a Passo

1. **Clone o repositório**
```bash
git clone https://github.com/cs0097746/Sistema-de-workflow.git
cd Sistema-de-workflow
```

2. **Crie e ative o ambiente virtual**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. **Instale as dependências**
```bash
pip install -r requirements.txt
```

4. **Configure as variáveis de ambiente (opcional)**

Copie o arquivo `.env.example` para `.env`: 
```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

**Nota:** Para SQLite, não é necessário configurar variáveis de banco de dados!

---

## Duas Opções de Banco de Dados

### Opção A: SQLite (Padrão - Recomendado para Testes) - Foi descontinuado, agora utilizamos Postgresql

**Já está configurado!** Não precisa fazer nada.

5. **Execute o script de inicialização**
```powershell
# Windows
.\iniciar_sqlite.ps1

# OU manualmente:
python manage.py migrate
python manage.py popular_dados
```

6. **Inicie o servidor**
```bash
python manage.py runserver
```

**Pronto!** Acesse: http://localhost:8000

**Veja o guia  de testes:** `GUIA_TESTES.md`

---

### Opção B: PostgreSQL (Produção)

Para usar PostgreSQL ao invés de SQLite:

1. **Instale psycopg2**
```bash
pip install psycopg2-binary
```

2. **Crie o banco de dados PostgreSQL**
```sql
CREATE DATABASE workflow_db;
CREATE USER workflow_user WITH PASSWORD 'sua_senha_segura';
ALTER ROLE workflow_user SET client_encoding TO 'utf8';
ALTER ROLE workflow_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE workflow_user SET timezone TO 'America/Sao_Paulo';
GRANT ALL PRIVILEGES ON DATABASE workflow_db TO workflow_user;
```

3. **Configure o `.env`**
```env
SECRET_KEY=sua-chave-secreta-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=workflow_db
DB_USER=workflow_user
DB_PASSWORD=sua_senha_segura
DB_HOST=localhost
DB_PORT=5432
```

4. **Edite `workflow/settings.py`**

Comente o SQLite e descomente o PostgreSQL:
```python
# SQLite (comentar)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

# PostgreSQL (descomentar)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='workflow_db'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default='postgres'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}
```

5. **Execute as migrações**
```bash
python manage.py migrate
python manage.py popular_dados
```

## Credenciais de Acesso

Após executar `python manage.py popular_dados`:

| Usuário | Senha | Perfil | Acesso |
|---------|-------|--------|--------|
| admin | admin123 | Administrador | Total |
| gestor | gestor123 | Gestor | Gerencial |
| operador1 | operador123 | Operador | Execução |
| operador2 | operador123 | Operador | Execução |

## 🌐 Iniciar o Servidor

```bash
python manage.py runserver
```

10. **Acesse o sistema**

Abra o navegador em: `http://localhost:8000`

### Checando monitoria
Pra checar a monitoria é só acessar o grafana; Se for seu primeiro build, será necessário configurar os datasources do prometheus e postgres;
hosts: http://prometheus:9090 | workflow_db:5432 (use senha e password do user da aplicação )

ID's das dashboards pre-configuradas do grafana: 
 - 12485
 - 6742
 - 13494

Obs: precisa ter o pg_stat_statements habilitado; se o pre-shared já estiver configurado, basta rodar um CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

Grafana:
http://localhost:3000 (login default admin / admin)


## 📚 Uso do Sistema

### Fluxo Básico de Trabalho

1. **Login**: Acesse com suas credenciais
2. **Dashboard**: Visualize estatísticas e processos pendentes
3. **Criar Template** (Admin/Gestor):
   - Acesse "Templates" → "Novo Template"
   - Defina nome e descrição
   - Adicione etapas ordenadas
   - Configure permissões por etapa
   
4. **Iniciar Processo**:
   - Acesse "Novo Processo"
   - Selecione o template desejado
   - Preencha título e descrição
   - Clique em "Iniciar Processo"

5. **Executar Etapas**:
   - Acesse "Meus Processos"
   - Clique em "Executar" no processo desejado
   - Preencha observações
   - Anexe documentos se necessário
   - Conclua a etapa
   - Encaminhe para o próximo responsável

6. **Consultar Processos**:
   - Acesse "Todos os Processos"
   - Utilize filtros para buscar
   - Visualize histórico e logs de auditoria

### Perfis de Usuário

- **Administrador**: Acesso total, pode criar templates e gerenciar tudo (admin / admin123)
- **Gestor**: Pode criar templates e gerenciar processos (gestor / gestor123)
- **Operador**: Executa processos conforme permissões (operador1 / operador123)
- **Visualizador**: Apenas visualiza processos

## Testes

Execute os testes unitários:
```bash
python manage.py test processos
```

## Segurança

- ✅ Autenticação obrigatória em todas as rotas
- ✅ Sistema de permissões granular por etapa
- ✅ CSRF protection ativado
- ✅ Senhas hasheadas com Django's PBKDF2
- ✅ Logs de auditoria para rastreamento

## Models Principais

### TemplateProcesso
Define o fluxo de trabalho reutilizável

### Etapa
Cada passo do processo com regras e permissões

### ProcessoInstancia
Instância em execução de um template

### EtapaExecutada
Registro de execução de cada etapa

### LogAuditoria
Histórico completo de ações

## Configs Extras

### Email para Notificações (Se alguém quiser brincar com isso, só conectar em algum SMTP, pode ser o mailtrap no linux por ex.)

Configure no `.env`:
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-app
```

### Personalização de Templates

Templates podem ser customizados editando os arquivos em `templates/`
