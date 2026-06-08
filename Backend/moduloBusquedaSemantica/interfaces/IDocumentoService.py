# Backend/moduloBusquedaSemantica/interfaces/IDocumentoService.py

from abc import ABC, abstractmethod
from typing import Optional


class IDocumentoService(ABC):
    """
    Interfaz del servicio de gestión documental.
    Define el contrato que debe cumplir cualquier implementación
    del ciclo de vida de documentos PDF en el sistema.
    """


    @abstractmethod
    async def cargar(
        self,
        archivo,
        nombre: str,
        temas: Optional[list[str]] = None,
        chunkSize: Optional[int] = None
    ) -> dict:
        """
        Carga un documento PDF, lo fragmenta y lo indexa en ChromaDB.

        Args:
            archivo:   Archivo PDF recibido desde la view.
            nombre:    Nombre legible del documento.
            temas:     Temas del documento provistos por el usuario. Si no se
                    proveen se intenta inferirlos desde opiniones_vec. Opcional.
            chunkSize: Tamaño de chunk en caracteres. Opcional.

        Returns:
            dict con el documento persistido y el total de fragmentos indexados.
        """
        pass

    @abstractmethod
    async def actualizar(
        self,
        documentoId: str,
        archivo,
        nombre: Optional[str] = None,
        temas: Optional[list[str]] = None,
        chunkSize: Optional[int] = None
    ) -> dict:
        """
        Reemplaza un documento existente y re-indexa desde cero.

        Args:
            documentoId: UUID del documento a reemplazar.
            archivo:     Nuevo archivo PDF.
            nombre:      Nuevo nombre legible. Opcional.
            temas:       Nuevos temas del documento. Opcional.
            chunkSize:   Tamaño de chunk. Opcional.

        Returns:
            dict con el documento actualizado y el total de fragmentos re-indexados.
        """
        pass

    @abstractmethod
    async def eliminar(self, documentoId: str) -> bool:
        """
        Elimina un documento y todos sus datos asociados de PG y ChromaDB.

        Args:
            documentoId: UUID del documento a eliminar.

        Returns:
            True si se eliminó correctamente, False si no se encontró.
        """
        pass