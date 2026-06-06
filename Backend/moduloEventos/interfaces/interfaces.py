from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import uuid


# =============================================================================
# IEventoService
# =============================================================================
class IEventoService(ABC):

    @abstractmethod
    async def listar(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def obtener(self, pk: uuid.UUID) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def crear(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def actualizar(self, pk: uuid.UUID, datos: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def cambiar_estado(self, pk: uuid.UUID, estado: str) -> Optional[Dict[str, Any]]:
        pass


# =============================================================================
# IEventoTipoService
# =============================================================================
class IEventoTipoService(ABC):

    @abstractmethod
    async def listar_por_evento(self, evento_pk: uuid.UUID) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def agregar(self, evento_pk: uuid.UUID, tipo: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def eliminar(self, pk: uuid.UUID) -> bool:
        pass


# =============================================================================
# IDisponibilidadService
# =============================================================================
class IDisponibilidadService(ABC):

    @abstractmethod
    async def simpatizantes_disponibles(
        self, evento_pk: uuid.UUID
    ) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def advertencia_territorial(
        self, simpatizante_pk: uuid.UUID, evento_pk: uuid.UUID, dias: int
    ) -> bool:
        pass


# =============================================================================
# IAsignacionService
# =============================================================================
class IAsignacionService(ABC):

    @abstractmethod
    async def listar(self, evento_pk: uuid.UUID) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def asignar_manual(
        self,
        evento_pk: uuid.UUID,
        simpatizante_pk: uuid.UUID,
        rol: str,
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def asignar_automatico(
        self,
        evento_pk: uuid.UUID,
        usar_disponibilidad: bool,
        usar_ocupacion: Optional[str],
        excluir_sector_reciente: bool,
    ) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def actualizar(self, pk: uuid.UUID, datos: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def eliminar(self, pk: uuid.UUID) -> bool:
        pass

    @abstractmethod
    async def registrar_asistencia(
        self, evento_pk: uuid.UUID, asistencias: Dict[str, bool]
    ) -> int:
        pass


# =============================================================================
# ICoberturaService
# =============================================================================
class ICoberturaService(ABC):

    @abstractmethod
    async def listar(self, evento_pk: uuid.UUID) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def agregar(self, evento_pk: uuid.UUID, datos: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def eliminar(self, pk: uuid.UUID) -> bool:
        pass


# =============================================================================
# IObservacionService
# =============================================================================
class IObservacionService(ABC):

    @abstractmethod
    async def listar(self, evento_pk: uuid.UUID) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def agregar(
        self, evento_pk: uuid.UUID, momento: str, contenido: str
    ) -> Dict[str, Any]:
        pass


# =============================================================================
# IParticipacionExternaService
# =============================================================================
class IParticipacionExternaService(ABC):

    @abstractmethod
    async def obtener(self, evento_pk: uuid.UUID) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def registrar(
        self, evento_pk: uuid.UUID, cantidad: int, notas: Optional[str]
    ) -> Dict[str, Any]:
        pass


# =============================================================================
# IMaterialPublicitarioService
# =============================================================================
class IMaterialPublicitarioService(ABC):

    @abstractmethod
    async def obtener(self, evento_pk: uuid.UUID) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def registrar(
        self, evento_pk: uuid.UUID, entregado: int, restante: int
    ) -> Dict[str, Any]:
        pass


# =============================================================================
# IEstadoMaterialService
# =============================================================================
class IEstadoMaterialService(ABC):

    @abstractmethod
    async def listar(self, evento_pk: uuid.UUID) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def registrar(
        self, evento_pk: uuid.UUID, estado: str, notas: Optional[str]
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def cargar_csv(self, contenido: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def promedio_estado(self, evento_pk: uuid.UUID) -> Dict[str, Any]:
        pass


# =============================================================================
# ITerritorioService
# =============================================================================
class ITerritorioService(ABC):

    @abstractmethod
    async def listar_barrios(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def listar_sectores(
        self, barrio_pk: Optional[uuid.UUID]
    ) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def listar_puntos_interes(
        self, sector_pk: Optional[uuid.UUID]
    ) -> List[Dict[str, Any]]:
        pass