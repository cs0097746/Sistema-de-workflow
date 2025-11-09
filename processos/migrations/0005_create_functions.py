from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('processos', '0004_create_procedures'),
    ]

    operations = [
        migrations.RunSQL(
            """
            CREATE OR REPLACE FUNCTION sp_encaminhar_processo(
                p_processo_id INT,
                p_proxima_etapa_id INT,
                p_usuario_id INT,
                p_observacao TEXT DEFAULT NULL
            )
            RETURNS VOID AS $$
            DECLARE
                v_etapa_atual_id INT;
            BEGIN
                -- Checa a etapa atual
                SELECT etapa_atual_id INTO v_etapa_atual_id
                FROM processos_processoinstancia
                WHERE id = p_processo_id
                FOR UPDATE;

                -- Atualiza processo
                UPDATE processos_processoinstancia
                SET
                    etapa_atual_id = p_proxima_etapa_id,
                    usuario_atual_id = p_usuario_id,
                    data_atualizacao = NOW()
                WHERE id = p_processo_id;

                -- Registra encaminhamento
                INSERT INTO processos_encaminhamento (
                    processo_id,
                    etapa_origem_id,
                    etapa_destino_id,
                    encaminhado_por_id,
                    usuario_destino_id,
                    observacoes,
                    data_encaminhamento
                )
                VALUES (
                    p_processo_id,
                    v_etapa_atual_id,
                    p_proxima_etapa_id,
                    p_usuario_id,
                    p_usuario_id,
                    COALESCE(p_observacao, 'Encaminhado automaticamente'),
                    NOW()
                );

                -- Log de auditoria
                INSERT INTO processos_logauditoria (
                    processo_id,
                    usuario_id,
                    acao,
                    descricao,
                    data_hora
                )
                VALUES (
                    p_processo_id,
                    p_usuario_id,
                    'ENCAMINHAMENTO',
                    CONCAT('Encaminhado para etapa ID: ', p_proxima_etapa_id),
                    NOW()
                );
            END;
            $$ LANGUAGE plpgsql;
            """,
            reverse_sql="DROP FUNCTION IF EXISTS sp_encaminhar_processo(INT, INT, INT, TEXT);",
        ),
    ]
