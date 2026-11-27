from django import forms
from .models import Cargo, Pessoa


class PessoaForm(forms.ModelForm):
    class Meta:
        model = Pessoa
        exclude = ["criado_em", "atualizado_em", "ano_vigente"]
        widgets = {
            "foto": forms.ClearableFileInput(attrs={"accept": "image/*"}),
            "data_nascimento": forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
            "data_batismo": forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
            "observacoes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for campo_data in ("data_nascimento", "data_batismo"):
            if campo_data in self.fields:
                self.fields[campo_data].input_formats = ["%Y-%m-%d", "%d/%m/%Y"]

        adultos = Pessoa.objects.filter(ativo=True, eh_crianca=False).order_by("nome_completo")
        if self.instance and self.instance.pk:
            adultos = adultos.exclude(pk=self.instance.pk)

        if "conjuge" in self.fields:
            self.fields["conjuge"].queryset = adultos
        if "pai" in self.fields:
            self.fields["pai"].queryset = adultos.exclude(sexo="F")
        if "mae" in self.fields:
            self.fields["mae"].queryset = adultos.exclude(sexo="M")


class CargoForm(forms.ModelForm):
    class Meta:
        model = Cargo
        fields = ["nome", "ano_vigente_de", "ano_vigente_ate", "observacao", "ativo"]
        widgets = {
            "nome": forms.TextInput(attrs={"placeholder": "Ex.: Presbítero, Diácono, Líder..."}),
            "ano_vigente_de": forms.NumberInput(attrs={"placeholder": "Ex.: 2026", "min": 1900, "max": 2100}),
            "ano_vigente_ate": forms.NumberInput(attrs={"placeholder": "Ex.: 2027", "min": 1900, "max": 2100}),
            "observacao": forms.Textarea(attrs={"rows": 3, "placeholder": "Observações sobre o cargo ou vigência..."}),
        }

    def clean(self):
        cleaned_data = super().clean()
        ano_de = cleaned_data.get("ano_vigente_de")
        ano_ate = cleaned_data.get("ano_vigente_ate")

        if ano_de and ano_ate and ano_ate < ano_de:
            self.add_error("ano_vigente_ate", "O ano final ('Até') não pode ser menor que 'Ano vigente de'.")

        return cleaned_data