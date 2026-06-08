# Backend/moduloBusquedaSemantica/interfaces/IBusquedaService.py

from abc import ABC, abstractmethod


class IBusquedaService(ABC):
    """
    Interfaz del servicio de búsqueda y navegación documental.
    Define el contrato para consultas orientadas al usuario sin exposición
    de IDs, y métodos internos para uso del sistema con IDs directos.
    Toda la resolución de identificadores se maneja internamente en la implementación.
    """

    # -------------------------------------------------------------------------
    # MÉTODOS DEL SISTEMA — reciben ID directamente, los llama el backend
    # -------------------------------------------------------------------------

    @abstractmethod
    async def obtenerFragmentosPorDocumentoId(self, documentoId: str) -> list[dict]:
        """
        Retorna todos los fragmentos de un documento dado su ID.
        Uso interno — lo llaman otros servicios, no el usuario final.

        Args:
            documentoId: UUID del documento.

        Returns:
            list[dict] con los fragmentos y nombre del documento incluido.
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    async def listarDocumentosDeArgumentoId(self, argumentoId: str) -> list[dict]:
        """
        Retorna los documentos vinculados a un argumento dado su ID.
        Uso interno — lo llaman otros servicios, no el usuario final.

        Args:
            argumentoId: UUID del argumento.

        Returns:
            list[dict] con los documentos vinculados con nombre legible.
        """
        pass

    @abstractmethod
    async def listarArgumentosDeDocumentoId(self, documentoId: str) -> list[dict]:
        """
        Retorna los argumentos vinculados a un documento dado su ID.
        Uso interno — lo llaman otros servicios, no el usuario final.

        Args:
            documentoId: UUID del documento.

        Returns:
            list[dict] con los argumentos y descripción de problemática incluida.
        """
        pass

    # -------------------------------------------------------------------------
    # MÉTODOS DEL USUARIO — sin IDs, el servicio los resuelve internamente
    # -------------------------------------------------------------------------

    @abstractmethod
    async def buscarDocumentosPorNombre(self, nombre: str) -> list[dict]:
        """
        Busca documentos por nombre usando coincidencia aproximada ILIKE.
        El usuario escribe un término parcial y recibe la lista de coincidencias.

        Args:
            nombre: Texto parcial o completo del nombre del documento.

        Returns:
            list[dict] con los documentos que coinciden.
        """
        pass

    @abstractmethod
    async def buscarDocumentosPorFecha(self, fechaInicio: str, fechaFin: str) -> list[dict]:
        """
        Busca documentos registrados dentro de un rango de fechas.

        Args:
            fechaInicio: Fecha de inicio del rango en formato 'YYYY-MM-DD'.
            fechaFin:    Fecha de fin del rango en formato 'YYYY-MM-DD'.

        Returns:
            list[dict] con los documentos dentro del rango.
        """
        pass

    @abstractmethod
    async def listarDocumentosConTemas(self) -> list[dict]:
        """
        Lista todos los documentos del sistema con sus temas asociados agrupados.
        Permite al usuario explorar el catálogo completo con contexto temático.

        Returns:
            list[dict] con cada documento y su lista de temas.
        """
        pass

    @abstractmethod
    async def buscarDocumentosPorNombreConTemas(self, nombre: str) -> list[dict]:
        """
        Busca documentos por nombre aproximado e incluye sus temas agrupados.
        Combina filtro por nombre con el contexto temático del documento.

        Args:
            nombre: Texto parcial o completo del nombre del documento.

        Returns:
            list[dict] con los documentos coincidentes y sus temas agrupados.
        """
        pass

    @abstractmethod
    async def listarTemas(self) -> list[str]:
        """
        Retorna todos los temas únicos registrados en el sistema.
        Útil para alimentar selectores o filtros en el frontend.

        Returns:
            list[str] con los temas únicos ordenados alfabéticamente.
        """
        pass

    @abstractmethod
    async def buscarDocumentosPorTema(self, tema: str) -> list[dict]:
        """
        Busca documentos que traten un tema usando coincidencia aproximada ILIKE.

        Args:
            tema: Texto parcial o completo del tema a buscar.

        Returns:
            list[dict] con los documentos que coinciden con el tema.
        """
        pass

    @abstractmethod
    async def obtenerFragmentosPorDocumento(self, nombreDocumento: str) -> dict:
        """
        Busca fragmentos de un documento a partir de su nombre.
        Si hay un solo documento coincidente resuelve el ID internamente y
        retorna los fragmentos directamente.
        Si hay varios coincidentes retorna la lista para que el usuario elija.

        Args:
            nombreDocumento: Nombre parcial o completo del documento.

        Returns:
            dict con 'fragmentos' si hubo un solo resultado, o
            dict con 'seleccion_requerida' con la lista de documentos coincidentes.
        """
        pass

    @abstractmethod
    async def obtenerFragmentoPorPagina(self, nombreDocumento: str, pagina: int) -> dict:
        """
        Retorna el fragmento de una página específica buscando el documento por nombre.
        Si hay varios documentos coincidentes retorna la lista para que el usuario elija.

        Args:
            nombreDocumento: Nombre parcial o completo del documento.
            pagina:          Número de página a recuperar.

        Returns:
            dict con 'fragmento' si hubo un solo resultado, o
            dict con 'seleccion_requerida' con la lista de documentos coincidentes.
        """
        pass

    @abstractmethod
    async def buscarFragmentosPorTexto(self, nombreDocumento: str, texto: str) -> dict:
        """
        Busca fragmentos que contengan un texto exacto dentro de un documento
        identificado por nombre aproximado.
        Si hay varios documentos coincidentes retorna la lista para que el usuario elija.

        Args:
            nombreDocumento: Nombre parcial o completo del documento.
            texto:           Texto a buscar dentro del contenido de los fragmentos.

        Returns:
            dict con 'fragmentos' si hubo un solo resultado, o
            dict con 'seleccion_requerida' con la lista de documentos coincidentes.
        """
        pass

    @abstractmethod
    async def listarArgumentosDeDocumento(self, nombreDocumento: str) -> dict:
        """
        Lista los argumentos vinculados a un documento identificado por nombre aproximado.
        Si hay varios documentos coincidentes retorna la lista para que el usuario elija.

        Args:
            nombreDocumento: Nombre parcial o completo del documento.

        Returns:
            dict con 'argumentos' si hubo un solo resultado, o
            dict con 'seleccion_requerida' con la lista de documentos coincidentes.
        """
        pass