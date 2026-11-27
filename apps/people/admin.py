from django.contrib import admin
from .models import Cargo, Pessoa


@admin.register(Cargo)
class CargoAdmin(admin.ModelAdmin):
    list_display = ("id", "nome", "ativo")
    list_filter = ("ativo",)
    search_fields = ("nome",)
    ordering = ("nome",)


@admin.register(Pessoa)
class PessoaAdmin(admin.ModelAdmin):
    list_display = (
        "nome_completo",
        "cargo",
        "ano_vigente",
        "eh_crianca",
        "conjuge",
        "sexo",
        "situacao_igreja",
        "dizimista",
        "telefone",
        "cidade",
        "ativo",
    )
    list_filter = (
        "eh_crianca",
        "dizimista",
        "cargo",
        "sexo",
        "estado_civil",
        "situacao_igreja",
        "ativo",
    )
    search_fields = ("nome_completo", "telefone", "email", "cidade")
    ordering = ("nome_completo",)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    ("nome_completo", "dizimista", "ativo", "eh_crianca"),
                ),
            },
        ),
        (
            "Vínculos familiares",
            {
                "fields": ("conjuge", "pai", "mae"),
            },
        ),
        (
            "Dados pessoais",
            {
                "fields": (
                    "sexo",
                    "data_nascimento",
                    "data_batismo",
                    "estado_civil",
                    "situacao_igreja",
                    "cargo",
                    "ano_vigente",
                )
            },
        ),
        (
            "Contato e endereço",
            {
                "fields": (
                    "telefone",
                    "email",
                    "endereco",
                    "bairro",
                    "cidade",
                    "estado",
                    "cep",
                )
            },
        ),
        (
            "Outras informações",
            {"fields": ("observacoes",)},
        ),
    )