from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


# =============================================================================
# TERRITORIO
# =============================================================================

class IBarrioService(ABC):

    @abstractmethod
    async def listar_barrios(self) -> List[Dict[str, Any]]:
        """Retorna todos los barrios registrados."""
        pass

    @abstractmethod
    async def obtener_barrio(self, barrio_id: str) -> Optional[Dict[str, Any]]:
        """Retorna un barrio por su ID, o None si no existe."""
        pass

    @abstractmethod
    async def crear_barrio(self, nombre: str) -> Dict[str, Any]:
        """Crea un barrio y retorna su representación."""
        pass

    @abstractmethod
    async def actualizar_barrio(self, barrio_id: str, nombre: str) -> Optional[Dict[str, Any]]:
        """Actualiza el nombre del barrio; retorna el barrio actualizado o None."""
        pass

    @abstractmethod
    async def eliminar_barrio(self, barrio_id: str) -> bool:
        """Elimina un barrio; retorna True si la operación fue exitosa."""
        pass


class IPuntoInteresService(ABC):

    @abstractmethod
    async def listar_puntos(self, barrio_id: str) -> List[Dict[str, Any]]:
        """Lista los puntos de interés de un barrio."""
        pass

    @abstractmethod
    async def obtener_punto(self, punto_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def crear_punto(self, nombre: str, barrio_id: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def actualizar_punto(
        self, punto_id: str, nombre: str, barrio_id: str
    ) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def eliminar_punto(self, punto_id: str) -> bool:
        pass


# =============================================================================
# COORDINADOR
# =============================================================================

class ICoordinadorService(ABC):

    @abstractmethod
    async def listar_coordinadores(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def obtener_coordinador(self, coordinador_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def crear_coordinador(
        self, nombre: str, email: str, password_plano: str
    ) -> Dict[str, Any]:
        """Hashea la contraseña internamente antes de persistir."""
        pass

    @abstractmethod
    async def actualizar_coordinador(
        self, coordinador_id: str, nombre: str, email: str
    ) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def cambiar_password(
        self, coordinador_id: str, password_plano: str
    ) -> bool:
        pass


# =============================================================================
# SIMPATIZANTE
# =============================================================================

class ISimpatizanteService(ABC):

    @abstractmethod
    async def listar_simpatizantes(
        self, barrio_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def obtener_simpatizante(self, simpatizante_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def crear_simpatizante(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def actualizar_simpatizante(
        self, simpatizante_id: str, payload: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def eliminar_simpatizante(self, simpatizante_id: str) -> bool:
        pass


# =============================================================================
# HORARIO DISPONIBLE
# =============================================================================

class IHorarioDisponibleService(ABC):

    @abstractmethod
    async def listar_horarios(self, simpatizante_id: str) -> List[Dict[str, Any]]:
        """Retorna los horarios registrados de un simpatizante."""
        pass

    @abstractmethod
    async def crear_horario(
        self,
        simpatizante_id: str,
        dia_semana: str,
        hora_inicio: str,
        hora_fin: str,
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def eliminar_horario(self, horario_id: str) -> bool:
        pass

    @abstractmethod
    async def consultar_disponibles_para_evento(
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
    async def listar_eventos(self) -> List[Dict[str, Any]]:
        """RF-EV-02 — Consulta de todos los eventos."""
        pass

    @abstractmethod
    async def obtener_evento(self, evento_id: str) -> Optional[Dict[str, Any]]:
        """RF-EV-02 — Consulta completa de un evento, incluye tipos y puntos de interés."""
        pass

    @abstractmethod
    async def crear_evento(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        RF-EV-01 — Crea un evento con sus tipos asociados.
        payload debe incluir la clave 'tipos' (lista de strings).
        """
        pass

    @abstractmethod
    async def actualizar_evento(
        self, evento_id: str, payload: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        RF-EV-03 — Modifica la información de un evento.
        Si payload incluye 'tipos', reemplaza todos los tipos existentes.
        """
        pass

    @abstractmethod
    async def actualizar_estado(
        self, evento_id: str, estado: str
    ) -> Optional[Dict[str, Any]]:
        """RF-EV-04 — Cambia el estado del evento."""
        pass

    @abstractmethod
    async def eliminar_evento(self, evento_id: str) -> bool:
        pass

    @abstractmethod
    async def agregar_tipo(self, evento_id: str, tipo: str) -> Dict[str, Any]:
        """RF-EV-05 — Agrega un tipo al evento."""
        pass

    @abstractmethod
    async def eliminar_tipo(self, tipo_id: str) -> bool:
        """RF-EV-05 — Elimina un tipo del evento."""
        pass


# =============================================================================
# EVENTO PUNTO DE INTERÉS
# =============================================================================

class IEventoPuntoInteresService(ABC):

    @abstractmethod
    async def listar_puntos_evento(self, evento_id: str) -> List[Dict[str, Any]]:
        """Retorna los puntos de interés asociados a un evento."""
        pass

    @abstractmethod
    async def agregar_punto(self, evento_id: str, punto_interes_id: str) -> Dict[str, Any]:
        """
        Asocia un punto de interés al evento.
        El trigger de BD valida que el punto pertenezca al mismo barrio del evento.
        """
        pass

    @abstractmethod
    async def remover_punto(self, evento_punto_interes_id: str) -> bool:
        """Desvincula un punto de interés del evento."""
        pass

    @abstractmethod
    async def reemplazar_puntos(
        self, evento_id: str, punto_interes_ids: List[str]
    ) -> List[Dict[str, Any]]:
        """Reemplaza todos los puntos de interés del evento por la lista indicada."""
        pass


# =============================================================================
# ASIGNACIÓN DE PERSONAL  (RF-EV-07 al RF-EV-11)
# =============================================================================

class IAsignacionService(ABC):

    @abstractmethod
    async def listar_asignaciones(self, evento_id: str) -> List[Dict[str, Any]]:
        """RF-EV-09 — Lista integrantes asignados al evento."""
        pass

    @abstractmethod
    async def asignar_manual(
        self,
        evento_id: str,
        simpatizante_id: str,
        rol: Optional[str],
    ) -> Dict[str, Any]:
        """RF-EV-07 — Asignación manual de personal."""
        pass

    @abstractmethod
    async def asignar_automatico(
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
    async def actualizar_rol(
        self, asignacion_id: str, rol: str
    ) -> Optional[Dict[str, Any]]:
        """RF-EV-09 — Actualiza el rol de un integrante."""
        pass

    @abstractmethod
    async def remover_asignacion(self, asignacion_id: str) -> bool:
        """RF-EV-09 — Remueve un integrante del evento."""
        pass

    @abstractmethod
    async def registrar_asistencia(
        self, asignacion_id: str, asistio: bool
    ) -> Optional[Dict[str, Any]]:
        """RF-EV-14 — Registra si el integrante asistió."""
        pass

    @abstractmethod
    async def verificar_participacion_territorial(
        self, simpatizante_id: str, evento_id: str
    ) -> Dict[str, Any]:
        """
        RF-EV-23 — Advierte si la persona participó recientemente
        en el mismo barrio del evento.
        """
        pass


# =============================================================================
# COBERTURA  (RF-EV-11)
# =============================================================================

class ICoberturaService(ABC):

    @abstractmethod
    async def listar_cobertura(self, evento_id: str) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def registrar_cobertura(
        self, evento_id: str, ocupacion: str, requeridos: int
    ) -> Dict[str, Any]:
        """RF-EV-11 — Registra la cobertura de personal requerida."""
        pass

    @abstractmethod
    async def actualizar_cobertura(
        self,
        cobertura_id: str,
        ocupacion: str,
        requeridos: int,
        asignados: int,
    ) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def eliminar_cobertura(self, cobertura_id: str) -> bool:
        pass


# =============================================================================
# REGISTRO OPERATIVO  (RF-EV-12, RF-EV-13, RF-EV-18)
# =============================================================================

class IObservacionService(ABC):

    @abstractmethod
    async def listar_observaciones(self, evento_id: str) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def registrar_observacion(
        self, evento_id: str, momento: str, contenido: str
    ) -> Dict[str, Any]:
        """
        RF-EV-12 / RF-EV-13 — Registra observaciones iniciales o finales.
        momento: 'INICIAL' | 'FINAL'
        """
        pass

    @abstractmethod
    async def eliminar_observacion(self, observacion_id: str) -> bool:
        pass


class IParticipacionExternaService(ABC):

    @abstractmethod
    async def obtener_participacion(self, evento_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def registrar_participacion(
        self, evento_id: str, cantidad: int, notas: Optional[str]
    ) -> Dict[str, Any]:
        """RF-EV-18 — Registra participación externa del evento."""
        pass

    @abstractmethod
    async def actualizar_participacion(
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
    async def obtener_material(self, evento_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def registrar_material(
        self, evento_id: str, entregado: int, restante: int
    ) -> Dict[str, Any]:
        """RF-EV-19 — Registra cantidades de material publicitario."""
        pass

    @abstractmethod
    async def actualizar_material(
        self, material_id: str, entregado: int, restante: int
    ) -> Optional[Dict[str, Any]]:
        pass


class IEstadoMaterialService(ABC):

    @abstractmethod
    async def listar_estados(self, evento_id: str) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def registrar_estado(
        self, evento_id: str, estado: str, notas: Optional[str]
    ) -> Dict[str, Any]:
        """RF-EV-20 — Registra el estado observado del material."""
        pass

    @abstractmethod
    async def cargar_desde_csv(
        self, archivo_csv: Any
    ) -> Dict[str, Any]:
        """
        RF-EV-21 — Carga un archivo CSV con columnas:
        numero_evento, estado (1-5), notas.
        Retorna resumen: insertados, errores.
        """
        pass

    @abstractmethod
    async def calcular_promedio_estado(self, evento_id: str) -> Optional[float]:
        """RF-EV-22 — Promedio numérico del estado total del material."""
        pass


# =============================================================================
# AUDITORÍA
# =============================================================================

class IAuditoriaService(ABC):

    @abstractmethod
    async def historial_registro(
        self, tabla: str, registro_id: str
    ) -> List[Dict[str, Any]]:
        """Retorna el historial de cambios de un registro específico."""
        pass

    @abstractmethod
    async def registros_recientes(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retorna los últimos N registros de auditoría."""
        pass