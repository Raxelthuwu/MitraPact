from django.urls import path
from Backend.moduloBusquedaSemantica.views import (
    # Frontend
    dashboard_vista,
    documento_lista_vista,
    documento_form_vista,
    busqueda_vista,
    fragmentos_vista,
    consulta_semantica_vista,
    dashboard_barrio_vista,
    dashboard_problematica_vista,
    auditoria_vista,
    argumentos_frecuentes_vista,

    # API
    DocumentoView,
    DocumentoDetalleView,
    DocumentoBusquedaView,
    TemaBusquedaView,
    FragmentoBusquedaView,
    ArgumentoBusquedaView,
    ArgumentoDetalleView,
    ArgumentoCreateView,
    ArgumentosFrecuentesView,
    ArgumentoIncrementarView,
    OpinionesClasificadasView,
    DistribucionFilterView,
    ProblematicaFilterView,
    TemaFilterView,
    OpinionFilterView,
    BarrioFilterView,
    AuditoriaFilterView,
    ConsultaSemanticaView,
)

urlpatterns = [

    # ── Vistas HTML ───────────────────────────────────────────────────────────
    path('',                             dashboard_vista,               name='dashboard-vista'),
    path('documentos/',                  documento_lista_vista,         name='documento-lista-vista'),
    path('documentos/nuevo/',            documento_form_vista,          name='documento-form-vista'),
    path('busqueda/',                    busqueda_vista,                name='busqueda-vista'),
    path('fragmentos/',                  fragmentos_vista,              name='fragmentos-vista'),
    path('consulta/',                    consulta_semantica_vista,      name='consulta-semantica-vista'),
    path('dashboard/barrio/',            dashboard_barrio_vista,        name='dashboard-barrio-vista'),
    path('dashboard/problematica/',      dashboard_problematica_vista,  name='dashboard-problematica-vista'),
    path('auditoria/',                   auditoria_vista,               name='auditoria-vista'),

    # IMPORTANTE: frecuentes antes de <str:pk> para que no colisione
    path('argumentos/frecuentes/',       argumentos_frecuentes_vista,   name='argumentos-frecuentes-vista'),

    # ── API — Argumentos ──────────────────────────────────────────────────────
    path('argumentos/frecuentes/api/',               ArgumentosFrecuentesView.as_view(),   name='argumentos-frecuentes-api'),
    path('argumentos/<str:pk>/incrementar/',         ArgumentoIncrementarView.as_view(),   name='argumento-incrementar'),
    path('argumentos/<str:pk>/',                     ArgumentoDetalleView.as_view(),       name='argumento-detalle'),
    path('argumentos/',                              ArgumentoCreateView.as_view(),         name='argumento-create'),

    # ── API — Opiniones clasificadas ──────────────────────────────────────────
    path('opiniones/clasificadas/',      OpinionesClasificadasView.as_view(),  name='opiniones-clasificadas-api'),

    # ── API — Documentos ──────────────────────────────────────────────────────
    path('documentos/api/',              DocumentoView.as_view(),         name='documento-list-api'),
    path('documentos/api/<str:pk>/',     DocumentoDetalleView.as_view(),  name='documento-detalle-api'),
    path('busqueda/documentos/<str:pk>/', DocumentoDetalleView.as_view(), name='busqueda-documento-detalle'),
    # ── API — Búsqueda ────────────────────────────────────────────────────────
    path('busqueda/documentos/',         DocumentoBusquedaView.as_view(),   name='busqueda-documentos'),
    path('busqueda/temas/',              TemaBusquedaView.as_view(),        name='busqueda-temas'),
    path('busqueda/fragmentos/',         FragmentoBusquedaView.as_view(),   name='busqueda-fragmentos'),
    path('busqueda/argumentos/',         ArgumentoBusquedaView.as_view(),   name='busqueda-argumentos'),

    # ── API — Filtros ─────────────────────────────────────────────────────────
    path('filter/distribucion/',         DistribucionFilterView.as_view(),   name='filter-distribucion'),
    path('filter/problematica/',         ProblematicaFilterView.as_view(),   name='filter-problematica'),
    path('filter/tema/',                 TemaFilterView.as_view(),           name='filter-tema'),
    path('filter/opinion/',              OpinionFilterView.as_view(),        name='filter-opinion'),
    path('filter/barrio/',               BarrioFilterView.as_view(),         name='filter-barrio'),
    path('filter/auditoria/',            AuditoriaFilterView.as_view(),      name='filter-auditoria'),

    # ── API — Consulta semántica ──────────────────────────────────────────────
    path('consulta/api/',                ConsultaSemanticaView.as_view(),   name='consulta-semantica-api'),
]