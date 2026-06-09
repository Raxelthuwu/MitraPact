# Backend/moduloBusquedaSemantica/services/filterService.py

import logging
from Backend.moduloBusquedaSemantica.models import (
    FiltroSemantico,
    Argumento,
    OpinionClasificada,
    Barrio,
)
from Backend.moduloBusquedaSemantica.interfaces import IFilterService

logger = logging.getLogger(__name__)


class FilterService(IFilterService):
    """
    Servicio de estadísticas y agregaciones semánticas.
    Orquesta consultas analíticas sobre argumentos, opiniones y documentos.
    Resuelve barrios por nombre internamente para que el usuario final
    nunca opere con IDs directos.
    """

    

    # -------------------------------------------------------------------------
    # MÉTODOS DEL SISTEMA
    # -------------------------------------------------------------------------

    async def resumenGeneralPorBarrioId(self, barrioId: str) -> dict:
        """
        Retorna el resumen consolidado de un barrio dado su ID.
        Uso interno — lo llaman otros servicios, no el usuario final.

        Args:
            barrioId: UUID del barrio.

        Returns:
            dict con el resumen consolidado del barrio.
        """
        logger.info(f"[FilterService] Resumen general para barrio_id: '{barrioId}'")
        try:
            return await FiltroSemantico.resumenGeneralPorBarrio(barrioId)
        except Exception as e:
            logger.error(f"[FilterService] Error en resumenGeneralPorBarrioId: {e}")
            raise

    async def temasMasRecurrentesPorBarrioId(self, barrioId: str) -> list[dict]:
        """
        Retorna los temas dominantes en las opiniones de un barrio dado su ID.
        Uso interno — lo llaman otros servicios, no el usuario final.

        Args:
            barrioId: UUID del barrio.

        Returns:
            list[dict] con los temas y su conteo ordenados por frecuencia.
        """
        logger.info(f"[FilterService] Temas recurrentes para barrio_id: '{barrioId}'")
        try:
            return await FiltroSemantico.temasMasRecurrentesPorBarrio(barrioId)
        except Exception as e:
            logger.error(f"[FilterService] Error en temasMasRecurrentesPorBarrioId: {e}")
            raise

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
        logger.info(f"[FilterService] Argumentos para barrio_id: '{barrioId}'")
        try:
            return await FiltroSemantico.argumentosPorBarrio(barrioId, limite)
        except Exception as e:
            logger.error(f"[FilterService] Error en argumentosPorBarrioId: {e}")
            raise

    async def cruzarBarrioProblematicaId(self, barrioId: str, problematicaCod: int) -> dict:
        """
        Cruza un barrio con una problemática dado el ID del barrio.
        Uso interno — lo llaman otros servicios, no el usuario final.

        Args:
            barrioId:        UUID del barrio.
            problematicaCod: Código de la problemática.

        Returns:
            dict con el resultado del cruce.
        """
        logger.info(f"[FilterService] Cruce barrio_id: '{barrioId}' x problematica_cod: {problematicaCod}")
        try:
            return await FiltroSemantico.cruzarBarrioProblematica(barrioId, problematicaCod)
        except Exception as e:
            logger.error(f"[FilterService] Error en cruzarBarrioProblematicaId: {e}")
            raise

    async def evolucionFrecuenciaArgumentoId(self, argumentoId: str) -> dict | None:
        """
        Retorna la frecuencia actual y tiempo activo de un argumento dado su ID.
        Uso interno — lo llaman otros servicios, no el usuario final.

        Args:
            argumentoId: UUID del argumento.

        Returns:
            dict con el argumento y su evolución, o None si no existe.
        """
        logger.info(f"[FilterService] Evolución de frecuencia para argumento_id: '{argumentoId}'")
        try:
            return await FiltroSemantico.evolucionFrecuenciaArgumento(argumentoId)
        except Exception as e:
            logger.error(f"[FilterService] Error en evolucionFrecuenciaArgumentoId: {e}")
            raise

    # -------------------------------------------------------------------------
    # MÉTODOS DEL USUARIO — globales sin filtro de barrio
    # -------------------------------------------------------------------------

    async def distribucionArgumentosPorProblematica(self) -> list[dict]:
        """
        Distribución global de argumentos por problemática con frecuencia acumulada.

        Returns:
            list[dict] con cada problemática, total argumentos y frecuencia acumulada.
        """
        logger.info("[FilterService] Distribución de argumentos por problemática.")
        try:
            return await FiltroSemantico.distribucionArgumentosPorProblematica()
        except Exception as e:
            logger.error(f"[FilterService] Error en distribucionArgumentosPorProblematica: {e}")
            raise

    async def distribucionOpinionesPorBarrio(self) -> list[dict]:
        """
        Distribución global de opiniones clasificadas por barrio y tema.

        Returns:
            list[dict] con barrio, tema y total de opiniones.
        """
        logger.info("[FilterService] Distribución de opiniones por barrio.")
        try:
            return await FiltroSemantico.distribucionOpinionesPorBarrio()
        except Exception as e:
            logger.error(f"[FilterService] Error en distribucionOpinionesPorBarrio: {e}")
            raise

    async def distribucionOpinionesPorTema(self) -> list[dict]:
        """
        Distribución global de opiniones por tema sin filtrar por barrio.

        Returns:
            list[dict] con cada tema y su total de opiniones.
        """
        logger.info("[FilterService] Distribución global de opiniones por tema.")
        try:
            return await FiltroSemantico.distribucionOpinionesPorTema()
        except Exception as e:
            logger.error(f"[FilterService] Error en distribucionOpinionesPorTema: {e}")
            raise

    async def opinionesPorRangoFecha(self, fechaInicio: str, fechaFin: str) -> list[dict]:
        """
        Opiniones clasificadas dentro de un rango de fechas.

        Args:
            fechaInicio: Fecha de inicio en formato 'YYYY-MM-DD'.
            fechaFin:    Fecha de fin en formato 'YYYY-MM-DD'.

        Returns:
            list[dict] con las opiniones clasificadas en el rango.
        """
        logger.info(f"[FilterService] Opiniones entre {fechaInicio} y {fechaFin}")
        try:
            return await FiltroSemantico.opinionesPorRangoFecha(fechaInicio, fechaFin)
        except Exception as e:
            logger.error(f"[FilterService] Error en opinionesPorRangoFecha: {e}")
            raise

    async def documentosConMasArgumentos(self, limite: int = 10) -> list[dict]:
        """
        Top N documentos con más argumentos vinculados semánticamente.

        Args:
            limite: Cantidad máxima de documentos a retornar. Default 10.

        Returns:
            list[dict] con los documentos y su total de argumentos vinculados.
        """
        logger.info(f"[FilterService] Top {limite} documentos con más argumentos.")
        try:
            return await FiltroSemantico.documentosConMasArgumentos(limite)
        except Exception as e:
            logger.error(f"[FilterService] Error en documentosConMasArgumentos: {e}")
            raise

    async def documentosSinArgumentos(self) -> list[dict]:
        """
        Documentos indexados que el worker nunca vinculó a ningún argumento.

        Returns:
            list[dict] con los documentos sin argumentos vinculados.
        """
        logger.info("[FilterService] Documentos sin argumentos vinculados.")
        try:
            return await FiltroSemantico.documentosSinArgumentos()
        except Exception as e:
            logger.error(f"[FilterService] Error en documentosSinArgumentos: {e}")
            raise

    async def fragmentosPorDocumentoConConteo(self) -> list[dict]:
        """
        Conteo de fragmentos por documento.

        Returns:
            list[dict] con cada documento y su total de fragmentos.
        """
        logger.info("[FilterService] Conteo de fragmentos por documento.")
        try:
            return await FiltroSemantico.fragmentosPorDocumentoConConteo()
        except Exception as e:
            logger.error(f"[FilterService] Error en fragmentosPorDocumentoConConteo: {e}")
            raise

    async def argumentosSinDocumentoVinculado(self) -> list[dict]:
        """
        Argumentos que el worker aún no pudo vincular a ningún documento.

        Returns:
            list[dict] con los argumentos sin documento vinculado.
        """
        logger.info("[FilterService] Argumentos sin documento vinculado.")
        try:
            return await FiltroSemantico.argumentosSinDocumentoVinculado()
        except Exception as e:
            logger.error(f"[FilterService] Error en argumentosSinDocumentoVinculado: {e}")
            raise

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
        logger.info(f"[FilterService] Top {limite} argumentos para problematica_cod: {problematicaCod}")
        try:
            return await FiltroSemantico.argumentosMasFrecuentesPorProblematica(problematicaCod, limite)
        except Exception as e:
            logger.error(f"[FilterService] Error en argumentosMasFrecuentesPorProblematica: {e}")
            raise

    async def documentosPorProblematica(self, problematicaCod: int) -> list[dict]:
        """
        Documentos vinculados a argumentos de una problemática específica.

        Args:
            problematicaCod: Código de la problemática a consultar.

        Returns:
            list[dict] con los documentos y descripción de problemática incluida.
        """
        logger.info(f"[FilterService] Documentos para problematica_cod: {problematicaCod}")
        try:
            return await FiltroSemantico.documentosPorProblematica(problematicaCod)
        except Exception as e:
            logger.error(f"[FilterService] Error en documentosPorProblematica: {e}")
            raise

    async def argumentosMasFrecuentesPorTema(self, tema: str, limite: int = 10) -> list[dict]:
        """
        Top N argumentos más frecuentes de un tema usando coincidencia aproximada ILIKE.

        Args:
            tema:   Texto parcial o completo del tema a consultar.
            limite: Cantidad máxima de argumentos a retornar. Default 10.

        Returns:
            list[dict] con los argumentos y descripción de problemática incluida.
        """
        logger.info(f"[FilterService] Top {limite} argumentos para tema: '{tema}'")
        try:
            return await Argumento.listarMasFrecuentesPorTema(tema, limite)
        except Exception as e:
            logger.error(f"[FilterService] Error en argumentosMasFrecuentesPorTema: {e}")
            raise

    # -------------------------------------------------------------------------
    # MÉTODOS DEL USUARIO — resuelven barrio por nombre internamente
    # -------------------------------------------------------------------------

    async def resumenGeneralPorBarrio(self, nombreBarrio: str) -> dict:
        """
        Resumen consolidado de un barrio buscado por nombre aproximado.

        Args:
            nombreBarrio: Nombre parcial o completo del barrio.

        Returns:
            dict con el resumen, o dict con 'seleccion_requerida' si hay ambigüedad.
        """
        logger.info(f"[FilterService] Resumen general para barrio: '{nombreBarrio}'")
        try:
            resolucion = await self.resolverBarrio(nombreBarrio)
            if 'seleccion_requerida' in resolucion:
                return resolucion
            return await FiltroSemantico.resumenGeneralPorBarrio(resolucion['barrioId'])
        except Exception as e:
            logger.error(f"[FilterService] Error en resumenGeneralPorBarrio: {e}")
            raise

    async def temasMasRecurrentesPorBarrio(self, nombreBarrio: str) -> dict:
        """
        Temas dominantes en las opiniones de un barrio buscado por nombre aproximado.

        Args:
            nombreBarrio: Nombre parcial o completo del barrio.

        Returns:
            dict con 'temas', o dict con 'seleccion_requerida' si hay ambigüedad.
        """
        logger.info(f"[FilterService] Temas recurrentes para barrio: '{nombreBarrio}'")
        try:
            resolucion = await self.resolverBarrio(nombreBarrio)
            if 'seleccion_requerida' in resolucion:
                return resolucion
            temas = await FiltroSemantico.temasMasRecurrentesPorBarrio(resolucion['barrioId'])
            return {'temas': temas}
        except Exception as e:
            logger.error(f"[FilterService] Error en temasMasRecurrentesPorBarrio: {e}")
            raise

    async def argumentosPorBarrio(self, nombreBarrio: str, limite: int = 10) -> dict:
        """
        Argumentos más frecuentes de un barrio buscado por nombre aproximado.

        Args:
            nombreBarrio: Nombre parcial o completo del barrio.
            limite:       Cantidad máxima de argumentos a retornar. Default 10.

        Returns:
            dict con 'argumentos', o dict con 'seleccion_requerida' si hay ambigüedad.
        """
        logger.info(f"[FilterService] Argumentos para barrio: '{nombreBarrio}'")
        try:
            resolucion = await self.resolverBarrio(nombreBarrio)
            if 'seleccion_requerida' in resolucion:
                return resolucion
            argumentos = await FiltroSemantico.argumentosPorBarrio(resolucion['barrioId'], limite)
            return {'argumentos': argumentos}
        except Exception as e:
            logger.error(f"[FilterService] Error en argumentosPorBarrio: {e}")
            raise

    async def cruzarBarrioProblematica(self, nombreBarrio: str, problematicaCod: int) -> dict:
        """
        Cruce de un barrio con una problemática, buscando el barrio por nombre aproximado.

        Args:
            nombreBarrio:    Nombre parcial o completo del barrio.
            problematicaCod: Código de la problemática.

        Returns:
            dict con el resultado del cruce, o dict con 'seleccion_requerida' si hay ambigüedad.
        """
        logger.info(f"[FilterService] Cruce barrio: '{nombreBarrio}' x problematica_cod: {problematicaCod}")
        try:
            resolucion = await self.resolverBarrio(nombreBarrio)
            if 'seleccion_requerida' in resolucion:
                return resolucion
            return await FiltroSemantico.cruzarBarrioProblematica(resolucion['barrioId'], problematicaCod)
        except Exception as e:
            logger.error(f"[FilterService] Error en cruzarBarrioProblematica: {e}")
            raise

    async def opinionesPorBarrioYTema(self, nombreBarrio: str, tema: str) -> dict:
        """
        Opiniones de un barrio filtradas por tema, buscando el barrio por nombre aproximado.

        Args:
            nombreBarrio: Nombre parcial o completo del barrio.
            tema:         Texto parcial o completo del tema a filtrar.

        Returns:
            dict con 'opiniones', o dict con 'seleccion_requerida' si hay ambigüedad.
        """
        logger.info(f"[FilterService] Opiniones para barrio: '{nombreBarrio}' y tema: '{tema}'")
        try:
            resolucion = await self.resolverBarrio(nombreBarrio)
            if 'seleccion_requerida' in resolucion:
                return resolucion
            opiniones = await OpinionClasificada.buscarPorBarrioYTema(resolucion['barrioId'], tema)
            return {'opiniones': opiniones}
        except Exception as e:
            logger.error(f"[FilterService] Error en opinionesPorBarrioYTema: {e}")
            raise

    async def resumenOpinionesPorBarrio(self, nombreBarrio: str) -> dict:
        """
        Resumen de opiniones agrupadas por tema para un barrio buscado por nombre aproximado.

        Args:
            nombreBarrio: Nombre parcial o completo del barrio.

        Returns:
            dict con 'resumen', o dict con 'seleccion_requerida' si hay ambigüedad.
        """
        logger.info(f"[FilterService] Resumen de opiniones para barrio: '{nombreBarrio}'")
        try:
            resolucion = await self.resolverBarrio(nombreBarrio)
            if 'seleccion_requerida' in resolucion:
                return resolucion
            resumen = await OpinionClasificada.resumenPorBarrio(resolucion['barrioId'])
            return {'resumen': resumen}
        except Exception as e:
            logger.error(f"[FilterService] Error en resumenOpinionesPorBarrio: {e}")
            raise

    # -------------------------------------------------------------------------
    # PRIVADO
    # -------------------------------------------------------------------------

    async def resolverBarrio(self, nombreBarrio: str) -> dict:
        """
        Busca barrios por nombre aproximado y decide si resolver el ID
        automáticamente o retornar la lista para que el usuario elija.

        Args:
            nombreBarrio: Nombre parcial o completo del barrio.

        Returns:
            dict con 'barrioId' si hubo un solo resultado, o
            dict con 'seleccion_requerida' con la lista de barrios coincidentes.
        """
        barrios = await Barrio.buscarPorNombre(nombreBarrio)

        if not barrios:
            logger.warning(f"[FilterService] Sin resultados para barrio: '{nombreBarrio}'")
            return {'seleccion_requerida': []}

        if len(barrios) > 1:
            logger.info(f"[FilterService] Múltiples barrios encontrados — selección requerida.")
            return {'seleccion_requerida': barrios}

        return {'barrioId': barrios[0]['id']}
    

    async def listarProblematicas(self) -> list[dict]:
        logger.info("[FilterService] Listando catálogo de problemáticas.")
        try:
            return await FiltroSemantico.listarProblematicas()
        except Exception as e:
            logger.error(f"[FilterService] Error en listarProblematicas: {e}")
            raise

    async def listarOpinionesPorBarrio(self, nombreBarrio: str) -> dict:
        """
        Lista todas las opiniones individuales de un barrio con texto completo.
        Usado por el selector del modal crear/editar argumento.

        Args:
            nombreBarrio: Nombre parcial o completo del barrio.

        Returns:
            dict con 'opiniones' y 'barrioId', o dict con 'seleccion_requerida'.
        """
        logger.info(f"[FilterService] Listando opiniones para barrio: '{nombreBarrio}'")
        try:
            resolucion = await self.resolverBarrio(nombreBarrio)
            if 'seleccion_requerida' in resolucion:
                return resolucion
            opiniones = await OpinionClasificada.listarPorBarrio(resolucion['barrioId'])
            return {'opiniones': opiniones, 'barrioId': resolucion['barrioId']}
        except Exception as e:
            logger.error(f"[FilterService] Error en listarOpinionesPorBarrio: {e}")
            raise

    async def obtenerCruceBarrioProblematica(self, barrioId: str, problematicaCod: int) -> list[dict]:
        """
        Consulta SQL para cruzar Barrio y Problematica.
        """
        logger.info(f"[FilterService] Ejecutando cruce real para barrio: {barrioId} y prob: {problematicaCod}")
        
        # Esta es la consulta que faltaba en tu servicio
        sql = f"""
            SELECT a.texto, a.frecuencia, a.tema
            FROM busqueda_semantica.argumento a
            JOIN busqueda_semantica.opinion_clasificada o ON a.opinion_id = o.id
            WHERE o.barrio_id = %s 
            AND a.problematica_cod = %s
        """
        
        # Debes usar el helper _query que ya tienes en otros archivos
        # Nota: Asegúrate de importar el helper _query o ejecutar la consulta vía FiltroSemantico
        try:
            from Backend.moduloBusquedaSemantica.models.filtros import _query
            return await _query(sql, [barrioId, int(problematicaCod)], fetchall=True)
        except Exception as e:
            logger.error(f"[FilterService] Error en el cruce: {e}")
            return []