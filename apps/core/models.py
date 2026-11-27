from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.db import models

User = get_user_model()


class PermissaoTela(models.Model):
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="permissoes_tela",
        verbose_name="Usuário",
    )
    codigo_tela = models.CharField(max_length=80, verbose_name="Código da Tela")
    nome_tela = models.CharField(max_length=120, verbose_name="Tela")
    app_label = models.CharField(max_length=50, verbose_name="App")
    model_name = models.CharField(max_length=50, verbose_name="Modelo")

    pode_consultar = models.BooleanField(default=False, verbose_name="Consultar")
    pode_alterar = models.BooleanField(default=False, verbose_name="Alterar")
    pode_excluir = models.BooleanField(default=False, verbose_name="Excluir")
    pode_incluir = models.BooleanField(default=False, verbose_name="Incluir")

    class Meta:
        db_table = "sistema_permissoes_tela"
        verbose_name = "Permissão de Tela"
        verbose_name_plural = "Permissões de Tela"
        unique_together = ("usuario", "codigo_tela")
        ordering = ["usuario__id", "nome_tela"]

    def __str__(self) -> str:
        return f"{self.usuario.username} - {self.nome_tela}"

    def sincronizar_permissoes_django(self) -> None:
        mapa = {
            f"view_{self.model_name}": self.pode_consultar,
            f"change_{self.model_name}": self.pode_alterar,
            f"delete_{self.model_name}": self.pode_excluir,
            f"add_{self.model_name}": self.pode_incluir,
        }
        for codename, habilitado in mapa.items():
            perm = Permission.objects.filter(
                content_type__app_label=self.app_label,
                content_type__model=self.model_name,
                codename=codename,
            ).first()
            if perm:
                if habilitado:
                    self.usuario.user_permissions.add(perm)
                else:
                    self.usuario.user_permissions.remove(perm)