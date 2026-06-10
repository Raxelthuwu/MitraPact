from .cargaDeDocumentos import Documento, Fragmento, TemaDocumento
from .argumentos        import Argumento
from .argumentoDocumento import ArgumentoDocumento
from .opiniones         import OpinionClasificada
from .filtros           import FiltroSemantico, Barrio   # ← Barrio viene de aquí ahora

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