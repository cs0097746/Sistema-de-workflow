from django.db import migrations

SQL_PROCEDURES = [
    ("sp_encaminhar_processo", """CREATE OR REPLACE PROCEDURE sp_encaminhar_processo(
        p_processo_id BIGINT,
        p_proxima_etapa_id BIGINT,
        p_usuario_id BIGINT,
        p_condicao TEXT
    )
    LANGUAGE plpgsql
    AS $$
    BEGIN
        -- Atualiza a etapa atual
        UPDATE processos_processoinstancia
        SET etapa_atual_id = p_proxima_etapa_id,
            status = 'EM_ANDAMENTO',
            data_atualizacao = NOW(),
            usuario_atual_id = p_usuario_id
        WHERE id = p_processo_id;

        -- Cria log de auditoria
        INSERT INTO processos_logauditoria (processo_id, usuario_id, acao, descricao, data_hora)
        VALUES (p_processo_id, p_usuario_id, 'ENCAMINHAMENTO',
                CONCAT('Processo encaminhado para etapa ', p_proxima_etapa_id, ' via condição ', p_condicao),
                NOW());
    END;
    $$;
    """),
    ("sp_finalizar_processo", """CREATE OR REPLACE PROCEDURE sp_finalizar_processo(p_processo_id BIGINT)
    LANGUAGE plpgsql
    AS $$
    BEGIN
        UPDATE processos_processoinstancia
        SET status = 'CONCLUIDO',
            data_conclusao = NOW(),
            data_atualizacao = NOW()
        WHERE id = p_processo_id;

        INSERT INTO processos_logauditoria (processo_id, acao, descricao, data_hora)
        VALUES (p_processo_id, 'CONCLUSAO', 'Processo concluído automaticamente', NOW());
    END;
    $$;
    """),
    ("sp_cancelar_processo", """<SQL da procedure aqui>"""),
]

class Migration(migrations.Migration):
    dependencies = [
        ('processos', '0003_create_views'),
    ]

    operations = [
        migrations.RunSQL(f"DROP PROCEDURE IF EXISTS {name};") for name, _ in SQL_PROCEDURES
    ] + [
        migrations.RunSQL(sql, reverse_sql=f"DROP PROCEDURE IF EXISTS {name};") for name, sql in SQL_PROCEDURES
    ]
