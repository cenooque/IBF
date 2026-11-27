from datetime import date
from io import BytesIO
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import models
from django.utils import timezone
from PIL import Image, ImageOps


def foto_pessoa_path(instance, filename):
    return f"pessoas/{instance.pk}.jpg"


def _converter_para_jpg(arquivo_foto):
    arquivo_foto.seek(0)
    with Image.open(arquivo_foto) as img:
        img = ImageOps.exif_transpose(img)
        if img.mode in ("RGBA", "LA", "P"):
            fundo = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            mascara = img.split()[-1] if "A" in img.mode else None
            fundo.paste(img, mask=mascara)
            img = fundo
        elif img.mode != "RGB":
            img = img.convert("RGB")

        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=90, optimize=True)
        return ContentFile(buffer.getvalue())


class Cargo(models.Model):
    nome = models.CharField(max_length=100, unique=True, verbose_name="Cargo")
    ano_vigente_de = models.PositiveIntegerField(
        blank=True, null=True, verbose_name="Ano vigente de"
    )
    ano_vigente_ate = models.PositiveIntegerField(
        blank=True, null=True, verbose_name="Até"
    )
    observacao = models.TextField(blank=True, null=True, verbose_name="Observação")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")

    class Meta:
        db_table = "cargos"
        verbose_name = "Cargo"
        verbose_name_plural = "Cargos"
        ordering = ["nome"]

    def __str__(self) -> str:
        return self.nome


class Pessoa(models.Model):
    class Sexo(models.TextChoices):
        MASCULINO = "M", "Masculino"
        FEMININO = "F", "Feminino"

    class EstadoCivil(models.TextChoices):
        SOLTEIRO = "SOLTEIRO", "Solteiro(a)"
        CASADO = "CASADO", "Casado(a)"
        DIVORCIADO = "DIVORCIADO", "Divorciado(a)"
        VIUVO = "VIUVO", "Viúvo(a)"

    class SituacaoIgreja(models.TextChoices):
        MEMBRO = "MEMBRO", "Membro"
        CONGREGADO = "CONGREGADO", "Congregado"
        VISITANTE = "VISITANTE", "Visitante"
        AFASTADO = "AFASTADO", "Afastado"
        TRANSFERIDO = "TRANSFERIDO", "Transferido"

    nome_completo = models.CharField("Nome completo", max_length=150)
    foto = models.ImageField(
        upload_to=foto_pessoa_path,
        blank=True,
        null=True,
        verbose_name="Foto",
    )
    dizimista = models.BooleanField("Dizimista", default=False)
    ativo = models.BooleanField("Ativo", default=True)
    eh_crianca = models.BooleanField("Criança", default=False)

    # Vínculo de Cônjuge (bidirecional no save)
    conjuge = models.OneToOneField(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="conjuge_vinculado",
        verbose_name="Cônjuge",
    )

    # Vínculo de Pais (habilitado quando eh_crianca = True)
    pai = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="filhos_pai",
        verbose_name="Pai",
    )
    mae = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="filhos_mae",
        verbose_name="Mãe",
    )

    sexo = models.CharField("Sexo", max_length=1, choices=Sexo.choices, blank=True)
    data_nascimento = models.DateField("Data de nascimento", null=True, blank=True)
    data_batismo = models.DateField("Data de batismo", null=True, blank=True)
    estado_civil = models.CharField(
        "Estado civil", max_length=15, choices=EstadoCivil.choices, blank=True
    )
    situacao_igreja = models.CharField(
        "Situação",
        max_length=15,
        choices=SituacaoIgreja.choices,
        default=SituacaoIgreja.MEMBRO,
    )
    cargo = models.ForeignKey(
        Cargo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pessoas",
        verbose_name="Cargo",
    )
    ano_vigente = models.PositiveIntegerField(
        "Ano vigente",
        null=True,
        blank=True,
        default=timezone.now().year,
    )

    telefone = models.CharField("Telefone", max_length=30, blank=True)
    email = models.EmailField("E-mail", blank=True)
    endereco = models.CharField("Endereço", max_length=200, blank=True)
    complemento = models.CharField("Complemento", max_length=100, blank=True)
    bairro = models.CharField("Bairro", max_length=100, blank=True)
    cidade = models.CharField("Cidade", max_length=100, blank=True)
    estado = models.CharField("UF", max_length=2, blank=True)
    cep = models.CharField("CEP", max_length=15, blank=True)

    observacoes = models.TextField("Observações", blank=True)
    criado_em = models.DateTimeField("Criado em", auto_now_add=True)
    atualizado_em = models.DateTimeField("Atualizado em", auto_now=True)

    class Meta:
        db_table = "pessoas"
        ordering = ["nome_completo"]
        verbose_name = "Pessoa"
        verbose_name_plural = "Pessoas"
        indexes = [
            models.Index(fields=["nome_completo"]),
            models.Index(fields=["situacao_igreja", "ativo"]),
            models.Index(fields=["dizimista"]),
            models.Index(fields=["eh_crianca"]),
        ]

    def __str__(self):
        return f"{self.id} - {self.nome_completo}" if self.pk else self.nome_completo

    @property
    def idade(self):
        if not self.data_nascimento:
            return None
        hoje = date.today()
        anos = hoje.year - self.data_nascimento.year - (
            (hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day)
        )
        if anos == 0:
            meses = (hoje.year - self.data_nascimento.year) * 12 + (hoje.month - self.data_nascimento.month)
            if hoje.day < self.data_nascimento.day:
                meses -= 1
            return f"{max(meses, 0)} mês(es)"
        return f"{anos} ano(s)"

    def clean(self):
        if self.pk:
            if self.conjuge_id == self.pk:
                raise ValidationError({"conjuge": "Uma pessoa não pode ser cônjuge de si mesma."})
            if self.pai_id == self.pk:
                raise ValidationError({"pai": "Uma pessoa não pode ser pai de si mesma."})
            if self.mae_id == self.pk:
                raise ValidationError({"mae": "Uma pessoa não pode ser mãe de si mesma."})
        if self.eh_crianca and self.conjuge_id:
            raise ValidationError({"conjuge": "Um cadastro marcado como criança não pode ter cônjuge."})

    def save(self, *args, **kwargs):
        # Se não for criança, limpa os vínculos de pai/mãe
        if not self.eh_crianca:
            self.pai = None
            self.mae = None

        foto_anterior = None
        conjuge_anterior_id = None
        if self.pk:
            antigo = (
                Pessoa.objects.filter(pk=self.pk)
                .values("foto", "conjuge_id")
                .first()
            )
            if antigo:
                conjuge_anterior_id = antigo["conjuge_id"]
                if antigo["foto"]:
                    foto_anterior = antigo["foto"]

        foto_enviada = self.foto
        foto_convertida = None
        if foto_enviada and hasattr(foto_enviada, "file"):
            foto_convertida = _converter_para_jpg(foto_enviada)
            try:
                if hasattr(foto_enviada.file, "close"):
                    foto_enviada.file.close()
            except Exception:
                pass
            try:
                foto_enviada.close()
            except Exception:
                pass

        try:
            if self.foto and getattr(self.foto, "closed", True) is False:
                self.foto.close()
        except Exception:
            pass

        foto_pendente = None
        if foto_convertida and not self.pk:
            foto_pendente = foto_convertida
            self.foto = None
        elif foto_convertida:
            storage = self._meta.get_field("foto").storage
            alvo_rel = f"pessoas/{self.pk}.jpg"
            if storage.exists(alvo_rel):
                try:
                    storage.delete(alvo_rel)
                except PermissionError:
                    pass
            self.foto.save(f"{self.pk}.jpg", foto_convertida, save=False)

        super().save(*args, **kwargs)

        if foto_pendente:
            self.foto.save(f"{self.pk}.jpg", foto_pendente, save=False)
            super().save(update_fields=["foto"])

        nome_foto_atual = self.foto.name if self.foto else None
        if foto_anterior and foto_anterior != nome_foto_atual:
            storage = self._meta.get_field("foto").storage
            try:
                if storage.exists(foto_anterior):
                    storage.delete(foto_anterior)
            except PermissionError:
                pass

        # Desvincula cônjuge antigo caso tenha sido trocado ou removido
        if conjuge_anterior_id and conjuge_anterior_id != self.conjuge_id:
            Pessoa.objects.filter(pk=conjuge_anterior_id, conjuge_id=self.pk).update(conjuge=None)

        # Espelha o vínculo no cadastro do cônjuge selecionado
        if self.conjuge_id:
            Pessoa.objects.filter(pk=self.conjuge_id).exclude(conjuge_id=self.pk).update(conjuge=self.pk)