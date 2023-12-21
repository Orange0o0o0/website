from django.urls import include, path
from . import views
from django.contrib import admin

urlpatterns = [
    path('', views.index, name='index'),
    path('admin/', admin.site.urls),
    path('webapp/', include('webapp.urls')),
]
