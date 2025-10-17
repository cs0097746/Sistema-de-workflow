"""
Comando para corrigir ordens duplicadas de etapas
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from processos.models import Etapa, TemplateProcesso


class Command(BaseCommand):
    help = 'Corrige ordens duplicadas de etapas em templates'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Verificando etapas duplicadas...'))
        
        # Busca todos os templates
        templates = TemplateProcesso.objects.all()
        
        total_corrigidos = 0
        
        for template in templates:
            self.stdout.write(f'\nProcessando template: {template.nome}')
            
            # Busca todas as etapas do template ordenadas
            etapas = Etapa.objects.filter(template=template).order_by('ordem', 'id')
            
            if not etapas.exists():
                self.stdout.write(self.style.WARNING('  Sem etapas'))
                continue
            
            with transaction.atomic():
                # Renumera todas as etapas sequencialmente
                for idx, etapa in enumerate(etapas, start=1):
                    if etapa.ordem != idx:
                        self.stdout.write(
                            self.style.WARNING(
                                f'  Corrigindo: Etapa "{etapa.nome}" - Ordem {etapa.ordem} → {idx}'
                            )
                        )
                        etapa.ordem = idx
                        etapa.save(update_fields=['ordem'])
                        total_corrigidos += 1
                    else:
                        self.stdout.write(
                            self.style.SUCCESS(f'  OK: Etapa "{etapa.nome}" - Ordem {etapa.ordem}')
                        )
        
        if total_corrigidos > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✅ {total_corrigidos} etapa(s) corrigida(s) com sucesso!'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('\n✅ Nenhuma etapa precisou ser corrigida!')
            )
