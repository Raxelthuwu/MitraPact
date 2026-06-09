# Backend/moduloBusquedaSemantica/urls.py

from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from Backend.moduloLogin.views import login_requerido
from .views import (
    # API views
    DocumentoView,
    DocumentoDetalleView,
    DocumentoBusquedaView,
    TemaBusquedaView,
    FragmentoBusquedaView,
    ArgumentoBusquedaView,
    DistribucionFilterView,
    ProblematicaFilterView,
    TemaFilterView,
    OpinionFilterView,
    BarrioFilterView,
    AuditoriaFilterView,
    ConsultaSemanticaView,
    ArgumentoDetalleView,
    ArgumentoCreateView,
    # Frontend views
    documento_lista_vista,
    documento_form_vista,
    busqueda_vista,
    fragmentos_vista,
    consulta_semantica_vista,
    dashboard_barrio_vista,
    dashboard_problematica_vista,
    auditoria_vista,
    dashboard_vista,
)

urlpatterns = [
    # FRONTEND
    path('',                         login_requerido(dashboard_vista),               name='semantica-inicio'),
    path('documentos/lista/',        login_requerido(documento_lista_vista),         name='documento-lista-vista'),
    path('documentos/nuevo/',        login_requerido(documento_form_vista),          name='documento-form-vista'),
    path('busqueda/',                login_requerido(busqueda_vista),                name='busqueda-vista'),
    path('fragmentos/',              login_requerido(fragmentos_vista),              name='fragmentos-vista'),
    path('consulta/',                login_requerido(consulta_semantica_vista),      name='consulta-semantica-vista'),
    path('dashboard/barrio/',        login_requerido(dashboard_barrio_vista),        name='dashboard-barrio-vista'),
    path('dashboard/problematica/',  login_requerido(dashboard_problematica_vista),  name='dashboard-problematica-vista'),
    path('auditoria/',               login_requerido(auditoria_vista),               name='auditoria-vista'),
    path('dashboard/',               login_requerido(dashboard_vista),               name='dashboard-vista'),

    # API — DOCUMENTOS
    path('documentos/',              csrf_exempt(login_requerido(DocumentoView.as_view())),               name='documento-cargar'),
    path('documentos/<str:pk>/',     csrf_exempt(login_requerido(DocumentoDetalleView.as_view())),        name='documento-detalle'),

    # API — BÚSQUEDA
    path('busqueda/documentos/',     csrf_exempt(login_requerido(DocumentoBusquedaView.as_view())),       name='busqueda-documentos'),
    path('busqueda/documentos/<str:pk>/', csrf_exempt(login_requerido(DocumentoDetalleView.as_view())),  name='documento-detalle-busqueda'),
    path('busqueda/temas/',          csrf_exempt(login_requerido(TemaBusquedaView.as_view())),            name='busqueda-temas'),
    path('busqueda/fragmentos/',     csrf_exempt(login_requerido(FragmentoBusquedaView.as_view())),       name='busqueda-fragmentos'),
    path('busqueda/argumentos/',     csrf_exempt(login_requerido(ArgumentoBusquedaView.as_view())),       name='busqueda-argumentos'),

    # API — FILTROS
    path('filter/distribucion/',     csrf_exempt(login_requerido(DistribucionFilterView.as_view())),      name='filter-distribucion'),
    path('filter/problematica/',     csrf_exempt(login_requerido(ProblematicaFilterView.as_view())),      name='filter-problematica'),
    path('filter/tema/',             csrf_exempt(login_requerido(TemaFilterView.as_view())),              name='filter-tema'),
    path('filter/opiniones/',        csrf_exempt(login_requerido(OpinionFilterView.as_view())),           name='filter-opiniones'),
    path('filter/barrio/',           csrf_exempt(login_requerido(BarrioFilterView.as_view())),            name='filter-barrio'),
    path('filter/auditoria/',        csrf_exempt(login_requerido(AuditoriaFilterView.as_view())),         name='filter-auditoria'),

    # API — CONSULTA SEMÁNTICA
    path('consulta/semantica/',      csrf_exempt(login_requerido(ConsultaSemanticaView.as_view())),       name='consulta-semantica'),

    # API — ARGUMENTOS
    path('argumentos/',              csrf_exempt(login_requerido(ArgumentoCreateView.as_view())),         name='argumento-crear'),
    path('argumentos/<str:pk>/',     csrf_exempt(login_requerido(ArgumentoDetalleView.as_view())),        name='argumento-detalle'),
]