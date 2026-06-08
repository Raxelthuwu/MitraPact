# Backend/moduloBusquedaSemantica/interfaces/__init__.py

from .IDocumentoService         import IDocumentoService
from .IClasificacionService     import IClasificacionService
from .IConsultaSemanticaService import IConsultaSemanticaService
from .IFilterService            import IFilterService
from .IBusquedaService          import IBusquedaService

__all__ = [
    'IDocumentoService',
    'IClasificacionService',
    'IConsultaSemanticaService',
    'IFilterService',
    'IBusquedaService',
]