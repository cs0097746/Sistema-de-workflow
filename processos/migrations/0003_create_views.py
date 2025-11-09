from django.db import migrations

VIEW_SQLS = [
    ("vw_processos_pendentes", """
    CREATE OR REPLACE VIEW vw_processos_pendentes AS
    SELECT
        p.id AS processo_id,
        p.numero_processo,
        p.titulo,
        p.status,
        p.data_criacao,
        p.data_atualizacao,
        u.username AS usuario_atual,
        c.username AS criado_por,
        e.nome AS etapa_atual,
        t.nome AS template_nome
    FROM processos_processoinstancia p
    LEFT JOIN usuarios_usuario c ON p.criado_por_id = c.id
    LEFT JOIN usuarios_usuario u ON p.usuario_atual_id = u.id
    LEFT JOIN processos_etapa e ON p.etapa_atual_id = e.id
    LEFT JOIN processos_templateprocesso t ON p.template_id = t.id
    WHERE p.status IN ('EM_ANDAMENTO', 'AGUARDANDO')
    ORDER BY p.data_criacao DESC;
    """),
    ("vw_processos_concluidos", """
    CREATE OR REPLACE VIEW vw_processos_concluidos AS
    SELECT
        p.id AS processo_id,
        p.numero_processo,
        p.titulo,
        t.nome AS template_nome,
        p.data_criacao,
        p.data_conclusao,
        ROUND(EXTRACT(EPOCH FROM (p.data_conclusao - p.data_criacao)) / 3600, 2) AS horas_execucao,
        c.username AS criado_por
    FROM processos_processoinstancia p
    LEFT JOIN usuarios_usuario c ON p.criado_por_id = c.id
    LEFT JOIN processos_templateprocesso t ON p.template_id = t.id
    WHERE p.status = 'CONCLUIDO'
    ORDER BY p.data_conclusao DESC;
    """),
    ("vw_etapas_em_execucao", """
    CREATE OR REPLACE VIEW vw_etapas_em_execucao AS
    SELECT
        e.id AS etapa_exec_id,
        et.nome AS etapa_nome,
        p.numero_processo,
        p.titulo AS processo_titulo,
        u.username AS executado_por,
        e.data_inicio,
        e.data_conclusao,
        e.resultado,
        t.nome AS template_nome
    FROM processos_etapaexecutada e
    JOIN processos_etapa et ON e.etapa_id = et.id
    JOIN processos_processoinstancia p ON e.processo_id = p.id
    JOIN processos_templateprocesso t ON p.template_id = t.id
    LEFT JOIN usuarios_usuario u ON e.executado_por_id = u.id
    WHERE e.resultado IN ('PENDENTE', 'CONCLUIDO')
    ORDER BY e.data_inicio DESC;
    """),
    ("vw_usuarios_desempenho", """
    CREATE OR REPLACE VIEW vw_usuarios_desempenho AS
    SELECT
        u.id AS usuario_id,
        u.username,
        COUNT(e.id) AS total_etapas,
        SUM(CASE WHEN e.resultado = 'APROVADO' THEN 1 ELSE 0 END) AS total_aprovadas,
        SUM(CASE WHEN e.resultado = 'REJEITADO' THEN 1 ELSE 0 END) AS total_rejeitadas,
        SUM(CASE WHEN e.resultado = 'CONCLUIDO' THEN 1 ELSE 0 END) AS total_concluidas
    FROM processos_etapaexecutada e
    JOIN usuarios_usuario u ON e.executado_por_id = u.id
    GROUP BY u.id, u.username
    ORDER BY total_etapas DESC;
    """)
]

class Migration(migrations.Migration):
    dependencies = [
        ('processos', '0002_initial'),
    ]

    operations: list[migrations.operations.base.Operation] = []

    for name, _ in VIEW_SQLS:
        operations.append(
            migrations.RunSQL(
                sql=f"DROP VIEW IF EXISTS {name};",
                reverse_sql="",
            )
        )

    for name, sql in VIEW_SQLS:
        operations.append(
            migrations.RunSQL(
                sql=sql,
                reverse_sql=f"DROP VIEW IF EXISTS {name};",
            )
        )
