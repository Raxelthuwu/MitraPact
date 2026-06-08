# Backend/moduloBusquedaSemantica/views/frontendViews.py

import logging
from django.shortcuts import render

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Vistas de renderizado — cargan el template correspondiente
# El JS de cada template consume la API directamente vía fetch
# ─────────────────────────────────────────────────────────────────────────────

def documento_lista_vista(request):
    """Carga la lista de documentos indexados."""
    return render(request, 'moduloBusquedaSemantica/documento_lista.html')


def documento_form_vista(request):
    """Carga el formulario para cargar o actualizar un documento PDF."""
    return render(request, 'moduloBusquedaSemantica/documento_form.html')


def busqueda_vista(request):
    """Carga el buscador principal de documentos."""
    return render(request, 'moduloBusquedaSemantica/busqueda.html')


def fragmentos_vista(request):
    """Carga la vista de fragmentos de documentos."""
    return render(request, 'moduloBusquedaSemantica/fragmentos.html')


def consulta_semantica_vista(request):
    """Carga la interfaz de consulta en lenguaje natural."""
    return render(request, 'moduloBusquedaSemantica/consulta_semantica.html')


def dashboard_barrio_vista(request):
    """Carga el dashboard de análisis por barrio."""
    return render(request, 'moduloBusquedaSemantica/dashboard_barrio.html')


def dashboard_problematica_vista(request):
    """Carga el dashboard de análisis por problemática y tema."""
    return render(request, 'moduloBusquedaSemantica/dashboard_problematica.html')


def auditoria_vista(request):
    """Carga la vista de diagnóstico de integridad del índice semántico."""
    return render(request, 'moduloBusquedaSemantica/auditoria.html')


def dashboard_vista(request):
    """Carga el dashboard general del índice semántico."""
    return render(request, 'moduloBusquedaSemantica/Dashboard.html')