from django.urls import path
from . import views

urlpatterns = [
    path('extract_keywords/', views.extract_keywords, name='extract_keywords'),
]
