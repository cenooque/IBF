from django.urls import path
from . import views

app_name = "relatorios"

urlpatterns = [
    path("aniversariantes/", views.aniversariantes, name="aniversariantes"),
    path("pessoas/", views.pessoas, name="pessoas"),
    path("financeiro/", views.financeiro, name="financeiro"),
]
