from django.urls import path
from . import views

app_name = 'cards'  # пространство имён для ссылок

urlpatterns = [
    path('', views.card_list, name='card_list'),
    path('card/<int:pk>/', views.card_detail, name='card_detail'),
    path('create/', views.card_create, name='card_create'),
    path('update/<int:pk>/', views.card_update, name='card_update'),
    path('quiz/', views.quiz, name='quiz'),
]
