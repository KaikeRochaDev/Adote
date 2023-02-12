from django.urls import path
from . import views

urlpatterns = [
    path('', views.cadastro),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('login/', views.logar, name='login'),
    path('sair/', views.sair, name="sair"),
]
