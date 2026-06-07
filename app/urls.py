from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('eventos/', include('Backend.moduloEventos.urls')),
    path('estadisticas/', include('Backend.moduloEstadisticas.urls')),
]


