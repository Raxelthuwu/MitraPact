# Backend/moduloBusquedaSemantica/services/busquedaService.py

import logging
from Backend.moduloBusquedaSemantica.models import (
    Documento,
    Fragmento,
    TemaDocumento,
    ArgumentoDocumento,
)
from Backend.moduloBusquedaSemantica.interfaces import IBusquedaService


logger = logging.getLogger(__name__)


class BusquedaService(IBusquedaService):
    """
    Servicio de búsqueda y navegación documental orientado al usuario.
    Resuelve IDs internamente a partir de nombres o textos para que el
    usuario final nunca tenga que operar con identificadores directos.
    Los métodos del sistema exponen IDs para uso exclusivo del backend.
    """

    # -------------------------------------------------------------------------
    # MÉTODOS DEL SISTEMA
    # -------------------------------------------------------------------------

    async def obtenerFragmentosPorDocumentoId(self, documentoId: str) -> list[dict]:
        """
        Retorna todos los fragmentos de un documento dado su ID.
        Uso interno — lo llaman otros servicios, no el usuario final.

        Args:
            documentoId: UUID del documento.

        Returns:
            list[dict] con los fragmentos y nombre del documento incluido.
        """
        logger.info(f"[BusquedaService] Obteniendo fragmentos para documento_id: '{documentoId}'")
        try:
            return await Fragmento.listarPorDocumentoConNombre(documentoId)
        except Exception as e:
            logger.error(f"[BusquedaService] Error en obtenerFragmentosPorDocumentoId: {e}")
            raise

    async def obtenerFragmentoPorPaginaId(self, documentoId: str, pagina: int) -> dict | None:
        """
        Retorna el fragmento de una página específica dado el ID del documento.
        Uso interno — lo llaman otros servicios, no el usuario final.

        Args:
            documentoId: UUID del documento.
            pagina:      Número de página a recuperar.

        Returns:
            dict con el fragmento, o None si no existe.
        """
        logger.info(f"[BusquedaService] Obteniendo fragmento pág {pagina} para documento_id: '{documentoId}'")
        try:
            return await Fragmento.buscarPorPagina(documentoId, pagina)
        except Exception as e:
            logger.error(f"[BusquedaService] Error en obtenerFragmentoPorPaginaId: {e}")
            raise

    async def listarDocumentosDeArgumentoId(self, argumentoId: str) -> list[dict]:
        """
        Retorna los documentos vinculados a un argumento dado su ID.
        Uso interno — lo llaman otros servicios, no el usuario final.

        Args:
            argumentoId: UUID del argumento.

        Returns:
            list[dict] con los documentos vinculados con nombre legible.
        """
        logger.info(f"[BusquedaService] Listando documentos para argumento_id: '{argumentoId}'")
        try:
            return await ArgumentoDocumento.listarDocumentosDeArgumento(argumentoId)
        except Exception as e:
            logger.error(f"[BusquedaService] Error en listarDocumentosDeArgumentoId: {e}")
            raise

    async def listarArgumentosDeDocumentoId(self, documentoId: str) -> list[dict]:
        """
        Retorna los argumentos vinculados a un documento dado su ID.
        Uso interno — lo llaman otros servicios, no el usuario final.

        Args:
            documentoId: UUID del documento.

        Returns:
            list[dict] con los argumentos y descripción de problemática incluida.
        """
        logger.info(f"[BusquedaService] Listando argumentos para documento_id: '{documentoId}'")
        try:
            return await ArgumentoDocumento.listarArgumentosDeDocumento(documentoId)
        except Exception as e:
            logger.error(f"[BusquedaService] Error en listarArgumentosDeDocumentoId: {e}")
            raise

    # -------------------------------------------------------------------------
    # MÉTODOS DEL USUARIO
    # -------------------------------------------------------------------------

    async def buscarDocumentosPorNombre(self, nombre: str) -> list[dict]:
        """
        Busca documentos por nombre usando coincidencia aproximada ILIKE.

        Args:
            nombre: Texto parcial o completo del nombre del documento.

        Returns:
            list[dict] con los documentos que coinciden.
        """
        logger.info(f"[BusquedaService] Buscando documentos por nombre: '{nombre}'")
        try:
            return await Documento.buscarPorNombre(nombre)
        except Exception as e:
            logger.error(f"[BusquedaService] Error en buscarDocumentosPorNombre: {e}")
            raise

    async def buscarDocumentosPorFecha(self, fechaInicio: str, fechaFin: str) -> list[dict]:
        """
        Busca documentos registrados dentro de un rango de fechas.

        Args:
            fechaInicio: Fecha de inicio en formato 'YYYY-MM-DD'.
            fechaFin:    Fecha de fin en formato 'YYYY-MM-DD'.

        Returns:
            list[dict] con los documentos dentro del rango.
        """
        logger.info(f"[BusquedaService] Buscando documentos entre {fechaInicio} y {fechaFin}")
        try:
            return await Documento.buscarPorRangoFecha(fechaInicio, fechaFin)
        except Exception as e:
            logger.error(f"[BusquedaService] Error en buscarDocumentosPorFecha: {e}")
            raise

    async def listarDocumentosConTemas(self) -> list[dict]:
        """
        Lista todos los documentos del sistema con sus temas asociados agrupados.

        Returns:
            list[dict] con cada documento y su lista de temas.
        """
        logger.info("[BusquedaService] Listando todos los documentos con temas.")
        try:
            return await Documento.listarConTemas()
        except Exception as e:
            logger.error(f"[BusquedaService] Error en listarDocumentosConTemas: {e}")
            raise

    async def buscarDocumentosPorNombreConTemas(self, nombre: str) -> list[dict]:
        """
        Busca documentos por nombre aproximado e incluye sus temas agrupados.

        Args:
            nombre: Texto parcial o completo del nombre del documento.

        Returns:
            list[dict] con los documentos coincidentes y sus temas agrupados.
        """
        logger.info(f"[BusquedaService] Buscando documentos con temas por nombre: '{nombre}'")
        try:
            return await TemaDocumento.listarDocumentosConTemasPorNombre(nombre)
        except Exception as e:
            logger.error(f"[BusquedaService] Error en buscarDocumentosPorNombreConTemas: {e}")
            raise

    async def listarTemas(self) -> list[str]:
        """
        Retorna todos los temas únicos registrados en el sistema.

        Returns:
            list[str] con los temas únicos ordenados alfabéticamente.
        """
        logger.info("[BusquedaService] Listando temas únicos.")
        try:
            return await TemaDocumento.listarTemasUnicos()
        except Exception as e:
            logger.error(f"[BusquedaService] Error en listarTemas: {e}")
            raise

    async def buscarDocumentosPorTema(self, tema: str) -> list[dict]:
        """
        Busca documentos que traten un tema usando coincidencia aproximada ILIKE.

        Args:
            tema: Texto parcial o completo del tema a buscar.

        Returns:
            list[dict] con los documentos que coinciden con el tema.
        """
        logger.info(f"[BusquedaService] Buscando documentos por tema: '{tema}'")
        try:
            return await TemaDocumento.buscarDocumentosPorTema(tema)
        except Exception as e:
            logger.error(f"[BusquedaService] Error en buscarDocumentosPorTema: {e}")
            raise

    async def obtenerFragmentosPorDocumento(self, nombreDocumento: str) -> dict:
        """
        Busca fragmentos de un documento a partir de su nombre.
        Si hay un solo coincidente resuelve el ID y retorna fragmentos.
        Si hay varios retorna la lista para que el usuario elija.

        Args:
            nombreDocumento: Nombre parcial o completo del documento.

        Returns:
            dict con 'fragmentos' si hubo un solo resultado, o
            dict con 'seleccion_requerida' con la lista de documentos coincidentes.
        """
        logger.info(f"[BusquedaService] Obteniendo fragmentos por nombre de documento: '{nombreDocumento}'")
        try:
            documentos = await Documento.buscarPorNombre(nombreDocumento)

            if not documentos:
                logger.warning(f"[BusquedaService] Sin resultados para nombre: '{nombreDocumento}'")
                return {'fragmentos': []}

            if len(documentos) > 1:
                logger.info(f"[BusquedaService] Múltiples documentos encontrados — selección requerida.")
                return {'seleccion_requerida': documentos}

            documentoId = documentos[0]['id']
            fragmentos  = await Fragmento.listarPorDocumentoConNombre(documentoId)
            return {'fragmentos': fragmentos}

        except Exception as e:
            logger.error(f"[BusquedaService] Error en obtenerFragmentosPorDocumento: {e}")
            raise

    async def obtenerFragmentoPorPagina(self, nombreDocumento: str, pagina: int) -> dict:
        """
        Retorna el fragmento de una página específica buscando el documento por nombre.
        Si hay varios coincidentes retorna la lista para que el usuario elija.

        Args:
            nombreDocumento: Nombre parcial o completo del documento.
            pagina:          Número de página a recuperar.

        Returns:
            dict con 'fragmento' si hubo un solo resultado, o
            dict con 'seleccion_requerida' con la lista de documentos coincidentes.
        """
        logger.info(f"[BusquedaService] Obteniendo fragmento pág {pagina} para documento: '{nombreDocumento}'")
        try:
            documentos = await Documento.buscarPorNombre(nombreDocumento)

            if not documentos:
                logger.warning(f"[BusquedaService] Sin resultados para nombre: '{nombreDocumento}'")
                return {'fragmento': None}

            if len(documentos) > 1:
                logger.info(f"[BusquedaService] Múltiples documentos encontrados — selección requerida.")
                return {'seleccion_requerida': documentos}

            documentoId = documentos[0]['id']
            fragmento   = await Fragmento.buscarPorPagina(documentoId, pagina)
            return {'fragmento': fragmento}

        except Exception as e:
            logger.error(f"[BusquedaService] Error en obtenerFragmentoPorPagina: {e}")
            raise

    async def buscarFragmentosPorTexto(self, nombreDocumento: str, texto: str) -> dict:
        """
        Busca fragmentos que contengan un texto exacto dentro de un documento
        identificado por nombre aproximado.
        Si hay varios coincidentes retorna la lista para que el usuario elija.

        Args:
            nombreDocumento: Nombre parcial o completo del documento.
            texto:           Texto a buscar dentro del contenido de los fragmentos.

        Returns:
            dict con 'fragmentos' si hubo un solo resultado, o
            dict con 'seleccion_requerida' con la lista de documentos coincidentes.
        """
        logger.info(f"[BusquedaService] Buscando texto '{texto}' en documento: '{nombreDocumento}'")
        try:
            documentos = await Documento.buscarPorNombre(nombreDocumento)

            if not documentos:
                logger.warning(f"[BusquedaService] Sin resultados para nombre: '{nombreDocumento}'")
                return {'fragmentos': []}

            if len(documentos) > 1:
                logger.info(f"[BusquedaService] Múltiples documentos encontrados — selección requerida.")
                return {'seleccion_requerida': documentos}

            documentoId = documentos[0]['id']
            fragmentos  = await Fragmento.buscarContenidoPorTexto(documentoId, texto)
            return {'fragmentos': fragmentos}

        except Exception as e:
            logger.error(f"[BusquedaService] Error en buscarFragmentosPorTexto: {e}")
            raise

    async def listarArgumentosDeDocumento(self, nombreDocumento: str) -> dict:
        """
        Lista los argumentos vinculados a un documento identificado por nombre aproximado.
        Si hay varios coincidentes retorna la lista para que el usuario elija.

        Args:
            nombreDocumento: Nombre parcial o completo del documento.

        Returns:
            dict con 'argumentos' si hubo un solo resultado, o
            dict con 'seleccion_requerida' con la lista de documentos coincidentes.
        """
        logger.info(f"[BusquedaService] Listando argumentos para documento: '{nombreDocumento}'")
        try:
            documentos = await Documento.buscarPorNombre(nombreDocumento)

            if not documentos:
                logger.warning(f"[BusquedaService] Sin resultados para nombre: '{nombreDocumento}'")
                return {'argumentos': []}

            if len(documentos) > 1:
                logger.info(f"[BusquedaService] Múltiples documentos encontrados — selección requerida.")
                return {'seleccion_requerida': documentos}

            documentoId = documentos[0]['id']
            argumentos  = await ArgumentoDocumento.listarArgumentosDeDocumento(documentoId)
            return {'argumentos': argumentos}

        except Exception as e:
            logger.error(f"[BusquedaService] Error en listarArgumentosDeDocumento: {e}")
            raise