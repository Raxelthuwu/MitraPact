# Backend/moduloBusquedaSemantica/interfaces/IClasificacionService.py

from abc import ABC, abstractmethod


class IClasificacionService(ABC):
    """
    Interfaz del servicio de clasificación semántica de encuestas.
    Define el contrato para el worker que escucha notificaciones de PostgreSQL
    y orquesta el procesamiento semántico automático de opiniones ciudadanas.
    Clasifica opiniones, extrae argumentos, gestiona frecuencias y vincula
    documentos relacionados sin intervención del usuario.
    """

    @abstractmethod
    async def iniciar(self) -> None:
        """
        Inicia el worker abriendo una conexión asyncpg y registrando
        el LISTEN sobre el canal 'encuesta_insertada' de PostgreSQL.
        Queda en loop indefinido procesando notificaciones hasta que
        se llame a detener().
        """
        pass

    @abstractmethod
    async def detener(self) -> None:
        """
        Detiene el worker cerrando la conexión asyncpg limpiamente.
        Garantiza que no queden conexiones abiertas ni procesos huérfanos.
        """
        pass

    @abstractmethod
    async def _procesarEncuesta(self, payload: dict) -> None:
        """
        Orquesta el flujo completo de procesamiento de una encuesta.
        Recibe el payload del pg_notify y coordina en orden:
        clasificación de opinión, extracción de argumentos y vinculación
        de documentos. Es el punto de entrada interno del worker.

        Args:
            payload: dict deserializado del pg_notify con los campos:
                     id, barrio_id, opinion_politica, prob_1_cod,
                     prob_2_cod, prob_otra.
        """
        pass

    @abstractmethod
    async def _clasificarOpinion(
        self,
        encuestaId: str,
        barrioId: str,
        textoOpinion: str
    ) -> dict:
        """
        Embeddea el texto de la opinión y consulta 'opiniones_vec' en ChromaDB
        para determinar el tema más cercano semánticamente.
        Persiste el resultado en OpinionClasificada y hace upsert en 'opiniones_vec'.

        Args:
            encuestaId:   UUID de la encuesta origen.
            barrioId:     UUID del barrio de la encuesta.
            textoOpinion: Texto libre de la opinión política.

        Returns:
            dict con la OpinionClasificada persistida incluyendo el tema asignado.
        """
        pass

    @abstractmethod
    async def _extraerArgumentos(
        self,
        opinionId: str,
        textoOpinion: str,
        prob1Cod: int,
        prob2Cod: int,
        probOtra: str
    ) -> list[dict]:
        """
        Extrae los argumentos presentes en el texto de la opinión.
        Por cada argumento consulta 'argumentos_vec' filtrando por problematica_cod
        para decidir si es el mismo argumento existente (incrementa frecuencia)
        o uno nuevo (inserta y hace upsert en 'argumentos_vec').
        Si viene prob_otra delega a _resolverProblematica para inferir el código.

        Args:
            opinionId:    UUID de la OpinionClasificada padre.
            textoOpinion: Texto de la opinión a procesar.
            prob1Cod:     Código de la primera problemática de la encuesta.
            prob2Cod:     Código de la segunda problemática de la encuesta.
            probOtra:     Texto libre de problemática no catalogada. Puede ser None.

        Returns:
            list[dict] con los argumentos procesados incluyendo id y frecuencia final.
        """
        pass

    @abstractmethod
    async def _resolverProblematica(self, probOtra: str) -> int:
        """
        Resuelve el código de problemática para un texto libre no catalogado.
        Embeddea probOtra y hace query general en 'argumentos_vec' sin filtro
        de problematica_cod para encontrar el código más cercano semánticamente.

        Args:
            probOtra: Texto libre de problemática no catalogada.

        Returns:
            int con el problematica_cod inferido semánticamente.
        """
        pass

    @abstractmethod
    async def _vincularDocumentos(
        self,
        argumentoId: str,
        textoArgumento: str
    ) -> list[str]:
        """
        Busca fragmentos documentales similares al argumento en 'fragmentos_vec'.
        Extrae los documento_id únicos de los resultados que superen el umbral
        SEMANTIC_FRAGMENT_MATCH_THRESHOLD y los vincula via ArgumentoDocumento.insertarBatch.

        Args:
            argumentoId:    UUID del argumento a vincular.
            textoArgumento: Texto del argumento para el query semántico.

        Returns:
            list[str] con los documento_id vinculados.
        """
        pass