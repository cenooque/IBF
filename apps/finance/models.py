from django.core.exceptions import ValidationError
from django.db import models
from apps.people.models import Pessoa


class GrupoCentroCusto(models.Model):
    codigo = models.CharField("Código", max_length=20, blank=True)
    descricao = models.CharField("Descrição", max_length=100)
    ativo = models.BooleanField("Ativo", default=True)

    class Meta:
        db_table = "fin_grupos_centro_custo"
        ordering = ["descricao"]
        verbose_name = "Grupo de centro de custo"
        verbose_name_plural = "Grupos de centros de custo"

    def __str__(self):
        return f"{self.codigo} - {self.descricao}" if self.codigo else self.descricao


class CentroCusto(models.Model):
    class Tipo(models.TextChoices):
        SINTETICO = "SINTETICO", "Sintético"
        ANALITICO = "ANALITICO", "Analítico"

    class ClassificacaoCusto(models.TextChoices):
        FIXO = "FIXO", "Fixo"
        VARIAVEL = "VARIAVEL", "Variável"

    codigo = models.CharField("Código", max_length=20, unique=True)
    descricao = models.CharField("Descrição", max_length=150)
    tipo = models.CharField("Tipo", max_length=12, choices=Tipo.choices, default=Tipo.ANALITICO)
    grupo = models.ForeignKey(
        GrupoCentroCusto,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        db_column="grupo_id",
        related_name="centros_custo",
        verbose_name="Grupo",
    )
    classificacao_custo = models.CharField(
        "Custo",
        max_length=10,
        choices=ClassificacaoCusto.choices,
        default=ClassificacaoCusto.FIXO,
    )

    # Vínculo com os módulos financeiros
    aceita_contas_pagar = models.BooleanField("Contas a pagar", default=True)
    aceita_contas_receber = models.BooleanField("Contas a receber", default=True)

    # Flags de status
    ativo = models.BooleanField("Ativo", default=True)
    produtivo = models.BooleanField("Produtivo", default=False)
    observacao = models.TextField("Observação", blank=True)

    class Meta:
        db_table = "fin_centros_custo"
        ordering = ["codigo", "descricao"]
        verbose_name = "Centro de custo"
        verbose_name_plural = "Centros de custo"

    def __str__(self):
        return f"{self.codigo} - {self.descricao}" if self.codigo else self.descricao


class ContaFinanceira(models.Model):
    class Tipo(models.TextChoices):
        CAIXA = "CAIXA", "Caixa Interno / Cofre"
        CONTA_CORRENTE = "CC", "Conta Corrente"
        POUPANCA = "POUPANCA", "Conta Poupança"
        APLICACAO = "APLICACAO", "Aplicação Financeira"

    nome = models.CharField("Nome da conta", max_length=100)
    tipo = models.CharField("Tipo", max_length=15, choices=Tipo.choices, default=Tipo.CONTA_CORRENTE)
    banco = models.CharField("Banco", max_length=80, blank=True)
    agencia = models.CharField("Agência", max_length=20, blank=True)
    numero_conta = models.CharField("Número da conta", max_length=30, blank=True)
    saldo_inicial = models.DecimalField("Saldo inicial (R$)", max_digits=14, decimal_places=2, default=0)
    ativo = models.BooleanField("Ativa", default=True)

    class Meta:
        db_table = "fin_contas"
        ordering = ["nome"]
        verbose_name = "Conta financeira"
        verbose_name_plural = "Contas financeiras"

    def __str__(self):
        return self.nome


class PlanoContas(models.Model):
    class Natureza(models.TextChoices):
        RECEITA = "RECEITA", "Receita (Entrada)"
        DESPESA = "DESPESA", "Despesa (Saída)"

    class Tipo(models.TextChoices):
        SINTETICA = "SINTETICA", "Sintética (Grupo)"
        ANALITICA = "ANALITICA", "Analítica (Lançamento)"

    codigo = models.CharField("Código", max_length=20, unique=True)
    nome = models.CharField("Nome da conta", max_length=120)
    natureza = models.CharField("Natureza", max_length=10, choices=Natureza.choices)
    tipo = models.CharField("Tipo", max_length=10, choices=Tipo.choices, default=Tipo.ANALITICA)
    conta_pai = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="subcontas",
        verbose_name="Conta pai",
    )
    ativo = models.BooleanField("Ativa", default=True)

    class Meta:
        db_table = "fin_plano_contas"
        ordering = ["codigo"]
        verbose_name = "Plano de contas"
        verbose_name_plural = "Planos de contas"

    def __str__(self):
        return f"{self.codigo} - {self.nome}"


class Fornecedor(models.Model):
    class TipoPessoa(models.TextChoices):
        PJ = "PJ", "Pessoa Jurídica"
        PF = "PF", "Pessoa Física"

    pessoa = models.ForeignKey(
        Pessoa,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="pessoa_id",
        related_name="fornecedores",
        verbose_name="Pessoa vinculada (ID)",
    )
    tipo_pessoa = models.CharField("Tipo", max_length=2, choices=TipoPessoa.choices, default=TipoPessoa.PJ)
    nome_razao = models.CharField("Nome / Razão Social", max_length=150)
    nome_fantasia = models.CharField("Nome Fantasia", max_length=150, blank=True)
    cpf_cnpj = models.CharField("CPF / CNPJ", max_length=20, blank=True)
    telefone = models.CharField("Telefone", max_length=30, blank=True)
    email = models.EmailField("E-mail", blank=True)
    chave_pix = models.CharField("Chave PIX", max_length=120, blank=True)
    observacoes = models.TextField("Observações", blank=True)
    ativo = models.BooleanField("Ativo", default=True)
    criado_em = models.DateTimeField("Criado em", auto_now_add=True)

    class Meta:
        db_table = "fin_fornecedores"
        ordering = ["nome_razao"]
        verbose_name = "Fornecedor"
        verbose_name_plural = "Fornecedores"

    def __str__(self):
        return f"{self.id} - {self.nome_razao}" if self.pk else self.nome_razao


class ContaReceber(models.Model):
    class Status(models.TextChoices):
        PENDENTE = "PENDENTE", "A receber"
        RECEBIDO = "RECEBIDO", "Recebido"
        CANCELADO = "CANCELADO", "Cancelado"

    class FormaRecebimento(models.TextChoices):
        PIX = "PIX", "PIX"
        DINHEIRO = "DINHEIRO", "Dinheiro"
        TRANSFERENCIA = "TRANSF", "Transferência / TED"
        BOLETO = "BOLETO", "Boleto"
        CARTAO = "CARTAO", "Cartão"

    status = models.CharField("Situação", max_length=10, choices=Status.choices, default=Status.PENDENTE)
    descricao = models.CharField("Descrição / Histórico", max_length=200)

    pessoa = models.ForeignKey(
        Pessoa,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        db_column="pessoa_id",
        related_name="contas_receber",
        verbose_name="Pessoa (ID)",
    )
    fornecedor = models.ForeignKey(
        Fornecedor,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        db_column="fornecedor_id",
        related_name="contas_receber",
        verbose_name="Fornecedor (ID)",
    )

    conta_financeira = models.ForeignKey(
        ContaFinanceira,
        on_delete=models.PROTECT,
        db_column="conta_id",
        related_name="contas_receber",
        verbose_name="Conta / Caixa",
    )
    plano_contas = models.ForeignKey(
        PlanoContas,
        on_delete=models.PROTECT,
        db_column="plano_contas_id",
        related_name="contas_receber",
        verbose_name="Plano de contas",
    )
    centro_custo = models.ForeignKey(
        CentroCusto,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        db_column="centro_custo_id",
        related_name="contas_receber",
        verbose_name="Centro de custo",
    )

    valor = models.DecimalField("Valor (R$)", max_digits=14, decimal_places=2)
    data_competencia = models.DateField("Data de competência")
    data_vencimento = models.DateField("Data de vencimento / previsão")
    data_recebimento = models.DateField("Data de recebimento", null=True, blank=True)
    forma_recebimento = models.CharField(
        "Forma de recebimento", max_length=12, choices=FormaRecebimento.choices, default=FormaRecebimento.PIX
    )
    numero_documento = models.CharField("Nº Documento / Recibo", max_length=50, blank=True)
    observacoes = models.TextField("Observações", blank=True)
    criado_em = models.DateTimeField("Criado em", auto_now_add=True)

    class Meta:
        db_table = "fin_contas_receber"
        ordering = ["-data_vencimento", "-id"]
        verbose_name = "Conta a receber"
        verbose_name_plural = "Contas a receber"
        indexes = [
            models.Index(fields=["status", "data_vencimento"]),
            models.Index(fields=["pessoa", "data_competencia"]),
        ]

    def __str__(self):
        return f"[RECEBER] {self.descricao} - R$ {self.valor}"

    def clean(self):
        if self.plano_contas_id:
            if self.plano_contas.natureza != PlanoContas.Natureza.RECEITA:
                raise ValidationError({"plano_contas": "Selecione uma conta do plano de contas com natureza RECEITA."})
            if self.plano_contas.tipo == PlanoContas.Tipo.SINTETICA:
                raise ValidationError({"plano_contas": "Selecione uma conta analítica para lançar valores."})
        if self.status == self.Status.RECEBIDO and not self.data_recebimento:
            raise ValidationError({"data_recebimento": "Informe a data de recebimento ao confirmar a entrada."})
        if self.centro_custo_id:
            if not self.centro_custo.ativo:
                raise ValidationError({"centro_custo": "Selecione um centro de custo ativo."})
            if self.centro_custo.tipo == CentroCusto.Tipo.SINTETICO:
                raise ValidationError({"centro_custo": "Selecione um centro de custo analítico para lançar valores."})
            if not self.centro_custo.aceita_contas_receber:
                raise ValidationError({"centro_custo": "Este centro de custo não permite vínculo com Contas a Receber."})


class ContaPagar(models.Model):
    class Status(models.TextChoices):
        PENDENTE = "PENDENTE", "A pagar"
        PAGO = "PAGO", "Pago"
        CANCELADO = "CANCELADO", "Cancelado"

    class FormaPagamento(models.TextChoices):
        PIX = "PIX", "PIX"
        DINHEIRO = "DINHEIRO", "Dinheiro"
        TRANSFERENCIA = "TRANSF", "Transferência / TED"
        BOLETO = "BOLETO", "Boleto"
        CARTAO = "CARTAO", "Cartão"

    status = models.CharField("Situação", max_length=10, choices=Status.choices, default=Status.PENDENTE)
    descricao = models.CharField("Descrição / Histórico", max_length=200)

    fornecedor = models.ForeignKey(
        Fornecedor,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        db_column="fornecedor_id",
        related_name="contas_pagar",
        verbose_name="Fornecedor (ID)",
    )
    pessoa = models.ForeignKey(
        Pessoa,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        db_column="pessoa_id",
        related_name="contas_pagar",
        verbose_name="Pessoa (ID)",
    )

    conta_financeira = models.ForeignKey(
        ContaFinanceira,
        on_delete=models.PROTECT,
        db_column="conta_id",
        related_name="contas_pagar",
        verbose_name="Conta / Caixa",
    )
    plano_contas = models.ForeignKey(
        PlanoContas,
        on_delete=models.PROTECT,
        db_column="plano_contas_id",
        related_name="contas_pagar",
        verbose_name="Plano de contas",
    )
    centro_custo = models.ForeignKey(
        CentroCusto,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        db_column="centro_custo_id",
        related_name="contas_pagar",
        verbose_name="Centro de custo",
    )

    valor = models.DecimalField("Valor (R$)", max_digits=14, decimal_places=2)
    data_competencia = models.DateField("Data de competência")
    data_vencimento = models.DateField("Data de vencimento")
    data_pagamento = models.DateField("Data de pagamento", null=True, blank=True)
    forma_pagamento = models.CharField(
        "Forma de pagamento", max_length=12, choices=FormaPagamento.choices, default=FormaPagamento.PIX
    )
    numero_documento = models.CharField("Nº Documento / NF / Boleto", max_length=50, blank=True)
    observacoes = models.TextField("Observações", blank=True)
    criado_em = models.DateTimeField("Criado em", auto_now_add=True)

    class Meta:
        db_table = "fin_contas_pagar"
        ordering = ["-data_vencimento", "-id"]
        verbose_name = "Conta a pagar"
        verbose_name_plural = "Contas a pagar"
        indexes = [
            models.Index(fields=["status", "data_vencimento"]),
            models.Index(fields=["fornecedor", "data_vencimento"]),
        ]

    def __str__(self):
        return f"[PAGAR] {self.descricao} - R$ {self.valor}"

    def clean(self):
        if self.plano_contas_id:
            if self.plano_contas.natureza != PlanoContas.Natureza.DESPESA:
                raise ValidationError({"plano_contas": "Selecione uma conta do plano de contas com natureza DESPESA."})
            if self.plano_contas.tipo == PlanoContas.Tipo.SINTETICA:
                raise ValidationError({"plano_contas": "Selecione uma conta analítica para lançar valores."})
        if self.status == self.Status.PAGO and not self.data_pagamento:
            raise ValidationError({"data_pagamento": "Informe a data de pagamento ao confirmar a saída."})
        if self.centro_custo_id:
            if not self.centro_custo.ativo:
                raise ValidationError({"centro_custo": "Selecione um centro de custo ativo."})
            if self.centro_custo.tipo == CentroCusto.Tipo.SINTETICO:
                raise ValidationError({"centro_custo": "Selecione um centro de custo analítico para lançar valores."})
            if not self.centro_custo.aceita_contas_pagar:
                raise ValidationError({"centro_custo": "Este centro de custo não permite vínculo com Contas a Pagar."})