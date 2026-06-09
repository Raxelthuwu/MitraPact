# Backend/moduloBusquedaSemantica/views/__init__.py

from .documentoViews         import DocumentoView, DocumentoDetalleView
from .busquedaViews          import DocumentoBusquedaView, TemaBusquedaView, FragmentoBusquedaView, ArgumentoBusquedaView # <-- Se agregó ArgumentoBusquedaView
from .filterViews            import DistribucionFilterView, ProblematicaFilterView, TemaFilterView, OpinionFilterView, BarrioFilterView, AuditoriaFilterView
from .consultaSemanticaViews import ConsultaSemanticaView, ArgumentoDetailView # <-- Aquí se importa correctamente
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
    # <-- SE ELIMINÓ la importación duplicada que rota el error
)

__all__ = [
    # API views
    'DocumentoView',
    'DocumentoDetalleView',
    'DocumentoBusquedaView',
    'TemaBusquedaView',
    'FragmentoBusquedaView',
    'ArgumentoBusquedaView',
    'DistribucionFilterView',
    'ProblematicaFilterView',
    'TemaFilterView',
    'OpinionFilterView',
    'BarrioFilterView',
    'AuditoriaFilterView',
    'ConsultaSemanticaView',
    'ArgumentoDetailView', # <-- Clasificado correctamente como API View
    
    # Frontend views
    'dashboard_vista',     # <-- Se agregó para que coincida con tus imports
    'documento_lista_vista',
    'documento_form_vista',
    'busqueda_vista',
    'fragmentos_vista',
    'consulta_semantica_vista',
    'dashboard_barrio_vista',
    'dashboard_problematica_vista',
    'auditoria_vista',
]