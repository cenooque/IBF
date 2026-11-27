from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404, redirect, render

from apps.core.views import usuario_pode_tela

from .forms import CentroCustoForm, PlanoContasForm
from .models import CentroCusto, PlanoContas

TELA_CENTRO_CUSTO = "CENTRO_CUSTO"
TELA_PLANO_CONTAS = "PLANO_CONTAS"


def _validar_permissao_gravacao(user, codigo_tela: str, instancia, msg_alterar: str, msg_incluir: str) -> None:
    if instancia:
        if not usuario_pode_tela(user, codigo_tela, "alterar"):
            raise PermissionDenied(msg_alterar)
    elif not usuario_pode_tela(user, codigo_tela, "incluir"):
        raise PermissionDenied(msg_incluir)


def _aplicar_erros_validacao(form, exc: ValidationError) -> None:
    if hasattr(exc, "message_dict") and exc.message_dict:
        for campo, erros in exc.message_dict.items():
            destino = None if campo == "__all__" else campo
            for erro in erros:
                form.add_error(destino, erro)
        return
    for erro in exc.messages:
        form.add_error(None, erro)


def _gravar_formulario(form):
    objeto = form.save(commit=False)
    objeto.full_clean()
    objeto.save()
    form.save_m2m()
    return objeto


@login_required
def centro_custo_form(request, pk=None):
    if not usuario_pode_tela(request.user, TELA_CENTRO_CUSTO, "consultar"):
        raise PermissionDenied("Sem permissão para consultar centros de custo.")

    instancia = get_object_or_404(CentroCusto, pk=pk) if pk else None

    if request.method == "POST":
        _validar_permissao_gravacao(
            request.user,
            TELA_CENTRO_CUSTO,
            instancia,
            "Sem permissão para alterar centros de custo.",
            "Sem permissão para incluir centros de custo.",
        )
        form = CentroCustoForm(request.POST, instance=instancia)
        if form.is_valid():
            try:
                objeto = _gravar_formulario(form)
            except ValidationError as exc:
                _aplicar_erros_validacao(form, exc)
            else:
                messages.success(request, "Centro de custo gravado com sucesso.")
                return redirect("finance:centro_custo_editar", pk=objeto.pk)
    else:
        form = CentroCustoForm(instance=instancia)

    return render(
        request,
        "finance/cadastro_step.html",
        {
            "titulo_pagina": "Cadastro de Centro de Custo — IBF",
            "titulo_tela": "Cadastro de Centro de Custo",
            "subtitulo_ajuda": "Preencha os dados e clique em gravar para realizar o cadastro ou alteração do Centro de Custo.",
            "form": form,
            "instancia": instancia,
            "tela_codigo": TELA_CENTRO_CUSTO,
            "url_voltar": "/",
            "url_novo": "finance:centro_custo",
        },
    )


@login_required
def plano_contas_form(request, pk=None):
    if not usuario_pode_tela(request.user, TELA_PLANO_CONTAS, "consultar"):
        raise PermissionDenied("Sem permissão para consultar planos de contas.")

    instancia = get_object_or_404(PlanoContas, pk=pk) if pk else None

    if request.method == "POST":
        _validar_permissao_gravacao(
            request.user,
            TELA_PLANO_CONTAS,
            instancia,
            "Sem permissão para alterar planos de contas.",
            "Sem permissão para incluir planos de contas.",
        )
        form = PlanoContasForm(request.POST, instance=instancia)
        if form.is_valid():
            try:
                objeto = _gravar_formulario(form)
            except ValidationError as exc:
                _aplicar_erros_validacao(form, exc)
            else:
                messages.success(request, "Plano de contas gravado com sucesso.")
                return redirect("finance:plano_contas_editar", pk=objeto.pk)
    else:
        form = PlanoContasForm(instance=instancia)

    return render(
        request,
        "finance/cadastro_step.html",
        {
            "titulo_pagina": "Cadastro de Plano de Contas — IBF",
            "titulo_tela": "Cadastro de Plano de Contas",
            "subtitulo_ajuda": "Preencha os dados e clique em gravar para realizar o cadastro ou alteração do Plano de Contas.",
            "form": form,
            "instancia": instancia,
            "tela_codigo": TELA_PLANO_CONTAS,
            "url_voltar": "/",
            "url_novo": "finance:plano_contas",
        },
    )
