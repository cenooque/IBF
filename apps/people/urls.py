from django.urls import path
from . import views

app_name = "people"

urlpatterns = [
    path("", views.pessoa_lista, name="lista"),
    path("nova/", views.pessoa_criar, name="criar"),
    path("<int:pk>/editar/", views.pessoa_editar, name="editar"),
    path("<int:pk>/excluir/", views.pessoa_excluir, name="excluir"),
    path("excluir-lote/", views.pessoa_excluir_lote, name="excluir_lote"),
    path("exportar/excel/", views.pessoa_exportar_excel, name="exportar_excel"),
    path("exportar/pdf/", views.pessoa_exportar_pdf, name="exportar_pdf"),
    path("cargos/", views.cargo_lista, name="cargo_lista"),
    path("cargos/novo/", views.cargo_criar, name="cargo_criar"),
    path("cargos/<int:pk>/editar/", views.cargo_editar, name="cargo_editar"),
]