from io import BytesIO
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from openpyxl import Workbook
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from .forms import CargoForm, PessoaForm
from .models import Cargo, Pessoa


def _filtrar_pessoas(request):
    qs = Pessoa.objects.select_related("cargo", "conjuge", "pai", "mae").all()

    q = (request.GET.get("q") or "").strip()
    dizimista = request.GET.get("dizimista") or ""
    ativo = request.GET.get("ativo") or ""
    cargo_id = (request.GET.get("cargo") or "").strip()
    crianca = request.GET.get("crianca") or ""

    if q:
        filtros = Q(nome_completo__icontains=q)
        if q.isdigit():
            filtros |= Q(id=int(q))
        for campo in ("telefone", "email"):
            if hasattr(Pessoa, campo):
                filtros |= Q(**{f"{campo}__icontains": q})
        qs = qs.filter(filtros)

    if dizimista == "1":
        qs = qs.filter(dizimista=True)
    elif dizimista == "0":
        qs = qs.filter(dizimista=False)

    if ativo == "1":
        qs = qs.filter(ativo=True)
    elif ativo == "0":
        qs = qs.filter(ativo=False)

    if cargo_id.isdigit():
        qs = qs.filter(cargo_id=int(cargo_id))

    if crianca == "1":
        qs = qs.filter(eh_crianca=True)
    elif crianca == "0":
        qs = qs.filter(eh_crianca=False)

    return qs.order_by("id")


@login_required
@permission_required("people.view_pessoa", raise_exception=True)
def pessoa_lista(request):
    pessoas = _filtrar_pessoas(request)
    total_pessoas = Pessoa.objects.count()
    total_dizimistas = Pessoa.objects.filter(dizimista=True).count()
    total_ativos = Pessoa.objects.filter(ativo=True).count()
    cargos = Cargo.objects.filter(ativo=True).order_by("nome")

    contexto = {
        "titulo_pagina": "Pessoas — IBF",
        "pessoas": pessoas,
        "cargos": cargos,
        "q": request.GET.get("q", ""),
        "dizimista": request.GET.get("dizimista", ""),
        "ativo": request.GET.get("ativo", ""),
        "cargo_id": (request.GET.get("cargo") or "").strip(),
        "crianca": request.GET.get("crianca", ""),
        "querystring": request.GET.urlencode(),
        "cards": [
            {"titulo": "Total de Pessoas", "valor": total_pessoas, "destaque": "info"},
            {"titulo": "Dizimistas", "valor": total_dizimistas, "destaque": "sucesso"},
            {"titulo": "Ativos", "valor": total_ativos, "destaque": "alerta"},
        ],
    }
    return render(request, "people/pessoa_lista.html", contexto)


@login_required
@permission_required("people.add_pessoa", raise_exception=True)
def pessoa_criar(request):
    if request.method == "POST":
        form = PessoaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("people:lista")
    else:
        form = PessoaForm()

    return render(
        request,
        "people/pessoa_form.html",
        {"titulo_pagina": "Cadastro de Pessoa", "form": form},
    )


@login_required
@permission_required("people.change_pessoa", raise_exception=True)
def pessoa_editar(request, pk):
    pessoa = get_object_or_404(Pessoa, pk=pk)
    if request.method == "POST":
        form = PessoaForm(request.POST, request.FILES, instance=pessoa)
        if form.is_valid():
            obj = form.save(commit=False)
            if request.POST.get("limpar_foto") == "1" and "foto" not in request.FILES:
                if obj.foto:
                    obj.foto.delete(save=False)
                obj.foto = None
            obj.save()
            form.save_m2m()
            return redirect("people:lista")
    else:
        form = PessoaForm(instance=pessoa)

    filhos = Pessoa.objects.filter(
        Q(pai=pessoa) | Q(mae=pessoa)
    ).order_by("nome_completo")

    return render(
        request,
        "people/pessoa_form.html",
        {
            "titulo_pagina": "Cadastro de Pessoa",
            "form": form,
            "pessoa": pessoa,
            "filhos": filhos,
        },
    )


@login_required
@permission_required("people.delete_pessoa", raise_exception=True)
def pessoa_excluir(request, pk):
    pessoa = get_object_or_404(Pessoa, pk=pk)
    if request.method == "POST":
        pessoa.delete()
        return redirect("people:lista")
    return redirect("people:editar", pk=pessoa.pk)


@login_required
@permission_required("people.delete_pessoa", raise_exception=True)
def pessoa_excluir_lote(request):
    if request.method == "POST":
        ids_raw = request.POST.getlist("selecionados")
        ids = [int(i) for i in ids_raw if i.isdigit()]
        if ids:
            Pessoa.objects.filter(pk__in=ids).delete()
    return redirect("people:lista")


@login_required
@permission_required("people.view_pessoa", raise_exception=True)
def pessoa_exportar_excel(request):
    pessoas = _filtrar_pessoas(request)

    wb = Workbook()
    ws = wb.active
    ws.title = "Pessoas"

    cabecalhos = [
        "ID",
        "Nome",
        "Telefone",
        "Endereço",
        "Bairro",
        "Estado",
        "Data Nascimento",
        "Cargo",
        "Criança",
        "Dizimista",
        "Ativo",
    ]
    ws.append(cabecalhos)

    for p in pessoas:
        nasc = p.data_nascimento.strftime("%d/%m/%Y") if p.data_nascimento else ""
        cargo_txt = p.cargo.nome if p.cargo else ""
        ws.append([
            p.id,
            p.nome_completo,
            p.telefone or "",
            p.endereco or "",
            p.bairro or "",
            p.estado or "",
            nasc,
            cargo_txt,
            "Sim" if p.eh_crianca else "Não",
            "Sim" if p.dizimista else "Não",
            "Sim" if p.ativo else "Não",
        ])

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    response = HttpResponse(
        buffer.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = 'attachment; filename="pessoas_ibf.xlsx"'
    return response


@login_required
@permission_required("people.view_pessoa", raise_exception=True)
def pessoa_exportar_pdf(request):
    pessoas = _filtrar_pessoas(request)

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), topMargin=24, bottomMargin=24)
    styles = getSampleStyleSheet()
    elementos = [
        Paragraph("Relatório de Pessoas — IBF", styles["Title"]),
        Spacer(1, 12),
    ]

    dados = [[
        "ID",
        "Nome",
        "Telefone",
        "Endereço",
        "Bairro",
        "UF",
        "Nascimento",
        "Cargo",
        "Criança",
        "Dizimista",
        "Ativo",
    ]]
    for p in pessoas:
        nasc = p.data_nascimento.strftime("%d/%m/%Y") if p.data_nascimento else "-"
        cargo_txt = p.cargo.nome if p.cargo else "-"
        dados.append([
            str(p.id),
            p.nome_completo,
            p.telefone or "-",
            p.endereco or "-",
            p.bairro or "-",
            p.estado or "-",
            nasc,
            cargo_txt,
            "Sim" if p.eh_crianca else "Não",
            "Sim" if p.dizimista else "Não",
            "Sim" if p.ativo else "Não",
        ])

    tabela = Table(dados, repeatRows=1)
    tabela.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2d3748")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7fafc")]),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("PADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    elementos.append(tabela)
    doc.build(elementos)
    buffer.seek(0)

    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="pessoas_ibf.pdf"'
    return response


@login_required
@permission_required("people.view_cargo", raise_exception=True)
def cargo_lista(request):
    busca = (request.GET.get("q") or "").strip()
    cargos = Cargo.objects.all().order_by("id")

    if busca:
        filtros = Q(nome__icontains=busca) | Q(observacao__icontains=busca)
        if busca.isdigit():
            filtros |= Q(id=int(busca)) | Q(ano_vigente_de=int(busca)) | Q(ano_vigente_ate=int(busca))
        cargos = cargos.filter(filtros)

    return render(
        request,
        "people/cargo_lista.html",
        {
            "titulo_pagina": "Cargos — IBF",
            "cargos": cargos,
            "busca": busca,
        },
    )


@login_required
@permission_required("people.add_cargo", raise_exception=True)
def cargo_criar(request):
    if request.method == "POST":
        form = CargoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("people:cargo_lista")
    else:
        form = CargoForm()

    return render(
        request,
        "people/cargo_form.html",
        {
            "titulo_pagina": "Novo Cargo — IBF",
            "form": form,
            "cargo_obj": None,
        },
    )


@login_required
@permission_required("people.change_cargo", raise_exception=True)
def cargo_editar(request, pk):
    cargo = get_object_or_404(Cargo, pk=pk)
    if request.method == "POST":
        form = CargoForm(request.POST, instance=cargo)
        if form.is_valid():
            form.save()
            return redirect("people:cargo_lista")
    else:
        form = CargoForm(instance=cargo)

    return render(
        request,
        "people/cargo_form.html",
        {
            "titulo_pagina": f"Editar Cargo #{cargo.pk} — IBF",
            "form": form,
            "cargo_obj": cargo,
        },
    )