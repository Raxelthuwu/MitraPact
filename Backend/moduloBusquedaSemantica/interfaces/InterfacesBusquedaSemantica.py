from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


# Gestión Documental

class IDocumentoService(ABC):

    @abstractmethod
    async def registrarDocumento(self, nombre: str, nombre_archivo: str) -> Dict[str, Any]:
        # Registrar un nuevo documento PDF y retornar sus datos
        # RF-SEM-01
        pass

    @abstractmethod
    async def obtenerDocumentoPorId(self, documento_id: str) -> Optional[Dict[str, Any]]:
        # Recuperar un documento por su UUID
        pass

    @abstractmethod
    async def listarDocumentos(self) -> List[Dict[str, Any]]:
        # Retornar todos los documentos registrados
        pass

    @abstractmethod
    async def actualizarDocumento(self, documento_id: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        # Actualizar nombre o nombre_archivo de un documento existente
        # RF-SEM-03
        pass

    @abstractmethod
    async def eliminarDocumento(self, documento_id: str) -> bool:
        # Eliminar un documento; retorna True si la operación fue exitosa
        pass


class IFragmentoService(ABC):

    @abstractmethod
    async def indexarFragmento(
        self,
        documento_id: str,
        pagina: int,
        contenido: str,
        vector_id: Optional[str],
    ) -> Dict[str, Any]:
        # Indexar un fragmento textual extraído de un documento
        # RF-SEM-02
        pass

    @abstractmethod
    async def obtenerFragmentosPorDocumento(self, documento_id: str) -> List[Dict[str, Any]]:
        # Retornar todos los fragmentos asociados a un documento
        pass

    @abstractmethod
    async def obtenerFragmentoPorId(self, fragmento_id: str) -> Optional[Dict[str, Any]]:
        # Recuperar un fragmento por su UUID
        pass

    @abstractmethod
    async def eliminarFragmentosPorDocumento(self, documento_id: str) -> int:
        # Eliminar todos los fragmentos de un documento; retorna cantidad eliminada
        # RF-SEM-03
        pass

    @abstractmethod
    async def recuperarFragmentosRelevantes(
        self, consulta: str, limite: int
    ) -> List[Dict[str, Any]]:
        # Recuperar los fragmentos con mayor similitud semántica a la consulta
        # RF-SEM-09
        pass


# ─────────────────────────────────────────────────────────────────────────────
# Procesamiento Semántico — Opiniones
# ─────────────────────────────────────────────────────────────────────────────

class IOpinionClasificadaService(ABC):

    @abstractmethod
    async def clasificarOpinion(
        self,
        encuesta_id: str,
        barrio_id: str,
        tema: str,
    ) -> Dict[str, Any]:
        # Registrar una opinión clasificada con su categoría temática
        # RF-SEM-04
        pass

    @abstractmethod
    async def obtenerOpinionesPorTema(self, tema: str) -> List[Dict[str, Any]]:
        # Retornar todas las opiniones asociadas a una categoría temática
        # RF-SEM-05
        pass

    @abstractmethod
    async def obtenerOpinionesPorBarrio(self, barrio_id: str) -> List[Dict[str, Any]]:
        # Retornar todas las opiniones registradas en un barrio específico
        pass

    @abstractmethod
    async def obtenerOpinionPorId(self, opinion_id: str) -> Optional[Dict[str, Any]]:
        # Recuperar una opinión clasificada por su UUID
        pass

    @abstractmethod
    async def eliminarOpinion(self, opinion_id: str) -> bool:
        # Eliminar una opinión clasificada; retorna True si la operación fue exitosa
        pass


# ─────────────────────────────────────────────────────────────────────────────
# Procesamiento Semántico — Argumentos
# ─────────────────────────────────────────────────────────────────────────────

class IArgumentoService(ABC):

    @abstractmethod
    async def registrarArgumento(
        self,
        opinion_id: str,
        texto: str,
        tema: str,
        problematica_cod: Optional[int],
    ) -> Dict[str, Any]:
        # Registrar un argumento identificado en una opinión ciudadana
        # RF-SEM-06
        pass

    @abstractmethod
    async def obtenerArgumentosPorOpinion(self, opinion_id: str) -> List[Dict[str, Any]]:
        # Retornar todos los argumentos de una opinión
        pass

    @abstractmethod
    async def obtenerArgumentosPorTema(self, tema: str) -> List[Dict[str, Any]]:
        # Retornar los argumentos agrupados por categoría temática
        # RF-SEM-06
        pass

    @abstractmethod
    async def obtenerArgumentosPorProblematica(self, problematica_cod: int) -> List[Dict[str, Any]]:
        # Retornar y agrupar argumentos según la problemática asociada
        # RF-SEM-11
        pass

    @abstractmethod
    async def calcularFrecuenciaArgumentos(self, problematica_cod: int) -> List[Dict[str, Any]]:
        # Calcular la frecuencia de aparición de argumentos en una problemática
        # RF-SEM-12
        pass

    @abstractmethod
    async def obtenerArgumentosPorBarrioYProblematica(
        self,
        barrio_id: str,
        problematica_cod: int,
        limite: int,
    ) -> List[Dict[str, Any]]:
        # Retornar los argumentos más frecuentes para una problemática en un barrio
        # RF-SEM-13
        pass

    @abstractmethod
    async def incrementarFrecuencia(self, argumento_id: str) -> None:
        # Incrementar el contador de frecuencia de un argumento existente
        pass

    @abstractmethod
    async def eliminarArgumento(self, argumento_id: str) -> bool:
        # Eliminar un argumento; retorna True si la operación fue exitosa
        pass


class IArgumentoDocumentoService(ABC):

    @abstractmethod
    async def asociarArgumentoDocumento(
        self,
        argumento_id: str,
        documento_id: str,
    ) -> Dict[str, Any]:
        # Crear la relación N:M entre un argumento y un documento
        # RF-SEM-14
        pass

    @abstractmethod
    async def obtenerDocumentosPorArgumento(self, argumento_id: str) -> List[Dict[str, Any]]:
        # Retornar todos los documentos relacionados con un argumento
        pass

    @abstractmethod
    async def obtenerArgumentosPorDocumento(self, documento_id: str) -> List[Dict[str, Any]]:
        # Retornar todos los argumentos que referencian un documento
        pass

    @abstractmethod
    async def eliminarAsociacion(self, argumento_id: str, documento_id: str) -> bool:
        # Eliminar la relación entre un argumento y un documento
        pass


# ─────────────────────────────────────────────────────────────────────────────
# Procesamiento Semántico — Temas y Búsqueda
# ─────────────────────────────────────────────────────────────────────────────

class ITemaDocumentoService(ABC):

    @abstractmethod
    async def asociarTemaDocumento(self, tema: str, documento_id: str) -> Dict[str, Any]:
        # Registrar la relación entre un tema y un documento
        # RF-SEM-10, RF-SEM-14
        pass

    @abstractmethod
    async def obtenerDocumentosPorTema(self, tema: str) -> List[Dict[str, Any]]:
        # Retornar todos los documentos asociados a una categoría temática
        # RF-SEM-10
        pass

    @abstractmethod
    async def obtenerTemasPorDocumento(self, documento_id: str) -> List[Dict[str, Any]]:
        # Retornar todos los temas registrados para un documento
        pass

    @abstractmethod
    async def eliminarTemaDocumento(self, tema_documento_id: str) -> bool:
        # Eliminar una relación tema-documento; retorna True si existía
        pass


class IBusquedaSemanticaService(ABC):

    @abstractmethod
    async def buscarPorLenguajeNatural(
        self,
        consulta: str,
        limite: int,
    ) -> List[Dict[str, Any]]:
        # Realizar búsqueda semántica en lenguaje natural sobre los documentos
        # RF-SEM-07, RF-SEM-15
        pass

    @abstractmethod
    async def obtenerSoporteDocumentalPorTema(
        self,
        tema: str,
    ) -> Dict[str, Any]:
        # Retornar documentos y fragmentos de soporte para una categoría temática
        # RF-SEM-10
        pass

    @abstractmethod
    async def relacionarProblematicaConDocumentos(
        self,
        problematica_cod: int,
    ) -> List[Dict[str, Any]]:
        # Asociar una problemática con sus documentos y fragmentos relacionados
        # RF-SEM-14
        pass