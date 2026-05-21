from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('statistics/', views.statistics, name='statistics'),
    path('broadcast/', views.broadcast, name='broadcast'),
]