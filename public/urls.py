from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('result/', views.result_view, name='result'),
    path('result/pdf/<str:roll>/', views.download_result_pdf, name='download_result_pdf'),
]