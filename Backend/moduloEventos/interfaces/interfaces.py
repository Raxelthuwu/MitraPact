from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


# =============================================================================
# TERRITORIO
# =============================================================================

class IBarrioService(ABC):

    @abstractmethod
    def listar_barrios(self) -> List[Dict[str, Any]]:
        """Retorna todos los barrios registrados."""
        pass

    @abstractmethod
    def obtener_barrio(self, barrio_id: str) -> Optional[Dict[str, Any]]:
        """Retorna un barrio por su ID, o None si no existe."""
        pass

    @abstractmethod
    def crear_barrio(self, nombre: str) -> Dict[str, Any]:
        """Crea un barrio y retorna su representación."""
        pass

    @abstractmethod
    def actualizar_barrio(self, barrio_id: str, nombre: str) -> Optional[Dict[str, Any]]:
        """Actualiza el nombre del barrio; retorna el barrio actualizado o None."""
        pass

    @abstractmethod
    def eliminar_barrio(self, barrio_id: str) -> bool:
        """Elimina un barrio; retorna True si la operación fue exitosa."""
        pass


class ISectorService(ABC):

    @abstractmethod
    def listar_sectores(self, barrio_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lista sectores, opcionalmente filtrando por barrio."""
        pass

    @abstractmethod
    def obtener_sector(self, sector_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def crear_sector(self, nombre: str, barrio_id: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def actualizar_sector(
        self, sector_id: str, nombre: str, barrio_id: str
    ) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def eliminar_sector(self, sector_id: str) -> bool:
        pass


class IPuntoInteresService(ABC):

    @abstractmethod
    def listar_puntos(self, sector_id: str) -> List[Dict[str, Any]]:
        """Lista los puntos de interés de un sector."""
        pass

    @abstractmethod
    def obtener_punto(self, punto_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def crear_punto(self, nombre: str, sector_id: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def actualizar_punto(
        self, punto_id: str, nombre: str, sector_id: str
    ) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def eliminar_punto(self, punto_id: str) -> bool:
        pass


# =============================================================================
# COORDINADOR
# =============================================================================

class ICoordinadorService(ABC):

    @abstractmethod
    def listar_coordinadores(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def obtener_coordinador(self, coordinador_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def crear_coordinador(
        self, nombre: str, email: str, password_plano: str
    ) -> Dict[str, Any]:
        """Hashea la contraseña internamente antes de persistir."""
        pass

    @abstractmethod
    def actualizar_coordinador(
        self, coordinador_id: str, nombre: str, email: str
    ) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def cambiar_password(
        self, coordinador_id: str, password_plano: str
    ) -> bool:
        pass


# =============================================================================
# SIMPATIZANTE
# =============================================================================

class ISimpatizanteService(ABC):

    @abstractmethod
    def listar_simpatizantes(
        self, barrio_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def obtener_simpatizante(self, simpatizante_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def crear_simpatizante(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def actualizar_simpatizante(
        self, simpatizante_id: str, payload: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def eliminar_simpatizante(self, simpatizante_id: str) -> bool:
        pass


# =============================================================================
# HORARIO DISPONIBLE
# =============================================================================

class IHorarioDisponibleService(ABC):

    @abstractmethod
    def listar_horarios(self, simpatizante_id: str) -> List[Dict[str, Any]]:
        """Retorna los horarios registrados de un simpatizante."""
        pass

    @abstractmethod
    def crear_horario(
        self,
        simpatizante_id: str,
        dia_semana: str,
        hora_inicio: str,
        hora_fin: str,
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    def eliminar_horario(self, horario_id: str) -> bool:
        pass

    @abstractmethod
    def consultar_disponibles_para_evento(
        self,
        fecha: str,
        dia_semana: str,
        hora_inicio: str,
        hora_fin: str,
    ) -> List[Dict[str, Any]]:
        """
        RF-EV-06 — Lista simpatizantes disponibles para el horario indicado.
        RF-EV-22 — Valida compatibilidad de horarios.
        """
        pass


# =============================================================================
# EVENTO  (RF-EV-01 al RF-EV-05)
# =============================================================================

class IEventoService(ABC):

    @abstractmethod
    def listar_eventos(self) -> List[Dict[str, Any]]:
        """RF-EV-02 — Consulta de todos los eventos."""
        pass

    @abstractmethod
    def obtener_evento(self, evento_id: str) -> Optional[Dict[str, Any]]:
        """RF-EV-02 — Consulta completa de un evento, incluye tipos."""
        pass

    @abstractmethod
    def crear_evento(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        RF-EV-01 — Crea un evento con sus tipos asociados.
        payload debe incluir la clave 'tipos' (lista de strings).
        """
        pass

    @abstractmethod
    def actualizar_evento(
        self, evento_id: str, payload: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        RF-EV-03 — Modifica la información de un evento.
        Si payload incluye 'tipos', reemplaza todos los tipos existentes.
        """
        pass

    @abstractmethod
    def actualizar_estado(
        self, evento_id: str, estado: str
    ) -> Optional[Dict[str, Any]]:
        """RF-EV-04 — Cambia el estado del evento."""
        pass

    @abstractmethod
    def eliminar_evento(self, evento_id: str) -> bool:
        pass

    @abstractmethod
    def agregar_tipo(self, evento_id: str, tipo: str) -> Dict[str, Any]:
        """RF-EV-05 — Agrega un tipo al evento."""
        pass

    @abstractmethod
    def eliminar_tipo(self, tipo_id: str) -> bool:
        """RF-EV-05 — Elimina un tipo del evento."""
        pass


# =============================================================================
# ASIGNACIÓN DE PERSONAL  (RF-EV-07 al RF-EV-11)
# =============================================================================

class IAsignacionService(ABC):

    @abstractmethod
    def listar_asignaciones(self, evento_id: str) -> List[Dict[str, Any]]:
        """RF-EV-09 — Lista integrantes asignados al evento."""
        pass

    @abstractmethod
    def asignar_manual(
        self,
        evento_id: str,
        simpatizante_id: str,
        rol: Optional[str],
    ) -> Dict[str, Any]:
        """RF-EV-07 — Asignación manual de personal."""
        pass

    @abstractmethod
    def asignar_automatico(
        self,
        evento_id: str,
        criterios: Dict[str, bool],
    ) -> List[Dict[str, Any]]:
        """
        RF-EV-08 — Asignación automática de personal.
        criterios puede contener: usar_horario, usar_ocupacion, usar_participacion_previa.
        """
        pass

    @abstractmethod
    def actualizar_rol(
        self, asignacion_id: str, rol: str
    ) -> Optional[Dict[str, Any]]:
        """RF-EV-09 — Actualiza el rol de un integrante."""
        pass

    @abstractmethod
    def remover_asignacion(self, asignacion_id: str) -> bool:
        """RF-EV-09 — Remueve un integrante del evento."""
        pass

    @abstractmethod
    def registrar_asistencia(
        self, asignacion_id: str, asistio: bool
    ) -> Optional[Dict[str, Any]]:
        """RF-EV-14 — Registra si el integrante asistió."""
        pass

    @abstractmethod
    def verificar_participacion_territorial(
        self, simpatizante_id: str, evento_id: str
    ) -> Dict[str, Any]:
        """
        RF-EV-23 — Advierte si la persona participó recientemente
        en el mismo sector del evento.
        """
        pass


# =============================================================================
# COBERTURA  (RF-EV-11)
# =============================================================================

class ICoberturaService(ABC):

    @abstractmethod
    def listar_cobertura(self, evento_id: str) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def registrar_cobertura(
        self, evento_id: str, ocupacion: str, requeridos: int
    ) -> Dict[str, Any]:
        """RF-EV-11 — Registra la cobertura de personal requerida."""
        pass

    @abstractmethod
    def actualizar_cobertura(
        self,
        cobertura_id: str,
        ocupacion: str,
        requeridos: int,
        asignados: int,
    ) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def eliminar_cobertura(self, cobertura_id: str) -> bool:
        pass


# =============================================================================
# REGISTRO OPERATIVO  (RF-EV-12, RF-EV-13, RF-EV-18)
# =============================================================================

class IObservacionService(ABC):

    @abstractmethod
    def listar_observaciones(self, evento_id: str) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def registrar_observacion(
        self, evento_id: str, momento: str, contenido: str
    ) -> Dict[str, Any]:
        """
        RF-EV-12 / RF-EV-13 — Registra observaciones iniciales o finales.
        momento: 'INICIAL' | 'FINAL'
        """
        pass

    @abstractmethod
    def eliminar_observacion(self, observacion_id: str) -> bool:
        pass


class IParticipacionExternaService(ABC):

    @abstractmethod
    def obtener_participacion(self, evento_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def registrar_participacion(
        self, evento_id: str, cantidad: int, notas: Optional[str]
    ) -> Dict[str, Any]:
        """RF-EV-18 — Registra participación externa del evento."""
        pass

    @abstractmethod
    def actualizar_participacion(
        self,
        participacion_id: str,
        cantidad: int,
        notas: Optional[str],
    ) -> Optional[Dict[str, Any]]:
        pass


# =============================================================================
# MATERIAL PUBLICITARIO  (RF-EV-19 al RF-EV-22)
# =============================================================================

class IMaterialPublicitarioService(ABC):

    @abstractmethod
    def obtener_material(self, evento_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def registrar_material(
        self, evento_id: str, entregado: int, restante: int
    ) -> Dict[str, Any]:
        """RF-EV-19 — Registra cantidades de material publicitario."""
        pass

    @abstractmethod
    def actualizar_material(
        self, material_id: str, entregado: int, restante: int
    ) -> Optional[Dict[str, Any]]:
        pass


class IEstadoMaterialService(ABC):

    @abstractmethod
    def listar_estados(self, evento_id: str) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def registrar_estado(
        self, evento_id: str, estado: str, notas: Optional[str]
    ) -> Dict[str, Any]:
        """RF-EV-20 — Registra el estado observado del material."""
        pass

    @abstractmethod
    def cargar_desde_csv(
        self, archivo_csv: Any
    ) -> Dict[str, Any]:
        """
        RF-EV-21 — Carga un archivo CSV con columnas:
        numero_evento, estado (1-5), notas.
        Retorna resumen: insertados, errores.
        """
        pass

    @abstractmethod
    def calcular_promedio_estado(self, evento_id: str) -> Optional[float]:
        """RF-EV-22 — Promedio numérico del estado total del material."""
        pass


# =============================================================================
# AUDITORÍA
# =============================================================================

class IAuditoriaService(ABC):

    @abstractmethod
    def historial_registro(
        self, tabla: str, registro_id: str
    ) -> List[Dict[str, Any]]:
        """Retorna el historial de cambios de un registro específico."""
        pass

    @abstractmethod
    def registros_recientes(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retorna los últimos N registros de auditoría."""
        pass