from django import forms
from django.db.models import Q

from .models import CentroCusto, GrupoCentroCusto, PlanoContas


def _definir_rotulo_vazio(campo, rotulo="Selecione uma opção"):
    """empty_label existe só em ModelChoiceField.

    ChoiceField e TypedChoiceField (usados nos choices dos models) não têm
    esse atributo; acessá-lo gera AttributeError.
    """
    if isinstance(campo, forms.ModelChoiceField):
        campo.empty_label = rotulo


def _incluir_opcao_em_branco(campo, rotulo="Selecione uma opção"):
    if isinstance(campo, forms.ModelChoiceField):
        return
    if not isinstance(campo, forms.ChoiceField):
        return
    if isinstance(campo.widget, forms.RadioSelect):
        return
    opcoes = list(campo.choices)
    if any(str(valor) == "" for valor, _rotulo in opcoes):
        return
    campo.choices = [("", rotulo), *opcoes]


class CentroCustoForm(forms.ModelForm):
    class Meta:
        model = CentroCusto
        fields = [
            "codigo",
            "descricao",
            "tipo",
            "grupo",
            "classificacao_custo",
            "aceita_contas_pagar",
            "aceita_contas_receber",
            "ativo",
            "produtivo",
            "observacao",
        ]
        widgets = {
            "codigo": forms.TextInput(attrs={"class": "form-control", "placeholder": "1"}),
            "descricao": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Descrição"}
            ),
            "tipo": forms.Select(attrs={"class": "form-select"}),
            "grupo": forms.Select(attrs={"class": "form-select"}),
            "classificacao_custo": forms.RadioSelect(attrs={"class": "form-check-input"}),
            "aceita_contas_pagar": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "aceita_contas_receber": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "ativo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "produtivo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "observacao": forms.Textarea(
                attrs={"class": "form-control", "rows": 4, "placeholder": "Observação"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        grupos = GrupoCentroCusto.objects.filter(ativo=True)
        if self.instance.pk and self.instance.grupo_id:
            grupos = GrupoCentroCusto.objects.filter(
                Q(ativo=True) | Q(pk=self.instance.grupo_id)
            )
        self.fields["grupo"].queryset = grupos.order_by("descricao", "id")
        _definir_rotulo_vazio(self.fields["grupo"])
        _incluir_opcao_em_branco(self.fields["tipo"])

        if not self.instance.pk and not self.initial.get("codigo"):
            ultimo = CentroCusto.objects.order_by("-pk").first()
            proximo = (ultimo.pk + 1) if ultimo else 1
            self.fields["codigo"].initial = str(proximo)


class PlanoContasForm(forms.ModelForm):
    class Meta:
        model = PlanoContas
        fields = [
            "codigo",
            "nome",
            "natureza",
            "tipo",
            "conta_pai",
            "ativo",
        ]
        widgets = {
            "codigo": forms.TextInput(attrs={"class": "form-control", "placeholder": "1.01"}),
            "nome": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Nome da conta"}
            ),
            "natureza": forms.Select(attrs={"class": "form-select"}),
            "tipo": forms.Select(attrs={"class": "form-select"}),
            "conta_pai": forms.Select(attrs={"class": "form-select"}),
            "ativo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        contas = PlanoContas.objects.all()
        if self.instance.pk:
            contas = contas.exclude(pk=self.instance.pk)
            if self.instance.conta_pai_id:
                contas = PlanoContas.objects.filter(
                    Q(pk=self.instance.conta_pai_id) | Q(ativo=True)
                ).exclude(pk=self.instance.pk)
            else:
                contas = contas.filter(ativo=True)
        else:
            contas = contas.filter(ativo=True)
        self.fields["conta_pai"].queryset = contas.order_by("codigo")
        _definir_rotulo_vazio(self.fields["conta_pai"])
        _incluir_opcao_em_branco(self.fields["natureza"])
        _incluir_opcao_em_branco(self.fields["tipo"])

        if not self.instance.pk and not self.initial.get("codigo"):
            ultimo = PlanoContas.objects.order_by("-pk").first()
            proximo = (ultimo.pk + 1) if ultimo else 1
            self.fields["codigo"].initial = str(proximo)
