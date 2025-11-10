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
        # pra retornar o histórico
        migrations.RunSQL(
            """
            CREATE OR REPLACE FUNCTION sp_criar_etapa(
                p_template_id INT,
                p_nome TEXT,
                p_ordem INT,
                p_responsavel_id INT,
                p_prazo_dias INT,
                p_descricao TEXT,
                p_usuario_criador_id INT
            )
            RETURNS VOID AS $$
            DECLARE
                v_perfil TEXT;
            BEGIN
                -- Verifica o perfil do usuário criador
                SELECT perfil INTO v_perfil
                FROM usuarios_usuario
                WHERE id = p_usuario_criador_id;

                IF v_perfil IS NULL THEN
                    RAISE EXCEPTION 'Usuário não encontrado (ID: %)', p_usuario_criador_id;
                END IF;

                IF v_perfil NOT IN ('ADMIN', 'GESTOR') THEN
                    RAISE EXCEPTION 'Usuário % não possui permissão para criar etapas (perfil: %)',
                        p_usuario_criador_id, v_perfil;
                END IF;

                -- Cria a nova etapa
                INSERT INTO processos_etapa (
                    template_id,
                    nome,
                    ordem,
                    responsavel_id,
                    prazo_dias,
                    descricao,
                    criado_em
                )
                VALUES (
                    p_template_id,
                    p_nome,
                    p_ordem,
                    p_responsavel_id,
                    p_prazo_dias,
                    p_descricao,
                    NOW()
                );

                -- Logzinho
                INSERT INTO processos_logauditoria (
                    processo_id,
                    usuario_id,
                    acao,
                    descricao,
                    data_hora
                )
                VALUES (
                    NULL,
                    p_usuario_criador_id,
                    'CRIACAO_ETAPA',
                    CONCAT('Etapa "', p_nome, '" criada no template ID: ', p_template_id),
                    NOW()
                );

            END;
            $$ LANGUAGE plpgsql;
            """,
            reverse_sql="DROP FUNCTION IF EXISTS fn_historico_processo(INT);",
        ),
        # atualizar etapa dos processos;
        migrations.RunSQL(
            """
            CREATE OR REPLACE FUNCTION sp_atualizar_etapa(
                p_etapa_id INT,
                p_nome TEXT,
                p_ordem INT,
                p_responsavel_id INT,
                p_prazo_dias INT,
                p_descricao TEXT,
                p_usuario_id INT
            )
            RETURNS VOID AS $$
            DECLARE
                v_perfil TEXT;
            BEGIN
                -- validação de role
                SELECT perfil INTO v_perfil FROM usuarios_usuario WHERE id = p_usuario_id;
                IF v_perfil NOT IN ('ADMIN', 'GESTOR') THEN
                    RAISE EXCEPTION 'Usuário % não possui permissão para editar etapas (perfil: %)', p_usuario_id, v_perfil;
                END IF;

                -- Atualiza se ta valido etapa
                UPDATE processos_etapa
                SET
                    nome = p_nome,
                    ordem = p_ordem,
                    responsavel_id = p_responsavel_id,
                    prazo_dias = p_prazo_dias,
                    descricao = p_descricao,
                    data_atualizacao = NOW()
                WHERE id = p_etapa_id;

            END;
            $$ LANGUAGE plpgsql;
            """,
            reverse_sql="DROP FUNCTION IF EXISTS sp_atualizar_etapa(INT, TEXT, INT, INT, INT, TEXT, INT);",
        ),
        migrations.RunSQL(
            """
            CREATE OR REPLACE FUNCTION fn_pode_visualizar_processo(
                p_processo_id INT,
                p_usuario_id INT
            )
            RETURNS BOOLEAN AS $$
            DECLARE
                v_perfil TEXT;
                v_existe BOOLEAN;
            BEGIN
                -- Pega o perfil do usuário
                SELECT perfil INTO v_perfil FROM usuarios_usuario WHERE id = p_usuario_id;

                -- Admins e Gestores podem ver tudo
                IF v_perfil IN ('ADMIN', 'GESTOR') THEN
                    RETURN TRUE;
                END IF;

                -- Verifica se o usuário está vinculado ao processo
                SELECT TRUE INTO v_existe
                FROM processos_processoinstancia p
                WHERE p.id = p_processo_id
                AND (
                    p.criado_por_id = p_usuario_id OR
                    p.usuario_atual_id = p_usuario_id OR
                    EXISTS (
                        SELECT 1 FROM processos_etapaexecucao e
                        WHERE e.processo_id = p_processo_id
                        AND e.executado_por_id = p_usuario_id
                    )
                )
                LIMIT 1;

                RETURN COALESCE(v_existe, FALSE);
            END;
            $$ LANGUAGE plpgsql;

            """,
            reverse_sql="DROP FUNCTION IF EXISTS fn_pode_visualizar_processo( INT, INT);",
        ),
    ]
