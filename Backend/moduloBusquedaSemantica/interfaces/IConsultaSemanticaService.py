# Backend/moduloBusquedaSemantica/interfaces/IConsultaSemanticaService.py

from abc import ABC, abstractmethod


class IConsultaSemanticaService(ABC):
    """
    Interfaz del servicio de consulta semántica.
    Define el contrato para realizar búsquedas en lenguaje natural
    sobre documentos y argumentos indexados en ChromaDB,
    recuperando los resultados desde PostgreSQL.
    """

    @abstractmethod
    async def buscarPorLenguajeNatural(
        self,
        consulta: str,
        nResultados: int = 5
    ) -> dict:
        """
        Recibe una consulta en lenguaje natural, la embeddea y busca
        los fragmentos documentales más similares en 'fragmentos_vec'.
        Recupera los fragmentos completos y sus documentos desde PG.

        Args:
            consulta:    Texto libre de la consulta del usuario.
            nResultados: Cantidad máxima de fragmentos a retornar. Default 5.

        Returns:
            dict con 'fragmentos' y 'documentos' relacionados.
        """
        pass

    @abstractmethod
    async def buscarArgumentosPorProblematica(
        self,
        problematicaCod: int,
        nResultados: int = 5
    ) -> list[dict]:
        """
        Busca en 'argumentos_vec' los argumentos más relevantes
        para una problemática específica y recupera sus documentos
        vinculados via ArgumentoDocumento.

        Args:
            problematicaCod: Código de la problemática a consultar.
            nResultados:     Cantidad máxima de argumentos a retornar. Default 5.

        Returns:
            list[dict] con argumentos y sus documentos vinculados.
        """
        pass

    @abstractmethod
    async def _recuperarFragmentos(self, vectorIds: list[str]) -> list[dict]:
        """
        Recupera los fragmentos completos desde PG dado una lista
        de vector_id retornados por ChromaDB.

        Args:
            vectorIds: Lista de vector_id de ChromaDB.

        Returns:
            list[dict] con los fragmentos completos desde PG.
        """
        pass

    @abstractmethod
    async def _recuperarDocumentosDeFragmentos(
        self,
        fragmentos: list[dict]
    ) -> list[dict]:
        """
        Extrae los documento_id únicos de los fragmentos recuperados
        y obtiene los documentos completos desde PG.

        Args:
            fragmentos: Lista de fragmentos con su documento_id.

        Returns:
            list[dict] con los documentos únicos recuperados desde PG.
        """
        pass