from .documentoViews            import DocumentoView, DocumentoDetalleView
from .busquedaViews             import (
    DocumentoBusquedaView,
    TemaBusquedaView,
    FragmentoBusquedaView,
    ArgumentoBusquedaView,
)
from .filterViews               import (
    DistribucionFilterView,
    ProblematicaFilterView,
    TemaFilterView,
    OpinionFilterView,
    BarrioFilterView,
    AuditoriaFilterView,
)
from .consultaSemanticaViews    import ConsultaSemanticaView
from .argumentoViews            import ArgumentoDetalleView, ArgumentoCreateView
from .ArgumentosFrecuentesview import (
    argumentos_frecuentes_vista,
    ArgumentosFrecuentesView,
    ArgumentoIncrementarView,
    OpinionesClasificadasView,
)
from .frontendViews             import (
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
    # Documentos
    'DocumentoView',
    'DocumentoDetalleView',
    # Búsqueda
    'DocumentoBusquedaView',
    'TemaBusquedaView',
    'FragmentoBusquedaView',
    'ArgumentoBusquedaView',
    # Filtros
    'DistribucionFilterView',
    'ProblematicaFilterView',
    'TemaFilterView',
    'OpinionFilterView',
    'BarrioFilterView',
    'AuditoriaFilterView',
    # Consulta semántica
    'ConsultaSemanticaView',
    # Argumentos
    'ArgumentoDetalleView',
    'ArgumentoCreateView',
    'ArgumentosFrecuentesView',
    'ArgumentoIncrementarView',
    # Opiniones
    'OpinionesClasificadasView',
    # Frontend (vistas HTML)
    'argumentos_frecuentes_vista',
    'dashboard_vista',
    'documento_lista_vista',
    'documento_form_vista',
    'busqueda_vista',
    'fragmentos_vista',
    'consulta_semantica_vista',
    'dashboard_barrio_vista',
    'dashboard_problematica_vista',
    'auditoria_vista',
]