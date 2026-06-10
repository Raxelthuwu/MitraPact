from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


# =============================================================================
# CATÁLOGOS (CRUD completo)
# =============================================================================

class ICatalogoOcupacionService(ABC):

    @abstractmethod
    async def listar(self) -> List[Dict]: ...

    @abstractmethod
    async def obtener(self, codigo: int) -> Optional[Dict]: ...

    @abstractmethod
    async def crear(self, codigo: int, descripcion: str) -> Dict: ...

    @abstractmethod
    async def actualizar(self, codigo: int, descripcion: str) -> bool: ...

    @abstractmethod
    async def eliminar(self, codigo: int) -> bool: ...


class ICatalogoInclinacionVotoService(ABC):

    @abstractmethod
    async def listar(self) -> List[Dict]: ...

    @abstractmethod
    async def obtener(self, codigo: int) -> Optional[Dict]: ...

    @abstractmethod
    async def crear(self, codigo: int, descripcion: str) -> Dict: ...

    @abstractmethod
    async def actualizar(self, codigo: int, descripcion: str) -> bool: ...

    @abstractmethod
    async def eliminar(self, codigo: int) -> bool: ...


class ICatalogoIntencionParticipacionService(ABC):

    @abstractmethod
    async def listar(self) -> List[Dict]: ...

    @abstractmethod
    async def obtener(self, codigo: int) -> Optional[Dict]: ...

    @abstractmethod
    async def crear(self, codigo: int, descripcion: str) -> Dict: ...

    @abstractmethod
    async def actualizar(self, codigo: int, descripcion: str) -> bool: ...

    @abstractmethod
    async def eliminar(self, codigo: int) -> bool: ...


class ICatalogoProblematicaService(ABC):

    @abstractmethod
    async def listar(self) -> List[Dict]: ...

    @abstractmethod
    async def obtener(self, codigo: int) -> Optional[Dict]: ...

    @abstractmethod
    async def crear(self, codigo: int, descripcion: str) -> Dict: ...

    @abstractmethod
    async def actualizar(self, codigo: int, descripcion: str) -> bool: ...

    @abstractmethod
    async def eliminar(self, codigo: int) -> bool: ...


# =============================================================================
# RANGO DE EDAD
# =============================================================================

class IRangoEdadService(ABC):

    @abstractmethod
    async def listar(self) -> List[Dict]: ...

    @abstractmethod
    async def obtener(self, rango_id: str) -> Optional[Dict]: ...

    @abstractmethod
    async def crear(self, etiqueta: str, edad_min: int, edad_max: int) -> Dict: ...

    @abstractmethod
    async def actualizar(
        self, rango_id: str, etiqueta: str, edad_min: int, edad_max: int
    ) -> Optional[Dict]: ...

    @abstractmethod
    async def eliminar(self, rango_id: str) -> bool: ...


# =============================================================================
# PERÍODO ESTADÍSTICO
# =============================================================================

class IPeriodoEstadisticoService(ABC):

    @abstractmethod
    async def listar(self) -> List[Dict]: ...

    @abstractmethod
    async def obtener(self, periodo_id: str) -> Optional[Dict]: ...

    @abstractmethod
    async def crear(self, etiqueta: str, fecha_inicio: Any, fecha_fin: Any) -> Dict: ...

    @abstractmethod
    async def actualizar(
        self, periodo_id: str, etiqueta: str, fecha_inicio: Any, fecha_fin: Any
    ) -> Optional[Dict]: ...

    @abstractmethod
    async def eliminar(self, periodo_id: str) -> bool: ...


# =============================================================================
# IMPORTACIÓN CSV
# =============================================================================

class IImportacionCsvService(ABC):

    @abstractmethod
    async def listar(self) -> List[Dict]: ...

    @abstractmethod
    async def obtener(self, importacion_id: str) -> Optional[Dict]: ...

    @abstractmethod
    async def obtener_estado(self, importacion_id: str) -> Optional[Dict]: ...

    @abstractmethod
    async def importar(self, archivo_csv: Any) -> Dict: ...


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
    ) -> List[Dict]: ...

    @abstractmethod
    async def obtener(self, encuesta_id: str) -> Optional[Dict]: ...

    @abstractmethod
    async def crear(self, payload: Dict) -> Dict: ...

    @abstractmethod
    async def actualizar(self, encuesta_id: str, payload: Dict) -> Optional[Dict]: ...

    @abstractmethod
    async def eliminar(self, encuesta_id: str) -> bool: ...


# =============================================================================
# SNAPSHOT TERRITORIAL
# =============================================================================

class ISnapshotTerritorialService(ABC):

    @abstractmethod
    async def listar(
        self, barrio_id: Optional[str] = None, periodo_id: Optional[str] = None
    ) -> List[Dict]: ...

    @abstractmethod
    async def obtener(self, snapshot_id: str) -> Optional[Dict]: ...

    @abstractmethod
    async def generar(self, barrio_id: str, periodo_id: str) -> Dict: ...

    @abstractmethod
    async def generar_todos(self, periodo_id: str) -> List[Dict]: ...

    @abstractmethod
    async def eliminar(self, snapshot_id: str) -> bool: ...


# =============================================================================
# VARIACIÓN TEMPORAL
# =============================================================================

class IVariacionTemporalService(ABC):

    @abstractmethod
    async def listar(
        self, barrio_id: Optional[str] = None, periodo_actual_id: Optional[str] = None
    ) -> List[Dict]: ...

    @abstractmethod
    async def obtener(self, variacion_id: str) -> Optional[Dict]: ...

    @abstractmethod
    async def calcular(
        self, barrio_id: str, periodo_anterior_id: str, periodo_actual_id: str
    ) -> Optional[Dict]: ...

    @abstractmethod
    async def calcular_todos(
        self, periodo_anterior_id: str, periodo_actual_id: str
    ) -> List[Dict]: ...


# =============================================================================
# RANKING PROBLEMÁTICA
# =============================================================================

class IRankingProblematicaService(ABC):

    @abstractmethod
    async def listar(
        self, periodo_id: Optional[str] = None, barrio_id: Optional[str] = None
    ) -> List[Dict]: ...

    @abstractmethod
    async def obtener(self, ranking_id: str) -> Optional[Dict]: ...

    @abstractmethod
    async def calcular(self, barrio_id: str, periodo_id: str) -> List[Dict]: ...

    @abstractmethod
    async def calcular_todos(self, periodo_id: str) -> List[Dict]: ...


# =============================================================================
# RESULTADO CRUCE
# =============================================================================

class IResultadoCruceService(ABC):

    @abstractmethod
    async def listar(self, periodo_id: str) -> List[Dict]: ...

    @abstractmethod
    async def obtener(self, cruce_id: str) -> Optional[Dict]: ...

    @abstractmethod
    async def calcular(
        self, periodo_id: str, dimension_a: str, dimension_b: str
    ) -> List[Dict]: ...

    @abstractmethod
    async def calcular_multiples(
        self, periodo_id: str, cruces: List[Dict[str, str]]
    ) -> List[Dict]: ...

    @abstractmethod
    async def eliminar_por_periodo(self, periodo_id: str) -> int: ...


# =============================================================================
# CARACTERIZACIÓN TERRITORIAL
# =============================================================================

class ICaracterizacionTerritorialService(ABC):

    @abstractmethod
    async def listar(
        self, barrio_id: Optional[str] = None, periodo_id: Optional[str] = None
    ) -> List[Dict]: ...

    @abstractmethod
    async def obtener(self, caracterizacion_id: str) -> Optional[Dict]: ...

    @abstractmethod
    async def generar(self, barrio_id: str, periodo_id: str) -> Optional[Dict]: ...

    @abstractmethod
    async def generar_todos(self, periodo_id: str) -> List[Dict]: ...


# =============================================================================
# EXPORTACIÓN RESULTADO
# =============================================================================

class IExportacionResultadoService(ABC):

    @abstractmethod
    async def listar(self, periodo_id: Optional[str] = None) -> List[Dict]: ...

    @abstractmethod
    async def obtener(self, exportacion_id: str) -> Optional[Dict]: ...

    @abstractmethod
    async def exportar(
        self,
        periodo_id: str,
        tipo_analisis: str,
        formato: str,
        coordinador_id: Optional[str] = None,
    ) -> Dict: ...


# =============================================================================
# RESUMEN ESTADÍSTICO
# =============================================================================

class IResumenEstadisticoService(ABC):

    @abstractmethod
    async def listar(
        self, barrio_id: Optional[str] = None, periodo_id: Optional[str] = None
    ) -> List[Dict]: ...

    @abstractmethod
    async def obtener(self, resumen_id: str) -> Optional[Dict]: ...

    @abstractmethod
    async def generar(self, barrio_id: str, periodo_id: str) -> Dict: ...

    @abstractmethod
    async def generar_todos(self, periodo_id: str) -> List[Dict]: ...