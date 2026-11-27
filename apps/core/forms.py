from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class UsuarioCadastroForm(forms.ModelForm):
    senha = forms.CharField(
        label="Senha",
        required=False,
        widget=forms.PasswordInput(
            attrs={"placeholder": "Informe a senha (obrigatória no novo usuário)"}
        ),
    )
    confirmar_senha = forms.CharField(
        label="Confirmar Senha",
        required=False,
        widget=forms.PasswordInput(attrs={"placeholder": "Repita a senha"}),
    )

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "is_active", "is_staff"]
        labels = {
            "username": "Usuário (Login)",
            "first_name": "Nome",
            "last_name": "Sobrenome",
            "email": "E-mail",
            "is_active": "Ativo",
            "is_staff": "Acesso ao Admin",
        }

    def clean(self):
        cleaned = super().clean()
        senha = cleaned.get("senha")
        confirmar = cleaned.get("confirmar_senha")
        is_novo = not (self.instance and self.instance.pk)

        if is_novo and not senha:
            self.add_error("senha", "Informe uma senha para o novo usuário.")

        if senha or confirmar:
            if senha != confirmar:
                self.add_error("confirmar_senha", "As senhas não conferem.")

        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        senha = self.cleaned_data.get("senha")
        if senha:
            user.set_password(senha)
        if commit:
            user.save()
        return user