from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render

from .forms import UsuarioCadastroForm
from .models import PermissaoTela

User = get_user_model()

TELAS_SISTEMA = [
    {
        "codigo_tela": "PAINEL_GERAL",
        "nome_tela": "PAINEL_GERAL",
        "app_label": "core",
        "model_name": "permissaotela",
    },
    {
        "codigo_tela": "PESSOAS_CADASTRO",
        "nome_tela": "PESSOAS_CADASTRO",
        "app_label": "people",
        "model_name": "pessoa",
    },
    {
        "codigo_tela": "CARGOS_CADASTRO",
        "nome_tela": "CARGOS_CADASTRO",
        "app_label": "people",
        "model_name": "cargo",
    },
    {
        "codigo_tela": "CONTAS_RECEBER",
        "nome_tela": "CONTAS_RECEBER",
        "app_label": "finance",
        "model_name": "contareceber",
    },
    {
        "codigo_tela": "CONTAS_PAGAR",
        "nome_tela": "CONTAS_PAGAR",
        "app_label": "finance",
        "model_name": "contapagar",
    },
    {
        "codigo_tela": "FORNECEDORES",
        "nome_tela": "FORNECEDORES",
        "app_label": "finance",
        "model_name": "fornecedor",
    },
    {
        "codigo_tela": "CENTRO_CUSTO",
        "nome_tela": "CENTRO_CUSTO",
        "app_label": "finance",
        "model_name": "centrocusto",
    },
    {
        "codigo_tela": "PLANO_CONTAS",
        "nome_tela": "PLANO_CONTAS",
        "app_label": "finance",
        "model_name": "planocontas",
    },
    {
        "codigo_tela": "USUARIOS_CADASTRO",
        "nome_tela": "USUARIOS_CADASTRO",
        "app_label": "auth",
        "model_name": "user",
    },
    {
        "codigo_tela": "LIBERACAO_ACESSOS",
        "nome_tela": "LIBERACAO_ACESSOS",
        "app_label": "core",
        "model_name": "permissaotela",
    },
]


def usuario_pode_tela(user, codigo_tela: str, acao: str = "consultar") -> bool:
    """
    acao: 'consultar' | 'alterar' | 'excluir' | 'incluir'
    Retorna True para superuser ou quando PermissaoTela estiver marcada para o usuário.
    """
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True

    campo_map = {
        "consultar": "pode_consultar",
        "alterar": "pode_alterar",
        "excluir": "pode_excluir",
        "incluir": "pode_incluir",
    }
    campo = campo_map.get(acao, "pode_consultar")
    return PermissaoTela.objects.filter(
        usuario=user,
        codigo_tela=codigo_tela,
        **{campo: True},
    ).exists()


def _is_gestor(user):
    return user.is_authenticated and (user.is_superuser or user.is_staff)


def _garantir_linhas_usuario(usuario):
    existentes = set(
        PermissaoTela.objects.filter(usuario=usuario).values_list("codigo_tela", flat=True)
    )
    novos = []
    for tela in TELAS_SISTEMA:
        if tela["codigo_tela"] not in existentes:
            novos.append(
                PermissaoTela(
                    usuario=usuario,
                    codigo_tela=tela["codigo_tela"],
                    nome_tela=tela["nome_tela"],
                    app_label=tela["app_label"],
                    model_name=tela["model_name"],
                    pode_consultar=usuario.is_superuser,
                    pode_alterar=usuario.is_superuser,
                    pode_excluir=usuario.is_superuser,
                    pode_incluir=usuario.is_superuser,
                )
            )
    if novos:
        PermissaoTela.objects.bulk_create(novos)


@login_required
def painel_erp(request):
    contexto = {
        "titulo_pagina": "Painel de Gestão — IBF",
        "cards": [
            {"titulo": "Total de Pessoas", "valor": 0, "destaque": "info"},
            {"titulo": "Contas a Receber (Aberto)", "valor": "R$ 0,00", "destaque": "sucesso"},
            {"titulo": "Contas a Pagar (Aberto)", "valor": "R$ 0,00", "destaque": "alerta"},
        ],
    }

    try:
        from apps.people.models import Pessoa

        contexto["cards"][0]["valor"] = Pessoa.objects.count()
    except Exception:
        pass

    try:
        from apps.finance.models import ContaPagar, ContaReceber

        total_receber = (
            ContaReceber.objects.filter(status="PENDENTE").aggregate(s=Sum("valor"))["s"] or 0
        )
        total_pagar = (
            ContaPagar.objects.filter(status="PENDENTE").aggregate(s=Sum("valor"))["s"] or 0
        )
        contexto["cards"][1]["valor"] = (
            f"R$ {total_receber:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )
        contexto["cards"][2]["valor"] = (
            f"R$ {total_pagar:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )
    except Exception:
        pass

    return render(request, "core/painel.html", contexto)


@login_required
@user_passes_test(_is_gestor)
def liberacao_acessos(request):
    usuarios = User.objects.all().order_by("id")
    usuario_id = request.GET.get("usuario") or request.POST.get("usuario_id")

    if usuario_id and str(usuario_id).isdigit():
        usuario_selecionado = get_object_or_404(User, pk=int(usuario_id))
    else:
        usuario_selecionado = usuarios.first()

    if usuario_selecionado:
        _garantir_linhas_usuario(usuario_selecionado)

    if request.method == "POST" and usuario_selecionado:
        acao = request.POST.get("acao", "confirmar")

        if acao == "copiar":
            origem_id = request.POST.get("origem_usuario_id")
            if origem_id and origem_id.isdigit():
                origem = get_object_or_404(User, pk=int(origem_id))
                _garantir_linhas_usuario(origem)
                mapa_origem = {
                    p.codigo_tela: p for p in PermissaoTela.objects.filter(usuario=origem)
                }
                for item in PermissaoTela.objects.filter(usuario=usuario_selecionado):
                    src = mapa_origem.get(item.codigo_tela)
                    if src:
                        item.pode_consultar = src.pode_consultar
                        item.pode_alterar = src.pode_alterar
                        item.pode_excluir = src.pode_excluir
                        item.pode_incluir = src.pode_incluir
                        item.save()
                        item.sincronizar_permissoes_django()
            return redirect(f"/acessos/?usuario={usuario_selecionado.pk}")

        itens = PermissaoTela.objects.filter(usuario=usuario_selecionado)
        for item in itens:
            item.pode_consultar = f"consultar_{item.pk}" in request.POST
            item.pode_alterar = f"alterar_{item.pk}" in request.POST
            item.pode_excluir = f"excluir_{item.pk}" in request.POST
            item.pode_incluir = f"incluir_{item.pk}" in request.POST
            item.save()
            item.sincronizar_permissoes_django()

        return redirect(f"/acessos/?usuario={usuario_selecionado.pk}")

    pesquisa = (request.GET.get("q") or "").strip()
    permissoes = PermissaoTela.objects.none()
    if usuario_selecionado:
        permissoes = PermissaoTela.objects.filter(usuario=usuario_selecionado).order_by("nome_tela")
        if pesquisa:
            permissoes = permissoes.filter(
                Q(nome_tela__icontains=pesquisa) | Q(codigo_tela__icontains=pesquisa)
            )

    return render(
        request,
        "core/liberacao_acessos.html",
        {
            "titulo_pagina": "Liberação de Acessos — IBF",
            "usuarios": usuarios,
            "usuario_selecionado": usuario_selecionado,
            "permissoes": permissoes,
            "pesquisa": pesquisa,
            "total_registros": permissoes.count(),
        },
    )


@login_required
@user_passes_test(_is_gestor)
def usuario_lista(request):
    busca = (request.GET.get("q") or "").strip()
    usuarios = User.objects.all().order_by("id")
    if busca:
        usuarios = usuarios.filter(
            Q(username__icontains=busca)
            | Q(first_name__icontains=busca)
            | Q(last_name__icontains=busca)
            | Q(email__icontains=busca)
        )
    return render(
        request,
        "core/usuario_lista.html",
        {
            "titulo_pagina": "Usuários — IBF",
            "usuarios": usuarios,
            "busca": busca,
        },
    )


@login_required
@user_passes_test(_is_gestor)
def usuario_form(request, pk=None):
    usuario_obj = get_object_or_404(User, pk=pk) if pk else None
    if request.method == "POST":
        form = UsuarioCadastroForm(request.POST, instance=usuario_obj)
        if form.is_valid():
            salvo = form.save()
            _garantir_linhas_usuario(salvo)
            return redirect("core:usuario_lista")
    else:
        form = UsuarioCadastroForm(instance=usuario_obj)

    return render(
        request,
        "core/usuario_form.html",
        {
            "titulo_pagina": f"Editar Usuário #{usuario_obj.pk} — IBF" if usuario_obj else "Novo Usuário — IBF",
            "form": form,
            "usuario_obj": usuario_obj,
        },
    )