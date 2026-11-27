from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from apps.people.models import Pessoa, RelacionamentoFamiliar
from apps.finance.models import ContaFinanceira, CentroCusto, PlanoContas


class Command(BaseCommand):
    help = "Cria grupos iniciais de acesso. Relatórios financeiros NÃO são concedidos por grupo."

    def handle(self, *args, **options):
        definicoes = {
            "Secretaria": [
                (Pessoa, ["view_pessoa", "add_pessoa", "change_pessoa"]),
                (RelacionamentoFamiliar, ["view_relacionamentofamiliar", "add_relacionamentofamiliar", "change_relacionamentofamiliar"]),
                (Pessoa, ["view_relatorio_aniversariantes", "view_relatorio_pessoas"]),
            ],
            "Tesouraria": [
                (ContaFinanceira, ["view_contafinanceira", "add_contafinanceira", "change_contafinanceira"]),
                (CentroCusto, ["view_centrocusto", "add_centrocusto", "change_centrocusto"]),
                (PlanoContas, ["view_planocontas", "add_planocontas", "change_planocontas"]),
            ],
            "Consulta": [
                (Pessoa, ["view_pessoa"]),
                (RelacionamentoFamiliar, ["view_relacionamentofamiliar"]),
                (ContaFinanceira, ["view_contafinanceira"]),
                (CentroCusto, ["view_centrocusto"]),
                (PlanoContas, ["view_planocontas"]),
            ],
        }

        for nome, itens in definicoes.items():
            grupo, _ = Group.objects.get_or_create(name=nome)
            permissoes = []
            for model, codenames in itens:
                ct = ContentType.objects.get_for_model(model)
                permissoes.extend(Permission.objects.filter(
                    content_type=ct, codename__in=codenames
                ))
            grupo.permissions.set(permissoes)
            self.stdout.write(self.style.SUCCESS(
                f"Grupo {nome}: {len(permissoes)} permissões configuradas."
            ))

        self.stdout.write(self.style.WARNING(
            "Atenção: permissões de relatórios financeiros não foram atribuídas a grupos. "
            "Conceda-as individualmente no usuário, em Usuários > Permissões do usuário."
        ))
