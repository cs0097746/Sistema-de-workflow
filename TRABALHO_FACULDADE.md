# 📚 TRABALHO DE BANCO DE DADOS - SISTEMA DE WORKFLOW

**Disciplina:** Projeto e Gerência de Banco de Dados  
**Semestre:** 2025/2  
**Professor:** Sergio Mergen  

---

## 👥 GRUPO

_(Preencher com os nomes dos integrantes)_

- Christian
- Integrante 2
- Integrante 3
- Integrante 4

---

## 🎯 OBJETIVO DO TRABALHO

Desenvolver um sistema de workflow que permita:
1. ✅ Criação de templates de processos
2. ✅ Criação e encaminhamento de processos por usuários
3. ✅ Controle de fluxo entre etapas
4. ✅ Consultas com filtros diversos

---

## 📋 PROPOSTA IMPLEMENTADA

### **Visão Geral**
Sistema completo de gerenciamento de workflows, permitindo:
- Criação de templates reutilizáveis de processos
- Execução de processos seguindo etapas predefinidas
- Encaminhamento automático entre etapas
- Controle de permissões por perfil de usuário
- Auditoria completa de todas as ações
- Consultas avançadas com múltiplos filtros

### **Características Principais**
- Interface web responsiva
- Sistema de autenticação e autorização
- Geração automática de números de processo
- Anexação de documentos por etapa
- Logs de auditoria completos
- Tratamento de concorrência (race conditions)

---

## 🏗️ ARQUITETURA DO SISTEMA

### **Stack Tecnológico**

#### **Backend:**
- **Django 4.2.25** - Framework web Python
  - Escolhido pela robustez e ORM integrado
  - Padrão MTV (Model-Template-View)
  - Admin interface nativa

#### **Banco de Dados:**
- **SQLite** - Desenvolvimento e testes
  - Facilidade de setup
  - Zero configuração
- **PostgreSQL** - Produção (migração disponível)
  - Suporte a transações avançadas
  - Performance para múltiplos usuários

#### **Frontend:**
- **Bootstrap 5** - Framework CSS
- **Django Templates** - Renderização server-side
- **Django Crispy Forms** - Estilização de formulários

### **Arquitetura em Camadas**

```
┌──────────────────────────────────────┐
│     CAMADA DE APRESENTAÇÃO          │
│   (Templates Django + Bootstrap)     │
├──────────────────────────────────────┤
│     CAMADA DE LÓGICA DE NEGÓCIO     │
│      (Views + Forms + Validators)    │
├──────────────────────────────────────┤
│     CAMADA DE ACESSO A DADOS        │
│         (Django ORM + Models)        │
├──────────────────────────────────────┤
│     CAMADA DE PERSISTÊNCIA          │
│       (SQLite / PostgreSQL)          │
└──────────────────────────────────────┘
```

---

## 🗄️ ESQUEMA DO BANCO DE DADOS

### **Modelo Entidade-Relacionamento**

```
┌─────────────────┐
│ Usuario         │
│ ─────────────── │
│ PK id           │
│    username     │
│    perfil       │◄─────┐
│    ...          │      │
└─────────────────┘      │
                         │
┌─────────────────┐      │
│TemplateProcesso │      │
│ ─────────────── │      │
│ PK id           │      │
│    nome         │      │
│    descricao    │      │
│    ativo        │      │
│ FK criado_por   │──────┘
└────────┬────────┘
         │ 1:N
         │
┌────────▼────────┐      ┌─────────────────┐
│ Etapa           │      │ Encaminhamento  │
│ ─────────────── │      │ ─────────────── │
│ PK id           │◄────┐│ PK id           │
│ FK template_id  │     ││ FK etapa_origem │
│    nome         │     ││ FK etapa_destino│
│    ordem        │     │└─────────────────┘
│    tipo         │     │
│    prazo_dias   │     │
└────────┬────────┘     │
         │              │
         │ N:1          │
         │              │
┌────────▼────────┐     │
│ProcessoInstancia│     │
│ ─────────────── │     │
│ PK id           │     │
│ FK template_id  │─────┘
│    numero_proc  │
│    titulo       │
│    status       │
│ FK etapa_atual  │
│ FK usuario_atual│
│ FK criado_por   │
└────────┬────────┘
         │ 1:N
         │
┌────────▼────────┐      ┌─────────────────┐
│EtapaExecutada   │      │ Documento       │
│ ─────────────── │      │ ─────────────── │
│ PK id           │      │ PK id           │
│ FK processo_id  │      │ FK etapa_exec_id│
│ FK etapa_id     │◄─────┤    arquivo      │
│ FK executado_por│      │    nome         │
│    resultado    │      └─────────────────┘
│    observacoes  │
│    data_inicio  │
│    data_conclusao│
└─────────────────┘

┌─────────────────┐
│ LogAuditoria    │
│ ─────────────── │
│ PK id           │
│ FK processo_id  │
│ FK usuario_id   │
│    acao         │
│    descricao    │
│    data_hora    │
└─────────────────┘
```

### **Descrição das Entidades**

#### **1. Usuario**
Armazena informações dos usuários do sistema.
- **Campos principais:** username, email, perfil (ADMIN/GESTOR/OPERADOR)
- **Relacionamentos:** Criador de templates e processos, executor de etapas

#### **2. TemplateProcesso**
Define modelos reutilizáveis de processos.
- **Campos principais:** nome, descrição, ativo
- **Relacionamentos:** Possui múltiplas etapas (1:N)

#### **3. Etapa**
Define cada passo de um template.
- **Campos principais:** nome, ordem, tipo, prazo_dias
- **Constraint:** `UNIQUE(template_id, ordem)` - garante ordem única por template
- **Relacionamentos:** Pertence a um template, possui encaminhamentos possíveis

#### **4. Encaminhamento**
Define caminhos possíveis entre etapas.
- **Campos principais:** etapa_origem, etapa_destino, condicao
- **Relacionamentos:** Conecta duas etapas

#### **5. ProcessoInstancia**
Representa uma execução de um template.
- **Campos principais:** numero_processo (único), titulo, status
- **Constraint:** `UNIQUE(numero_processo)` - garante unicidade
- **Relacionamentos:** Baseado em template, possui etapas executadas

#### **6. EtapaExecutada**
Registra a execução de cada etapa de um processo.
- **Campos principais:** resultado, observacoes, data_inicio, data_conclusao
- **Relacionamentos:** Pertence a processo e etapa, executada por usuário

#### **7. Documento**
Armazena anexos de etapas executadas.
- **Campos principais:** arquivo, nome, data_upload
- **Relacionamentos:** Associado a uma etapa executada

#### **8. LogAuditoria**
Registra todas as ações no sistema.
- **Campos principais:** acao, descricao, data_hora
- **Relacionamentos:** Associado a processo e usuário

---

## 🔧 RECURSOS DO BANCO DE DADOS

### **1. Transações (ACID)**
```python
from django.db import transaction

with transaction.atomic():
    # Operações críticas garantem atomicidade
    processo.etapa_atual = proxima_etapa
    processo.save()
    log.create(...)
```

**Uso:**
- Criação de processos
- Execução de etapas
- Encaminhamentos
- Garantia de consistência

### **2. Row-Level Locking**
```python
# Locking pessimista para evitar race conditions
ultimo = ProcessoInstancia.objects.select_for_update().filter(
    numero_processo__endswith=f'/{ano}'
).order_by('-numero_processo').first()
```

**Uso:**
- Geração de números sequenciais
- Auto-incremento de ordem de etapas
- Prevenção de duplicatas

### **3. Constraints e Validações**
```python
class Meta:
    unique_together = ['template', 'ordem']  # Etapa
    
class ProcessoInstancia:
    numero_processo = models.CharField(unique=True)
```

**Integridade garantida por:**
- Unique constraints
- Foreign keys com ON_DELETE
- Validações de modelo
- Validações de formulário

### **4. Indexes e Otimizações**
```python
# Select related para reduzir queries
ProcessoInstancia.objects.select_related(
    'template', 'etapa_atual', 'usuario_atual', 'criado_por'
).prefetch_related('etapas_executadas')
```

**Benefícios:**
- Redução de N+1 queries
- Performance melhorada
- Menos carga no banco

---

## 💡 INTERAÇÃO COM O BANCO DE DADOS

### **1. Consultas (SELECT)**

#### **Listagem com Filtros**
```python
queryset = ProcessoInstancia.objects.all()

# Filtros dinâmicos
if numero_processo:
    queryset = queryset.filter(numero_processo__icontains=numero_processo)
if template:
    queryset = queryset.filter(template=template)
if status:
    queryset = queryset.filter(status=status)
if data_inicio:
    queryset = queryset.filter(data_criacao__gte=data_inicio)
if data_fim:
    queryset = queryset.filter(data_criacao__lte=data_fim)

# Otimização com joins
queryset = queryset.select_related(
    'template', 'etapa_atual', 'usuario_atual'
)

# Paginação
queryset = queryset.order_by('-data_criacao')[:15]
```

#### **Agregações**
```python
# Contagem de processos por status
from django.db.models import Count

stats = ProcessoInstancia.objects.values('status').annotate(
    total=Count('id')
)

# Templates com número de etapas
templates = TemplateProcesso.objects.annotate(
    num_etapas=Count('etapas')
)
```

### **2. Inserções (INSERT)**

#### **Criação de Processo com Número Automático**
```python
def save(self, *args, **kwargs):
    if not self.numero_processo:
        with transaction.atomic():
            ano = timezone.now().year
            
            # Lock e busca último número
            ultimo = ProcessoInstancia.objects.select_for_update().filter(
                numero_processo__endswith=f'/{ano}'
            ).order_by('-numero_processo').first()
            
            if ultimo:
                numero = int(ultimo.numero_processo.split('/')[0]) + 1
            else:
                numero = 1
            
            # Retry até 10 vezes
            for tentativa in range(10):
                numero_temp = f"{numero:06d}/{ano}"
                if not ProcessoInstancia.objects.filter(
                    numero_processo=numero_temp
                ).exists():
                    self.numero_processo = numero_temp
                    break
                numero += 1
    
    super().save(*args, **kwargs)
```

### **3. Atualizações (UPDATE)**

#### **Execução de Etapa**
```python
def executar_etapa(processo, usuario, resultado, observacoes):
    with transaction.atomic():
        # Cria registro de execução
        etapa_exec = EtapaExecutada.objects.create(
            processo=processo,
            etapa=processo.etapa_atual,
            executado_por=usuario,
            resultado=resultado,
            observacoes=observacoes
        )
        
        # Avança processo
        proxima = processo.etapa_atual.get_proxima_etapa()
        if proxima:
            processo.etapa_atual = proxima
            processo.usuario_atual = usuario
        else:
            processo.status = 'CONCLUIDO'
            processo.etapa_atual = None
        
        processo.save()
        
        # Log de auditoria
        LogAuditoria.objects.create(
            processo=processo,
            usuario=usuario,
            acao='EXECUCAO_ETAPA',
            descricao=f'Etapa {etapa_exec.etapa.nome} executada'
        )
```

### **4. Deleções (DELETE)**

#### **Soft Delete vs Hard Delete**
```python
# Soft delete - desativa em vez de deletar
template.ativo = False
template.save()

# Hard delete com cascade
processo.delete()  # Deleta etapas executadas, logs, documentos
```

---

## 🎨 REQUISITOS IMPLEMENTADOS

### **✅ Requisitos Obrigatórios**

1. **Criação de Templates de Processos**
   - Interface CRUD completa
   - Validação de fluxo
   - Gestão de etapas

2. **Criação e Encaminhamento de Processos**
   - Baseado em templates
   - Encaminhamento automático
   - Controle de responsáveis

3. **Controle de Fluxo entre Etapas**
   - Sequência automática
   - Validação de permissões
   - Status por etapa

4. **Consultas com Filtros**
   - 7 filtros diferentes
   - Combinação de filtros
   - Paginação

### **🌟 Requisitos Extras (Diferenciais)**

1. **Sistema de Auditoria**
   - Log de todas as ações
   - Rastreabilidade completa
   - Timestamps automáticos

2. **Controle de Permissões**
   - 3 perfis de usuário
   - Permissões por etapa
   - Validação em múltiplas camadas

3. **Anexação de Documentos**
   - Upload de arquivos
   - Associação por etapa
   - Controle de tamanho

4. **Geração Automática de Números**
   - Formato padronizado
   - Sequencial por ano
   - Tratamento de concorrência

5. **Validações Avançadas**
   - No modelo
   - No formulário
   - No banco (constraints)

---

## 🧪 TESTES E VALIDAÇÃO

### **Casos de Teste Implementados**

1. ✅ Criação de templates com múltiplas etapas
2. ✅ Criação simultânea de processos (concorrência)
3. ✅ Execução de fluxo completo
4. ✅ Filtros combinados
5. ✅ Permissões por perfil
6. ✅ Anexação de documentos
7. ✅ Auditoria completa

### **Script de Testes**
```powershell
# Resetar banco e popular dados de teste
.\resetar_banco.ps1

# Executar servidor
python manage.py runserver

# Seguir guia de testes
# Veja: COMO_TESTAR.md
```

---

## 📊 PONTOS FORTES DO PROJETO

### **1. Arquitetura Consistente**
- Separação clara de responsabilidades
- Camadas bem definidas
- Padrões de projeto aplicados

### **2. Acesso aos Dados Sofisticado**
- ORM otimizado
- Transações ACID
- Locking para concorrência
- Queries eficientes

### **3. Integridade de Dados**
- Constraints no banco
- Validações em múltiplas camadas
- Tratamento de erros

### **4. Rastreabilidade**
- Logs completos
- Histórico de execuções
- Auditoria de todas as ações

### **5. Usabilidade**
- Interface intuitiva
- Feedback claro
- Documentação completa

---

## 📈 POSSÍVEIS MELHORIAS FUTURAS

1. **Notificações**
   - Email ao receber processo
   - Alertas de prazo

2. **Dashboard Analytics**
   - Gráficos de performance
   - Estatísticas por template
   - Tempo médio por etapa

3. **Workflow Condicional**
   - Múltiplos caminhos
   - Decisões baseadas em resultado

4. **API REST**
   - Django REST Framework
   - Integração com outros sistemas

5. **Testes Automatizados**
   - Unit tests
   - Integration tests
   - Coverage report

---

## 📚 DOCUMENTAÇÃO DISPONÍVEL

1. **README.md** - Visão geral do projeto
2. **COMO_TESTAR.md** - Guia completo de testes
3. **CORRECOES_FLUXO.md** - Melhorias implementadas
4. **MIGRACAO_BANCO.md** - Como migrar para PostgreSQL
5. **Scripts PowerShell** - Automação de tarefas

---

## 🎬 DEMONSTRAÇÃO

### **Fluxo Completo de Uso**

1. **Login** → Admin, Gestor ou Operador
2. **Criar Template** → "Solicitação de Compra" com 4 etapas
3. **Criar Processo** → Baseado no template criado
4. **Executar Etapas** → Avanço automático entre etapas
5. **Consultar Processos** → Filtros por status, template, etc
6. **Ver Histórico** → Auditoria completa de ações
7. **Django Admin** → Gestão avançada de dados

---

## 🎯 CONCLUSÃO

O sistema desenvolvido atende **completamente** aos requisitos do trabalho:
- ✅ Todos os requisitos obrigatórios implementados
- ✅ Arquitetura consistente e bem documentada
- ✅ Interação sofisticada com banco de dados
- ✅ Recursos avançados de banco (transactions, locking)
- ✅ Interface funcional e intuitiva
- ✅ Código limpo e bem estruturado

**Diferenciais:**
- Sistema de auditoria completo
- Tratamento de concorrência
- Validações em múltiplas camadas
- Documentação extensa


**Data de Entrega:** (A confirmar)  
**Data de Apresentação:** (A confirmar)
