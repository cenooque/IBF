from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("", views.painel_erp, name="painel"),
    path("usuarios/", views.usuario_lista, name="usuario_lista"),
    path("usuarios/novo/", views.usuario_form, name="usuario_criar"),
    path("usuarios/<int:pk>/editar/", views.usuario_form, name="usuario_editar"),
    path("acessos/", views.liberacao_acessos, name="liberacao_acessos"),
]