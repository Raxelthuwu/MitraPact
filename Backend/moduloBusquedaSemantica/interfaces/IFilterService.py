# Backend/moduloBusquedaSemantica/interfaces/IFilterService.py

from abc import ABC, abstractmethod


class IFilterService(ABC):
    """
    Interfaz del servicio de estadísticas y agregaciones semánticas.
    Define el contrato para consultas analíticas sobre argumentos, opiniones
    y documentos. Separado en métodos del sistema que operan con IDs directos
    y métodos del usuario que resuelven barrios por nombre internamente.
    """

    # -------------------------------------------------------------------------
    # MÉTODOS DEL SISTEMA — reciben ID directamente, los llama el backend
    # -------------------------------------------------------------------------

    @abstractmethod
    async def resumenGeneralPorBarrioId(self, barrioId: str) -> dict:
        """
        Retorna el resumen consolidado de un barrio dado su ID.
        Total opiniones, temas únicos, argumentos y frecuencia acumulada.
        Uso interno — lo llaman otros servicios, no el usuario final.

        Args:
            barrioId: UUID del barrio.

        Returns:
            dict con el resumen consolidado del barrio.
        """
        pass

    @abstractmethod
    async def temasMasRecurrentesPorBarrioId(self, barrioId: str) -> list[dict]:
        """
        Retorna los temas dominantes en las opiniones clasificadas de un barrio dado su ID.
        Uso interno — lo llaman otros servicios, no el usuario final.

        Args:
            barrioId: UUID del barrio.

        Returns:
            list[dict] con los temas y su conteo ordenados por frecuencia.
        """
        pass

    @abstractmethod
    async def argumentosPorBarrioId(self, barrioId: str, limite: int = 10) -> list[dict]:
        """
        Retorna los argumentos más frecuentes de un barrio dado su ID.
        Uso interno — lo llaman otros servicios, no el usuario final.

        Args:
            barrioId: UUID del barrio.
            limite:   Cantidad máxima de argumentos a retornar. Default 10.

        Returns:
            list[dict] con los argumentos y descripción de problemática incluida.
        """
        pass

    @abstractmethod
    async def cruzarBarrioProblematicaId(self, barrioId: str, problematicaCod: int) -> dict:
        """
        Cruza un barrio con una problemática dado el ID del barrio.
        Retorna total opiniones, argumentos y frecuencia acumulada del cruce.
        Uso interno — lo llaman otros servicios, no el usuario final.

        Args:
            barrioId:        UUID del barrio.
            problematicaCod: Código de la problemática.

        Returns:
            dict con el resultado del cruce.
        """
        pass

    @abstractmethod
    async def evolucionFrecuenciaArgumentoId(self, argumentoId: str) -> dict | None:
        """
        Retorna la frecuencia actual y tiempo activo de un argumento dado su ID.
        Útil para ver la tendencia de crecimiento de un argumento específico.
        Uso interno — lo llaman otros servicios, no el usuario final.

        Args:
            argumentoId: UUID del argumento.

        Returns:
            dict con el argumento y su evolución, o None si no existe.
        """
        pass

    # -------------------------------------------------------------------------
    # MÉTODOS DEL USUARIO — globales sin filtro de barrio
    # -------------------------------------------------------------------------

    @abstractmethod
    async def distribucionArgumentosPorProblematica(self) -> list[dict]:
        """
        Distribución global de argumentos por problemática con frecuencia acumulada.
        Vista general para dashboard — no requiere filtro de barrio.

        Returns:
            list[dict] con cada problemática, total argumentos y frecuencia acumulada.
        """
        pass

    @abstractmethod
    async def distribucionOpinionesPorBarrio(self) -> list[dict]:
        """
        Distribución global de opiniones clasificadas por barrio y tema.
        Vista macro territorial para dashboard general.

        Returns:
            list[dict] con barrio, tema y total de opiniones.
        """
        pass

    @abstractmethod
    async def distribucionOpinionesPorTema(self) -> list[dict]:
        """
        Distribución global de opiniones por tema sin filtrar por barrio.
        Permite ver qué temas dominan en toda la ciudad.

        Returns:
            list[dict] con cada tema y su total de opiniones.
        """
        pass

    @abstractmethod
    async def opinionesPorRangoFecha(self, fechaInicio: str, fechaFin: str) -> list[dict]:
        """
        Opiniones clasificadas dentro de un rango de fechas.
        Permite alinearse con los periodos estadísticos del módulo territorial.

        Args:
            fechaInicio: Fecha de inicio en formato 'YYYY-MM-DD'.
            fechaFin:    Fecha de fin en formato 'YYYY-MM-DD'.

        Returns:
            list[dict] con las opiniones clasificadas en el rango.
        """
        pass

    @abstractmethod
    async def documentosConMasArgumentos(self, limite: int = 10) -> list[dict]:
        """
        Top N documentos con más argumentos vinculados semánticamente.

        Args:
            limite: Cantidad máxima de documentos a retornar. Default 10.

        Returns:
            list[dict] con los documentos y su total de argumentos vinculados.
        """
        pass

    @abstractmethod
    async def documentosSinArgumentos(self) -> list[dict]:
        """
        Documentos indexados que el worker nunca vinculó a ningún argumento.
        Útil para auditoría y para identificar PDFs que necesitan reprocesarse.

        Returns:
            list[dict] con los documentos sin argumentos vinculados.
        """
        pass

    @abstractmethod
    async def fragmentosPorDocumentoConConteo(self) -> list[dict]:
        """
        Conteo de fragmentos por documento.
        Permite verificar si un PDF fue procesado e indexado completamente.

        Returns:
            list[dict] con cada documento y su total de fragmentos.
        """
        pass

    @abstractmethod
    async def argumentosSinDocumentoVinculado(self) -> list[dict]:
        """
        Argumentos que el worker aún no pudo vincular a ningún documento.
        Útil para auditoría y para relanzar el proceso de vinculación.

        Returns:
            list[dict] con los argumentos sin documento vinculado.
        """
        pass

    @abstractmethod
    async def argumentosMasFrecuentesPorProblematica(
        self,
        problematicaCod: int,
        limite: int = 10
    ) -> list[dict]:
        """
        Top N argumentos más frecuentes de una problemática específica.

        Args:
            problematicaCod: Código de la problemática a consultar.
            limite:          Cantidad máxima de argumentos a retornar. Default 10.

        Returns:
            list[dict] con los argumentos y descripción de problemática incluida.
        """
        pass

    @abstractmethod
    async def documentosPorProblematica(self, problematicaCod: int) -> list[dict]:
        """
        Documentos vinculados a argumentos de una problemática específica.

        Args:
            problematicaCod: Código de la problemática a consultar.

        Returns:
            list[dict] con los documentos y descripción de problemática incluida.
        """
        pass

    @abstractmethod
    async def argumentosMasFrecuentesPorTema(self, tema: str, limite: int = 10) -> list[dict]:
        """
        Top N argumentos más frecuentes de un tema usando coincidencia aproximada ILIKE.

        Args:
            tema:   Texto parcial o completo del tema a consultar.
            limite: Cantidad máxima de argumentos a retornar. Default 10.

        Returns:
            list[dict] con los argumentos y descripción de problemática incluida.
        """
        pass

    # -------------------------------------------------------------------------
    # MÉTODOS DEL USUARIO — resuelven barrio por nombre internamente
    # -------------------------------------------------------------------------

    @abstractmethod
    async def resumenGeneralPorBarrio(self, nombreBarrio: str) -> dict:
        """
        Resumen consolidado de un barrio buscado por nombre aproximado.
        Si hay varios coincidentes retorna la lista para que el usuario elija.

        Args:
            nombreBarrio: Nombre parcial o completo del barrio.

        Returns:
            dict con el resumen, o dict con 'seleccion_requerida' si hay ambigüedad.
        """
        pass

    @abstractmethod
    async def temasMasRecurrentesPorBarrio(self, nombreBarrio: str) -> dict:
        """
        Temas dominantes en las opiniones de un barrio buscado por nombre aproximado.
        Si hay varios coincidentes retorna la lista para que el usuario elija.

        Args:
            nombreBarrio: Nombre parcial o completo del barrio.

        Returns:
            dict con 'temas', o dict con 'seleccion_requerida' si hay ambigüedad.
        """
        pass

    @abstractmethod
    async def argumentosPorBarrio(self, nombreBarrio: str, limite: int = 10) -> dict:
        """
        Argumentos más frecuentes de un barrio buscado por nombre aproximado.
        Si hay varios coincidentes retorna la lista para que el usuario elija.

        Args:
            nombreBarrio: Nombre parcial o completo del barrio.
            limite:       Cantidad máxima de argumentos a retornar. Default 10.

        Returns:
            dict con 'argumentos', o dict con 'seleccion_requerida' si hay ambigüedad.
        """
        pass

    @abstractmethod
    async def cruzarBarrioProblematica(self, nombreBarrio: str, problematicaCod: int) -> dict:
        """
        Cruce de un barrio con una problemática, buscando el barrio por nombre aproximado.
        Si hay varios coincidentes retorna la lista para que el usuario elija.

        Args:
            nombreBarrio:    Nombre parcial o completo del barrio.
            problematicaCod: Código de la problemática.

        Returns:
            dict con el resultado del cruce, o dict con 'seleccion_requerida' si hay ambigüedad.
        """
        pass

    @abstractmethod
    async def opinionesPorBarrioYTema(self, nombreBarrio: str, tema: str) -> dict:
        """
        Opiniones clasificadas de un barrio filtradas por tema,
        buscando el barrio por nombre aproximado.
        Si hay varios coincidentes retorna la lista para que el usuario elija.

        Args:
            nombreBarrio: Nombre parcial o completo del barrio.
            tema:         Texto parcial o completo del tema a filtrar.

        Returns:
            dict con 'opiniones', o dict con 'seleccion_requerida' si hay ambigüedad.
        """
        pass

    @abstractmethod
    async def resumenOpinionesPorBarrio(self, nombreBarrio: str) -> dict:
        """
        Resumen de opiniones agrupadas por tema para un barrio buscado por nombre aproximado.
        Si hay varios coincidentes retorna la lista para que el usuario elija.

        Args:
            nombreBarrio: Nombre parcial o completo del barrio.

        Returns:
            dict con 'resumen', o dict con 'seleccion_requerida' si hay ambigüedad.
        """
        pass

    # -------------------------------------------------------------------------
    # PRIVADO — resolución interna de barrio
    # -------------------------------------------------------------------------

    @abstractmethod
    async def resolverBarrio(self, nombreBarrio: str) -> dict:
        """
        Busca barrios por nombre aproximado y decide si resolver el ID
        automáticamente o retornar la lista para que el usuario elija.
        Patrón compartido por todos los métodos que filtran por barrio.

        Args:
            nombreBarrio: Nombre parcial o completo del barrio.

        Returns:
            dict con 'barrioId' si hubo un solo resultado, o
            dict con 'seleccion_requerida' con la lista de barrios coincidentes.
        """
        pass