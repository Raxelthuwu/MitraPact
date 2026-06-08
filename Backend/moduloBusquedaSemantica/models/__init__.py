# Backend/moduloBusquedaSemantica/models/__init__.py

from Backend.moduloEventos.models import Barrio

from .cargaDeDocumentos        import Documento
from .cargaDeDocumentos        import Fragmento
from .cargaDeDocumentos        import TemaDocumento
from .argumentos               import Argumento
from .argumentoDocumento       import ArgumentoDocumento
from .opiniones                import OpinionClasificada
from .filtros                  import FiltroSemantico
from .filtros                  import Barrio

__all__ = [
    'Documento',
    'Fragmento',
    'TemaDocumento',
    'Argumento',
    'ArgumentoDocumento',
    'OpinionClasificada',
    'FiltroSemantico',
    'Barrio',
]