"""
Comando para corrigir números de processo duplicados
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from processos.models import ProcessoInstancia


class Command(BaseCommand):
    help = 'Corrige números de processo duplicados no banco de dados'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Verificando processos duplicados...'))
        
        # Busca todos os processos ordenados por data
        processos = ProcessoInstancia.objects.all().order_by('data_criacao')
        
        # Agrupa por ano
        processos_por_ano = {}
        for processo in processos:
            ano = processo.data_criacao.year
            if ano not in processos_por_ano:
                processos_por_ano[ano] = []
            processos_por_ano[ano].append(processo)
        
        total_corrigidos = 0
        
        with transaction.atomic():
            for ano, lista_processos in processos_por_ano.items():
                self.stdout.write(f'\nProcessando ano {ano}...')
                
                # Renumera todos os processos do ano
                for idx, processo in enumerate(lista_processos, start=1):
                    novo_numero = f"{idx:06d}/{ano}"
                    
                    if processo.numero_processo != novo_numero:
                        self.stdout.write(
                            self.style.WARNING(
                                f'  Corrigindo: {processo.numero_processo} → {novo_numero}'
                            )
                        )
                        processo.numero_processo = novo_numero
                        processo.save(update_fields=['numero_processo'])
                        total_corrigidos += 1
                    else:
                        self.stdout.write(
                            self.style.SUCCESS(f'  OK: {processo.numero_processo}')
                        )
        
        if total_corrigidos > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✅ {total_corrigidos} processo(s) corrigido(s) com sucesso!'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('\n✅ Nenhum processo precisou ser corrigido!')
            )
