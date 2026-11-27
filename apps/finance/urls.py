from django.urls import path

from . import views

app_name = "finance"

urlpatterns = [
    path("centros-custo/", views.centro_custo_form, name="centro_custo"),
    path("centros-custo/<int:pk>/", views.centro_custo_form, name="centro_custo_editar"),
    path("plano-contas/", views.plano_contas_form, name="plano_contas"),
    path("plano-contas/<int:pk>/", views.plano_contas_form, name="plano_contas_editar"),
]
