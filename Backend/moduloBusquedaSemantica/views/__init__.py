# Backend/moduloBusquedaSemantica/views/__init__.py

from .documentoViews         import DocumentoView, DocumentoDetalleView
from .busquedaViews          import DocumentoBusquedaView, TemaBusquedaView, FragmentoBusquedaView, ArgumentoBusquedaView
from .filterViews            import DistribucionFilterView, ProblematicaFilterView, TemaFilterView, OpinionFilterView, BarrioFilterView, AuditoriaFilterView
from .consultaSemanticaViews import ConsultaSemanticaView
from .argumentoViews         import ArgumentoDetalleView, ArgumentoCreateView
from .frontendViews          import (
    dashboard_vista,
    documento_lista_vista,
    documento_form_vista,
    busqueda_vista,
    fragmentos_vista,
    consulta_semantica_vista,
    dashboard_barrio_vista,
    dashboard_problematica_vista,
    auditoria_vista,
)

__all__ = [
    'DocumentoView',
    'DocumentoDetalleView',
    'DocumentoBusquedaView',
    'TemaBusquedaView',
    'FragmentoBusquedaView',
    'ArgumentoBusquedaView',
    'ArgumentoDetalleView',
    'ArgumentoCreateView',
    'DistribucionFilterView',
    'ProblematicaFilterView',
    'TemaFilterView',
    'OpinionFilterView',
    'BarrioFilterView',
    'AuditoriaFilterView',
    'ConsultaSemanticaView',
    'documento_lista_vista',
    'documento_form_vista',
    'busqueda_vista',
    'fragmentos_vista',
    'consulta_semantica_vista',
    'dashboard_barrio_vista',
    'dashboard_problematica_vista',
    'auditoria_vista',
    'dashboard_vista',
]