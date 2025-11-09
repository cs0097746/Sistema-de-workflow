# processos/services.py
from django.db import connection, transaction
import sys
from django.core.management.base import BaseCommand
import logging

logger = logging.getLogger(__name__)

def run_procedure(name: str, params: list):
    """Executa um procedure com segurança e logging."""
    with connection.cursor() as cursor, transaction.atomic():
        placeholders = ', '.join(['%s'] * len(params))
        sql = f"CALL {name}({placeholders});"
        logger.debug(f"Executando: {sql} {params}")
        cursor.execute(sql, params)

def encaminhar_processo(processo_id: int, proxima_etapa_id: int, usuario_id: int, observacao: str | None = None):
    """
    Chama a stored procedure sp_encaminhar_processo no PostgreSQL.

    Args:
        processo_id: ID do processo
        proxima_etapa_id: ID da próxima etapa
        usuario_id: ID do usuário que encaminha
        observacao: observação opcional
    """
    sys.stdout.write(f"aq chamamos a procedure({processo_id}, {proxima_etapa_id}, {usuario_id}, '{observacao}')")
    with connection.cursor() as cursor:
        cursor.callproc(
            'sp_encaminhar_processo',
            [processo_id, proxima_etapa_id, usuario_id, observacao]
        )
def finalizar_processo(processo_id: int):
    run_procedure('sp_finalizar_processo', [processo_id])

def cancelar_processo(processo_id: int, usuario_id: int):
    run_procedure('sp_cancelar_processo', [processo_id, usuario_id])
