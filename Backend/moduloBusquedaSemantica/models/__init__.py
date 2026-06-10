# Backend/moduloBusquedaSemantica/models/__init__.py

from Backend.moduloEventos.models import Barrio
from .cargaDeDocumentos           import Documento, Fragmento, TemaDocumento
from .argumentos                  import Argumento
from .argumentoDocumento          import ArgumentoDocumento
from .opiniones                   import OpinionClasificada
from .filtros                     import FiltroSemantico

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