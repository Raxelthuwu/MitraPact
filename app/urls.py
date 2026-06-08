from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('eventos/', include('Backend.moduloEventos.urls')),
    path('', include('Backend.moduloLogin.urls')),
    path('semantica/', include('Backend.moduloBusquedaSemantica.urls')),
]


