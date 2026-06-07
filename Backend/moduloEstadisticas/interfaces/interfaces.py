from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


# =============================================================================
# CATÁLOGOS
# =============================================================================

class ICatalogoOcupacionService(ABC):

    @abstractmethod
    async def listar(self) -> List[Dict[str, Any]]:
        """Retorna todos los códigos de ocupación."""
        pass

    @abstractmethod
    async def obtener(self, codigo: int) -> Optional[Dict[str, Any]]:
        """Retorna una ocupación por su código."""
        pass


class ICatalogoInclinacionVotoService(ABC):

    @abstractmethod
    async def listar(self) -> List[Dict[str, Any]]:
        """Retorna todas las inclinaciones de voto registradas."""
        pass

    @abstractmethod
    async def obtener(self, codigo: int) -> Optional[Dict[str, Any]]:
        pass


class ICatalogoIntencionParticipacionService(ABC):

    @abstractmethod
    async def listar(self) -> List[Dict[str, Any]]:
        """Retorna todas las intenciones de participación registradas."""
        pass

    @abstractmethod
    async def obtener(self, codigo: int) -> Optional[Dict[str, Any]]:
        pass


class ICatalogoProblematicaService(ABC):

    @abstractmethod
    async def listar(self) -> List[Dict[str, Any]]:
        """Retorna todas las problemáticas del catálogo."""
        pass

    @abstractmethod
    async def obtener(self, codigo: int) -> Optional[Dict[str, Any]]:
        pass


# =============================================================================
# RANGO DE EDAD
# =============================================================================

class IRangoEdadService(ABC):

    @abstractmethod
    async def listar(self) -> List[Dict[str, Any]]:
        """Retorna todos los rangos de edad definidos."""
        pass

    @abstractmethod
    async def obtener(self, rango_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def crear(self, etiqueta: str, edad_min: int, edad_max: int) -> Dict[str, Any]:
        """Crea un nuevo rango de edad."""
        pass

    @abstractmethod
    async def actualizar(
        self, rango_id: str, etiqueta: str, edad_min: int, edad_max: int
    ) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def eliminar(self, rango_id: str) -> bool:
        pass


# =============================================================================
# PERÍODO ESTADÍSTICO
# =============================================================================

class IPeriodoEstadisticoService(ABC):

    @abstractmethod
    async def listar(self) -> List[Dict[str, Any]]:
        """Retorna todos los períodos estadísticos."""
        pass

    @abstractmethod
    async def obtener(self, periodo_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def crear(
        self, etiqueta: str, fecha_inicio: str, fecha_fin: str
    ) -> Dict[str, Any]:
        """Crea un período estadístico; valida que fecha_fin >= fecha_inicio."""
        pass

    @abstractmethod
    async def actualizar(
        self, periodo_id: str, etiqueta: str, fecha_inicio: str, fecha_fin: str
    ) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def eliminar(self, periodo_id: str) -> bool:
        pass


# =============================================================================
# IMPORTACIÓN CSV
# =============================================================================

class IImportacionCsvService(ABC):

    @abstractmethod
    async def listar(self) -> List[Dict[str, Any]]:
        """Retorna el historial de importaciones."""
        pass

    @abstractmethod
    async def obtener(self, importacion_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def importar(self, archivo_csv: Any) -> Dict[str, Any]:
        """
        Procesa un archivo CSV de encuestas.
        Valida cada fila contra los catálogos, persiste registros válidos
        en la tabla encuesta y retorna el resumen:
        { importacion_id, total, validos, invalidos, errores_detalle }.
        """
        pass

    @abstractmethod
    async def obtener_estado(self, importacion_id: str) -> Optional[Dict[str, Any]]:
        """Consulta el estado de procesamiento de una importación."""
        pass


# =============================================================================
# ENCUESTA
# =============================================================================

class IEncuestaService(ABC):

    @abstractmethod
    async def listar(
        self,
        importacion_id: Optional[str] = None,
        barrio_id: Optional[str] = None,
        periodo_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Lista encuestas con filtros opcionales.
        Si se pasa periodo_id, filtra por fecha_inicio/fecha_fin del período.
        """
        pass

    @abstractmethod
    async def obtener(self, encuesta_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def crear(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Crea una encuesta individual (sin importación masiva)."""
        pass

    @abstractmethod
    async def actualizar(
        self, encuesta_id: str, payload: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def eliminar(self, encuesta_id: str) -> bool:
        pass


# =============================================================================
# SNAPSHOT TERRITORIAL
# =============================================================================

class ISnapshotTerritorialService(ABC):

    @abstractmethod
    async def listar(
        self,
        barrio_id: Optional[str] = None,
        periodo_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Lista snapshots con filtros opcionales por barrio y/o período."""
        pass

    @abstractmethod
    async def obtener(self, snapshot_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def generar(
        self, barrio_id: str, periodo_id: str
    ) -> Dict[str, Any]:
        """
        Calcula y persiste el snapshot territorial de un barrio en un período,
        agregando las encuestas correspondientes.
        Retorna el snapshot generado.
        """
        pass

    @abstractmethod
    async def generar_todos(self, periodo_id: str) -> List[Dict[str, Any]]:
        """
        Genera snapshots para todos los barrios dentro de un período.
        Retorna la lista de snapshots creados.
        """
        pass

    @abstractmethod
    async def eliminar(self, snapshot_id: str) -> bool:
        pass


# =============================================================================
# VARIACIÓN TEMPORAL
# =============================================================================

class IVariacionTemporalService(ABC):

    @abstractmethod
    async def listar(
        self,
        barrio_id: Optional[str] = None,
        periodo_actual_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Lista variaciones con filtros opcionales."""
        pass

    @abstractmethod
    async def obtener(self, variacion_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def calcular(
        self, barrio_id: str, periodo_anterior_id: str, periodo_actual_id: str
    ) -> Dict[str, Any]:
        """
        Calcula la variación entre dos períodos para un barrio,
        determina si el cambio es significativo y lo persiste.
        """
        pass

    @abstractmethod
    async def calcular_todos(
        self, periodo_anterior_id: str, periodo_actual_id: str
    ) -> List[Dict[str, Any]]:
        """Calcula variaciones para todos los barrios entre dos períodos."""
        pass


# =============================================================================
# RANKING PROBLEMÁTICA
# =============================================================================

class IRankingProblematicaService(ABC):

    @abstractmethod
    async def listar(
        self,
        periodo_id: Optional[str] = None,
        barrio_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Lista rankings con filtros opcionales."""
        pass

    @abstractmethod
    async def obtener(self, ranking_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def calcular(
        self, barrio_id: str, periodo_id: str
    ) -> List[Dict[str, Any]]:
        """
        Calcula y persiste el ranking de problemáticas por frecuencia
        para un barrio en un período. Retorna el ranking ordenado.
        """
        pass

    @abstractmethod
    async def calcular_todos(self, periodo_id: str) -> List[Dict[str, Any]]:
        """Calcula el ranking de problemáticas para todos los barrios en el período."""
        pass


# =============================================================================
# RESULTADO CRUCE
# =============================================================================

class IResultadoCruceService(ABC):

    @abstractmethod
    async def listar(self, periodo_id: str) -> List[Dict[str, Any]]:
        """Lista todos los resultados de cruce de un período."""
        pass

    @abstractmethod
    async def obtener(self, cruce_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def calcular(
        self,
        periodo_id: str,
        dimension_a: str,
        dimension_b: str,
    ) -> List[Dict[str, Any]]:
        """
        Cruza dos dimensiones (e.g. 'ocupacion' × 'inclinacion_voto')
        sobre las encuestas del período y persiste los resultados.
        Retorna las celdas del cruce con cantidad y porcentaje.
        """
        pass

    @abstractmethod
    async def calcular_multiples(
        self,
        periodo_id: str,
        cruces: List[Dict[str, str]],
    ) -> List[Dict[str, Any]]:
        """
        Ejecuta múltiples cruces en lote.
        cruces: lista de { dimension_a, dimension_b }.
        """
        pass

    @abstractmethod
    async def eliminar_por_periodo(self, periodo_id: str) -> int:
        """Elimina todos los cruces de un período; retorna cantidad eliminada."""
        pass


# =============================================================================
# CARACTERIZACIÓN TERRITORIAL
# =============================================================================

class ICaracterizacionTerritorialService(ABC):

    @abstractmethod
    async def listar(
        self,
        barrio_id: Optional[str] = None,
        periodo_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def obtener(self, caracterizacion_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def generar(
        self, barrio_id: str, periodo_id: str
    ) -> Dict[str, Any]:
        """
        Deriva y persiste la caracterización territorial de un barrio
        a partir del snapshot, rankings y cruces del período.
        Determina afinidad predominante, problemática principal,
        índices de indecisión/apoyo y flags de prioridad.
        """
        pass

    @abstractmethod
    async def generar_todos(self, periodo_id: str) -> List[Dict[str, Any]]:
        """Genera la caracterización para todos los barrios del período."""
        pass


# =============================================================================
# EXPORTACIÓN DE RESULTADOS
# =============================================================================

class IExportacionResultadoService(ABC):

    @abstractmethod
    async def listar(self, periodo_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lista exportaciones con filtro opcional por período."""
        pass

    @abstractmethod
    async def obtener(self, exportacion_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def exportar(
        self,
        periodo_id: str,
        tipo_analisis: str,
        formato: str,
        coordinador_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Genera el archivo de exportación (CSV, XLSX, JSON) con los
        resultados del análisis indicado para el período.
        tipo_analisis: 'snapshot' | 'variacion' | 'ranking' | 'cruce' | 'caracterizacion'.
        Retorna la entrada de exportacion_resultado con la ruta del archivo.
        """
        pass


# =============================================================================
# RESUMEN ESTADÍSTICO
# =============================================================================

class IResumenEstadisticoService(ABC):

    @abstractmethod
    async def listar(
        self,
        barrio_id: Optional[str] = None,
        periodo_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def obtener(self, resumen_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def generar(
        self, barrio_id: str, periodo_id: str
    ) -> Dict[str, Any]:
        """
        Consolida en texto el análisis completo de un barrio para el período:
        snapshot, variación, ranking de problemáticas y caracterización.
        Persiste y retorna el resumen generado.
        """
        pass

    @abstractmethod
    async def generar_todos(self, periodo_id: str) -> List[Dict[str, Any]]:
        """Genera el resumen para todos los barrios del período."""
        pass