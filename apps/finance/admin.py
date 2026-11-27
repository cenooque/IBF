from django.contrib import admin
from .models import (
    CentroCusto,
    ContaFinanceira,
    ContaPagar,
    ContaReceber,
    Fornecedor,
    GrupoCentroCusto,
    PlanoContas,
)


@admin.register(GrupoCentroCusto)
class GrupoCentroCustoAdmin(admin.ModelAdmin):
    list_display = ("codigo", "descricao", "ativo")
    list_filter = ("ativo",)
    search_fields = ("codigo", "descricao")
    ordering = ("descricao",)


@admin.register(CentroCusto)
class CentroCustoAdmin(admin.ModelAdmin):
    list_display = (
        "codigo",
        "descricao",
        "tipo",
        "grupo",
        "classificacao_custo",
        "aceita_contas_pagar",
        "aceita_contas_receber",
        "ativo",
        "produtivo",
    )
    list_filter = (
        "ativo",
        "tipo",
        "classificacao_custo",
        "aceita_contas_pagar",
        "aceita_contas_receber",
        "produtivo",
        "grupo",
    )
    search_fields = ("codigo", "descricao", "grupo__descricao")
    autocomplete_fields = ("grupo",)
    radio_fields = {"classificacao_custo": admin.HORIZONTAL}

    fieldsets = (
        (
            "Geral",
            {
                "fields": (
                    ("codigo", "tipo"),
                    ("descricao", "grupo"),
                    "classificacao_custo",
                )
            },
        ),
        (
            "Vínculo Financeiro e Status",
            {
                "fields": (
                    ("aceita_contas_pagar", "aceita_contas_receber"),
                    ("ativo", "produtivo"),
                )
            },
        ),
        (
            "Observações",
            {
                "fields": ("observacao",),
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        obj.full_clean()
        super().save_model(request, obj, form, change)


@admin.register(ContaFinanceira)
class ContaFinanceiraAdmin(admin.ModelAdmin):
    list_display = ("nome", "tipo", "banco", "saldo_inicial", "ativo")
    list_filter = ("tipo", "ativo")
    search_fields = ("nome", "banco", "numero_conta")


@admin.register(PlanoContas)
class PlanoContasAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nome", "natureza", "tipo", "conta_pai", "ativo")
    list_filter = ("natureza", "tipo", "ativo")
    search_fields = ("codigo", "nome")
    ordering = ("codigo",)


@admin.register(Fornecedor)
class FornecedorAdmin(admin.ModelAdmin):
    list_display = ("id", "nome_razao", "tipo_pessoa", "cpf_cnpj", "telefone", "pessoa", "ativo")
    list_filter = ("tipo_pessoa", "ativo")
    search_fields = ("nome_razao", "nome_fantasia", "cpf_cnpj", "pessoa__nome_completo")
    autocomplete_fields = ("pessoa",)


@admin.register(ContaReceber)
class ContaReceberAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "status",
        "descricao",
        "pessoa",
        "valor",
        "data_vencimento",
        "data_recebimento",
        "conta_financeira",
    )
    list_filter = ("status", "forma_recebimento", "conta_financeira", "centro_custo")
    search_fields = (
        "descricao",
        "numero_documento",
        "pessoa__nome_completo",
        "fornecedor__nome_razao",
    )
    autocomplete_fields = ("pessoa", "fornecedor")
    date_hierarchy = "data_vencimento"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "centro_custo":
            kwargs["queryset"] = CentroCusto.objects.filter(
                ativo=True,
                tipo=CentroCusto.Tipo.ANALITICO,
                aceita_contas_receber=True,
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        obj.full_clean()
        super().save_model(request, obj, form, change)


@admin.register(ContaPagar)
class ContaPagarAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "status",
        "descricao",
        "fornecedor",
        "pessoa",
        "valor",
        "data_vencimento",
        "data_pagamento",
        "conta_financeira",
    )
    list_filter = ("status", "forma_pagamento", "conta_financeira", "centro_custo")
    search_fields = (
        "descricao",
        "numero_documento",
        "fornecedor__nome_razao",
        "pessoa__nome_completo",
    )
    autocomplete_fields = ("fornecedor", "pessoa")
    date_hierarchy = "data_vencimento"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "centro_custo":
            kwargs["queryset"] = CentroCusto.objects.filter(
                ativo=True,
                tipo=CentroCusto.Tipo.ANALITICO,
                aceita_contas_pagar=True,
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        obj.full_clean()
        super().save_model(request, obj, form, change)