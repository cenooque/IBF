from django import template

from apps.core.views import usuario_pode_tela

register = template.Library()


@register.filter(name="pode_ver")
def pode_ver(user, codigo_tela):
    return usuario_pode_tela(user, codigo_tela, "consultar")


@register.filter(name="pode_incluir")
def pode_incluir(user, codigo_tela):
    return usuario_pode_tela(user, codigo_tela, "incluir")


@register.filter(name="pode_alterar")
def pode_alterar(user, codigo_tela):
    return usuario_pode_tela(user, codigo_tela, "alterar")


@register.filter(name="pode_excluir")
def pode_excluir(user, codigo_tela):
    return usuario_pode_tela(user, codigo_tela, "excluir")