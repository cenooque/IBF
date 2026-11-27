from datetime import date

from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render
from django.utils import timezone

from apps.people.models import Pessoa


@login_required
@permission_required("people.view_relatorio_aniversariantes", raise_exception=True)
def aniversariantes(request):
    hoje = timezone.localdate()
    try:
        mes = int(request.GET.get("mes", hoje.month))
        if mes < 1 or mes > 12:
            raise ValueError
    except (TypeError, ValueError):
        mes = hoje.month

    pessoas = (
        Pessoa.objects.filter(ativo=True, data_nascimento__month=mes)
        .order_by("data_nascimento__day", "nome_completo")
    )
    return render(request, "reports/aniversariantes.html", {
        "pessoas": pessoas, "mes": mes, "hoje": hoje, "meses": [(1, "Janeiro"), (2, "Fevereiro"), (3, "Março"), (4, "Abril"), (5, "Maio"), (6, "Junho"), (7, "Julho"), (8, "Agosto"), (9, "Setembro"), (10, "Outubro"), (11, "Novembro"), (12, "Dezembro")],
    })


@login_required
@permission_required("people.view_relatorio_pessoas", raise_exception=True)
def pessoas(request):
    situacao = request.GET.get("situacao", "")
    qs = Pessoa.objects.filter(ativo=True)
    if situacao in dict(Pessoa.SituacaoIgreja.choices):
        qs = qs.filter(situacao_igreja=situacao)
    return render(request, "reports/pessoas.html", {
        "pessoas": qs.order_by("nome_completo"),
        "situacoes": Pessoa.SituacaoIgreja.choices,
        "situacao_selecionada": situacao,
    })


@login_required
@permission_required("finance.view_relatorio_financeiro", raise_exception=True)
def financeiro(request):
    # A página fica protegida desde já. Os relatórios com saldos e totais
    # serão ligados aos lançamentos depois que os modelos financeiros existirem.
    return render(request, "reports/financeiro_em_preparacao.html")
