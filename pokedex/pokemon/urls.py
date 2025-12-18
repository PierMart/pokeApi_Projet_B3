from django.urls import path
from . import views

app_name = 'pokemon'

urlpatterns = [
    path('', views.index, name='index'),
    path('list/', views.pokedex_list, name='list'),
    path('pokemon/<str:pokemon_id>/', views.pokemon_detail, name='detail'),
]
