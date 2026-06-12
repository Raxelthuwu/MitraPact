import csv
import io
import logging
from typing import Any, Dict, List, Optional

from asgiref.sync import sync_to_async

from Backend.moduloEventos.interfaces import (
    IBarrioService,
    IPuntoInteresService,
    ICoordinadorService,
    ISimpatizanteService,
    IHorarioDisponibleService,
    IEventoService,
    IEventoPuntoInteresService,
    IAsignacionService,
    ICoberturaService,
    IObservacionService,
    IParticipacionExternaService,
    IMaterialPublicitarioService,
    IEstadoMaterialService,
    IAuditoriaService,
)
from Backend.moduloEventos.models import (
    Barrio,
    PuntoInteres,
    Coordinador,
    Simpatizante,
    HorarioDisponible,
    Evento,
    EventoTipo,
    EventoPuntoInteres,
    Asignacion,
    Cobertura,
    Observacion,
    ParticipacionExterna,
    MaterialPublicitario,
    EstadoMaterial,
    Auditoria,
)

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Helpers internos de serialización
# ─────────────────────────────────────────────────────────────────────────────

def _str_fields(obj: Dict[str, Any]) -> Dict[str, Any]:
    """Convierte UUID y datetime a str para respuestas JSON-friendly."""
    import datetime, uuid
    result = {}
    for k, v in obj.items():
        if isinstance(v, uuid.UUID):
            result[k] = str(v)
        elif isinstance(v, (datetime.date, datetime.time, datetime.datetime)):
            result[k] = str(v)
        else:
            result[k] = v
    return result


def _serialize(obj: Optional[Dict]) -> Optional[Dict]:
    if obj is None:
        return None
    return _str_fields(obj)


def _serialize_list(objs: List[Dict]) -> List[Dict]:
    return [_str_fields(o) for o in objs]


# =============================================================================
# BARRIO
# =============================================================================

class BarrioService(IBarrioService):

    async def listar_barrios(self) -> List[Dict[str, Any]]:
        logger.debug("[BarrioService] listar_barrios: consultando todos los barrios")
        result = _serialize_list(await sync_to_async(Barrio.get_all)())
        logger.info("[BarrioService] listar_barrios: %d barrios encontrados", len(result))
        return result

    async def obtener_barrio(self, barrio_id: str) -> Optional[Dict[str, Any]]:
        logger.debug("[BarrioService] obtener_barrio: barrio_id=%s", barrio_id)
        result = _serialize(await sync_to_async(Barrio.get_by_id)(barrio_id))
        if result is None:
            logger.warning("[BarrioService] obtener_barrio: barrio_id=%s no encontrado", barrio_id)
        else:
            logger.info("[BarrioService] obtener_barrio: encontrado barrio_id=%s", barrio_id)
        return result

    async def crear_barrio(self, nombre: str) -> Dict[str, Any]:
        logger.debug("[BarrioService] crear_barrio: nombre='%s'", nombre)
        barrio_id = await sync_to_async(Barrio.create)(nombre)
        result = _serialize(await sync_to_async(Barrio.get_by_id)(barrio_id))
        logger.info("[BarrioService] crear_barrio: creado barrio_id=%s nombre='%s'", barrio_id, nombre)
        return result

    async def actualizar_barrio(self, barrio_id: str, nombre: str) -> Optional[Dict[str, Any]]:
        logger.debug("[BarrioService] actualizar_barrio: barrio_id=%s nombre='%s'", barrio_id, nombre)
        await sync_to_async(Barrio.update)(barrio_id, nombre)
        result = _serialize(await sync_to_async(Barrio.get_by_id)(barrio_id))
        logger.info("[BarrioService] actualizar_barrio: actualizado barrio_id=%s", barrio_id)
        return result

    async def eliminar_barrio(self, barrio_id: str) -> bool:
        logger.debug("[BarrioService] eliminar_barrio: barrio_id=%s", barrio_id)
        result = await sync_to_async(Barrio.delete)(barrio_id)
        logger.info("[BarrioService] eliminar_barrio: barrio_id=%s eliminado=%s", barrio_id, result)
        return result


# =============================================================================
# PUNTO DE INTERÉS
# =============================================================================

class PuntoInteresService(IPuntoInteresService):

    async def listar_puntos(self, barrio_id: str) -> List[Dict[str, Any]]:
        logger.debug("[PuntoInteresService] listar_puntos: barrio_id=%s", barrio_id)
        result = _serialize_list(await sync_to_async(PuntoInteres.get_by_barrio)(barrio_id))
        logger.info("[PuntoInteresService] listar_puntos: %d puntos en barrio_id=%s", len(result), barrio_id)
        return result

    async def obtener_punto(self, punto_id: str) -> Optional[Dict[str, Any]]:
        logger.debug("[PuntoInteresService] obtener_punto: punto_id=%s", punto_id)
        result = _serialize(await sync_to_async(PuntoInteres.get_by_id)(punto_id))
        if result is None:
            logger.warning("[PuntoInteresService] obtener_punto: punto_id=%s no encontrado", punto_id)
        else:
            logger.info("[PuntoInteresService] obtener_punto: encontrado punto_id=%s", punto_id)
        return result

    async def crear_punto(self, nombre: str, barrio_id: str) -> Dict[str, Any]:
        logger.debug("[PuntoInteresService] crear_punto: nombre='%s' barrio_id=%s", nombre, barrio_id)
        punto_id = await sync_to_async(PuntoInteres.create)(nombre, barrio_id)
        result = _serialize(await sync_to_async(PuntoInteres.get_by_id)(punto_id))
        logger.info("[PuntoInteresService] crear_punto: creado punto_id=%s", punto_id)
        return result

    async def actualizar_punto(
        self,
        punto_id: str,
        nombre: str,
        barrio_id: str,
    ) -> Optional[Dict[str, Any]]:
        logger.debug(
            "[PuntoInteresService] actualizar_punto: punto_id=%s nombre='%s' barrio_id=%s",
            punto_id, nombre, barrio_id,
        )
        await sync_to_async(PuntoInteres.update)(punto_id, nombre, barrio_id)
        result = _serialize(await sync_to_async(PuntoInteres.get_by_id)(punto_id))
        logger.info("[PuntoInteresService] actualizar_punto: actualizado punto_id=%s", punto_id)
        return result

    async def eliminar_punto(self, punto_id: str) -> bool:
        logger.debug("[PuntoInteresService] eliminar_punto: punto_id=%s", punto_id)
        result = await sync_to_async(PuntoInteres.delete)(punto_id)
        logger.info("[PuntoInteresService] eliminar_punto: punto_id=%s eliminado=%s", punto_id, result)
        return result


# =============================================================================
# COORDINADOR
# =============================================================================

class CoordinadorService(ICoordinadorService):

    @staticmethod
    def _hash(password_plano: str) -> str:
        import hashlib
        return hashlib.sha256(password_plano.encode()).hexdigest()

    async def listar_coordinadores(self) -> List[Dict[str, Any]]:
        logger.debug("[CoordinadorService] listar_coordinadores: consultando todos")
        result = _serialize_list(await sync_to_async(Coordinador.get_all)())
        logger.info("[CoordinadorService] listar_coordinadores: %d coordinadores encontrados", len(result))
        return result

    async def obtener_coordinador(self, coordinador_id: str) -> Optional[Dict[str, Any]]:
        logger.debug("[CoordinadorService] obtener_coordinador: coordinador_id=%s", coordinador_id)
        result = _serialize(await sync_to_async(Coordinador.get_by_id)(coordinador_id))
        if result is None:
            logger.warning("[CoordinadorService] obtener_coordinador: coordinador_id=%s no encontrado", coordinador_id)
        else:
            logger.info("[CoordinadorService] obtener_coordinador: encontrado coordinador_id=%s", coordinador_id)
        return result

    async def crear_coordinador(
        self, nombre: str, email: str, password_plano: str
    ) -> Dict[str, Any]:
        logger.debug("[CoordinadorService] crear_coordinador: nombre='%s' email='%s'", nombre, email)
        coordinador_id = await sync_to_async(Coordinador.create)(nombre, email, self._hash(password_plano))
        result = _serialize(await sync_to_async(Coordinador.get_by_id)(coordinador_id))
        logger.info("[CoordinadorService] crear_coordinador: creado coordinador_id=%s", coordinador_id)
        return result

    async def actualizar_coordinador(
        self, coordinador_id: str, nombre: str, email: str
    ) -> Optional[Dict[str, Any]]:
        logger.debug(
            "[CoordinadorService] actualizar_coordinador: coordinador_id=%s nombre='%s' email='%s'",
            coordinador_id, nombre, email,
        )
        await sync_to_async(Coordinador.update)(coordinador_id, nombre, email)
        result = _serialize(await sync_to_async(Coordinador.get_by_id)(coordinador_id))
        logger.info("[CoordinadorService] actualizar_coordinador: actualizado coordinador_id=%s", coordinador_id)
        return result

    async def cambiar_password(self, coordinador_id: str, password_plano: str) -> bool:
        logger.debug("[CoordinadorService] cambiar_password: coordinador_id=%s", coordinador_id)
        result = await sync_to_async(Coordinador.update_password)(coordinador_id, self._hash(password_plano))
        logger.info("[CoordinadorService] cambiar_password: coordinador_id=%s resultado=%s", coordinador_id, result)
        return result


# =============================================================================
# SIMPATIZANTE
# =============================================================================

class SimpatizanteService(ISimpatizanteService):

    async def listar_simpatizantes(
        self, barrio_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        logger.debug("[SimpatizanteService] listar_simpatizantes: barrio_id=%s", barrio_id)
        if barrio_id:
            result = _serialize_list(await sync_to_async(Simpatizante.get_by_barrio)(barrio_id))
        else:
            result = _serialize_list(await sync_to_async(Simpatizante.get_all)())
        logger.info("[SimpatizanteService] listar_simpatizantes: %d simpatizantes encontrados", len(result))
        return result

    async def obtener_simpatizante(self, simpatizante_id: str) -> Optional[Dict[str, Any]]:
        logger.debug("[SimpatizanteService] obtener_simpatizante: simpatizante_id=%s", simpatizante_id)
        result = _serialize(await sync_to_async(Simpatizante.get_by_id)(simpatizante_id))
        if result is None:
            logger.warning("[SimpatizanteService] obtener_simpatizante: simpatizante_id=%s no encontrado", simpatizante_id)
        else:
            logger.info("[SimpatizanteService] obtener_simpatizante: encontrado simpatizante_id=%s", simpatizante_id)
        return result

    async def crear_simpatizante(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        logger.debug("[SimpatizanteService] crear_simpatizante: cedula=%s nombre='%s'", payload.get("cedula"), payload.get("nombre"))
        simpatizante_id = await sync_to_async(Simpatizante.create)(
            nombre=payload["nombre"],
            cedula=payload["cedula"],
            telefono=payload.get("telefono"),
            edad=payload["edad"],
            ocupacion=payload["ocupacion"],
            lugar_votacion=payload["lugar_votacion"],
            puesto_votacion=payload["puesto_votacion"],
            mesa_votacion=payload["mesa_votacion"],
            opinion_politica=payload.get("opinion_politica"),
            barrio_id=payload.get("barrio_id"),
            email=payload.get("email"),
            direccion=payload.get("direccion"),
            organizacion=payload.get("organizacion"),
        )
        result = _serialize(await sync_to_async(Simpatizante.get_by_id)(simpatizante_id))
        logger.info("[SimpatizanteService] crear_simpatizante: creado simpatizante_id=%s", simpatizante_id)
        return result

    async def actualizar_simpatizante(
        self, simpatizante_id: str, payload: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        logger.debug("[SimpatizanteService] actualizar_simpatizante: simpatizante_id=%s campos=%s", simpatizante_id, list(payload.keys()))
        await sync_to_async(Simpatizante.update)(simpatizante_id, payload)
        result = _serialize(await sync_to_async(Simpatizante.get_by_id)(simpatizante_id))
        logger.info("[SimpatizanteService] actualizar_simpatizante: actualizado simpatizante_id=%s", simpatizante_id)
        return result

    async def eliminar_simpatizante(self, simpatizante_id: str) -> bool:
        logger.debug("[SimpatizanteService] eliminar_simpatizante: simpatizante_id=%s", simpatizante_id)
        result = await sync_to_async(Simpatizante.delete)(simpatizante_id)
        logger.info("[SimpatizanteService] eliminar_simpatizante: simpatizante_id=%s eliminado=%s", simpatizante_id, result)
        return result


# =============================================================================
# HORARIO DISPONIBLE
# =============================================================================

class HorarioDisponibleService(IHorarioDisponibleService):

    async def listar_horarios(self, simpatizante_id: str) -> List[Dict[str, Any]]:
        logger.debug("[HorarioDisponibleService] listar_horarios: simpatizante_id=%s", simpatizante_id)
        result = _serialize_list(await sync_to_async(HorarioDisponible.get_by_simpatizante)(simpatizante_id))
        logger.info("[HorarioDisponibleService] listar_horarios: %d horarios para simpatizante_id=%s", len(result), simpatizante_id)
        return result

    async def crear_horario(
        self,
        simpatizante_id: str,
        dia_semana: str,
        hora_inicio: str,
        hora_fin: str,
    ) -> Dict[str, Any]:
        logger.debug(
            "[HorarioDisponibleService] crear_horario: simpatizante_id=%s dia=%s %s-%s",
            simpatizante_id, dia_semana, hora_inicio, hora_fin,
        )
        horario_id = await sync_to_async(HorarioDisponible.create)(
            simpatizante_id, dia_semana, hora_inicio, hora_fin
        )
        rows = _serialize_list(await sync_to_async(HorarioDisponible.get_by_simpatizante)(simpatizante_id))
        result = next(r for r in rows if r["id"] == horario_id)
        logger.info("[HorarioDisponibleService] crear_horario: creado horario_id=%s", horario_id)
        return result

    async def eliminar_horario(self, horario_id: str) -> bool:
        logger.debug("[HorarioDisponibleService] eliminar_horario: horario_id=%s", horario_id)
        result = await sync_to_async(HorarioDisponible.delete)(horario_id)
        logger.info("[HorarioDisponibleService] eliminar_horario: horario_id=%s eliminado=%s", horario_id, result)
        return result

    async def consultar_disponibles_para_evento(
        self,
        fecha: str,
        dia_semana: str,
        hora_inicio: str,
        hora_fin: str,
    ) -> List[Dict[str, Any]]:
        logger.debug(
            "[HorarioDisponibleService] consultar_disponibles_para_evento: fecha=%s dia=%s %s-%s",
            fecha, dia_semana, hora_inicio, hora_fin,
        )
        result = _serialize_list(
            await sync_to_async(HorarioDisponible.get_disponibles_para_evento)(
                fecha, dia_semana, hora_inicio, hora_fin
            )
        )
        logger.info("[HorarioDisponibleService] consultar_disponibles_para_evento: %d disponibles", len(result))
        return result


# =============================================================================
# EVENTO  (RF-EV-01 al RF-EV-05)
# =============================================================================

class EventoService(IEventoService):

    async def listar_eventos(self) -> List[Dict[str, Any]]:
        logger.debug("[EventoService] listar_eventos: consultando todos los eventos")
        eventos = _serialize_list(await sync_to_async(Evento.get_all)())
        for ev in eventos:
            ev["tipos"] = _serialize_list(await sync_to_async(EventoTipo.get_by_evento)(ev["id"]))
        logger.info("[EventoService] listar_eventos: %d eventos encontrados", len(eventos))
        return eventos

    async def obtener_evento(self, evento_id: str) -> Optional[Dict[str, Any]]:
        logger.debug("[EventoService] obtener_evento: evento_id=%s", evento_id)
        ev = _serialize(await sync_to_async(Evento.get_by_id)(evento_id))
        if ev is None:
            logger.warning("[EventoService] obtener_evento: evento_id=%s no encontrado", evento_id)
            return None
        ev["tipos"] = _serialize_list(await sync_to_async(EventoTipo.get_by_evento)(evento_id))
        logger.info("[EventoService] obtener_evento: encontrado evento_id=%s con %d tipos", evento_id, len(ev["tipos"]))
        return ev

     
    async def crear_evento(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        tipos = payload.pop("tipos", [])
        logger.debug("[EventoService] crear_evento: nombre='%s' coordinador_id=%s tipos=%s", payload.get("nombre"), payload.get("coordinador_id"), tipos)
        evento_id = await sync_to_async(Evento.create)(
            nombre=payload["nombre"],
            descripcion=payload.get("descripcion"),
            fecha=payload["fecha"],
            hora_inicio=payload["hora_inicio"],
            hora_fin=payload["hora_fin"],
            duracion_min=payload.get("duracion_min"),
            objetivo=payload.get("objetivo"),
            resultado_esperado=payload.get("resultado_esperado"),
            resultado_obtenido=None,
            capacidad=payload.get("capacidad", 0),
            estado=payload.get("estado", "PLANIFICADO"),
            coordinador_id=payload["coordinador_id"],
            barrio_id=payload.get("barrio_id"),
        )
        for tipo in tipos:
            await sync_to_async(EventoTipo.create)(evento_id, tipo)
            logger.debug("[EventoService] crear_evento: tipo '%s' agregado a evento_id=%s", tipo, evento_id)
        result = await self.obtener_evento(evento_id)
        logger.info("[EventoService] crear_evento: creado evento_id=%s", evento_id)
        return result

     
    async def actualizar_evento(
        self, evento_id: str, payload: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        tipos = payload.pop("tipos", None)
        logger.debug("[EventoService] actualizar_evento: evento_id=%s campos=%s", evento_id, list(payload.keys()))
        await sync_to_async(Evento.update)(evento_id, payload)
        if tipos is not None:
            logger.debug("[EventoService] actualizar_evento: reemplazando tipos para evento_id=%s -> %s", evento_id, tipos)
            await sync_to_async(EventoTipo.delete_by_evento)(evento_id)
            for tipo in tipos:
                await sync_to_async(EventoTipo.create)(evento_id, tipo)
        result = await self.obtener_evento(evento_id)
        logger.info("[EventoService] actualizar_evento: actualizado evento_id=%s", evento_id)
        return result

    async def actualizar_estado(
        self, evento_id: str, estado: str
    ) -> Optional[Dict[str, Any]]:
        estados_validos = {"PLANIFICADO", "EN_EJECUCION", "FINALIZADO", "CANCELADO"}
        logger.debug("[EventoService] actualizar_estado: evento_id=%s estado='%s'", evento_id, estado)
        if estado not in estados_validos:
            logger.error("[EventoService] actualizar_estado: estado inválido '%s'", estado)
            raise ValueError(f"Estado inválido. Opciones: {estados_validos}")
        await sync_to_async(Evento.update_estado)(evento_id, estado)
        result = await self.obtener_evento(evento_id)
        logger.info("[EventoService] actualizar_estado: evento_id=%s -> estado='%s'", evento_id, estado)
        return result

    async def eliminar_evento(self, evento_id: str) -> bool:
        logger.debug("[EventoService] eliminar_evento: evento_id=%s", evento_id)
        result = await sync_to_async(Evento.delete)(evento_id)
        logger.info("[EventoService] eliminar_evento: evento_id=%s eliminado=%s", evento_id, result)
        return result

    async def agregar_tipo(self, evento_id: str, tipo: str) -> Dict[str, Any]:
        logger.debug("[EventoService] agregar_tipo: evento_id=%s tipo='%s'", evento_id, tipo)
        tipo_id = await sync_to_async(EventoTipo.create)(evento_id, tipo)
        logger.info("[EventoService] agregar_tipo: tipo_id=%s agregado a evento_id=%s", tipo_id, evento_id)
        return {"id": tipo_id, "evento_id": evento_id, "tipo": tipo}

    async def eliminar_tipo(self, tipo_id: str) -> bool:
        logger.debug("[EventoService] eliminar_tipo: tipo_id=%s", tipo_id)
        result = await sync_to_async(EventoTipo.delete)(tipo_id)
        logger.info("[EventoService] eliminar_tipo: tipo_id=%s eliminado=%s", tipo_id, result)
        return result


# =============================================================================
# EVENTO PUNTO DE INTERÉS
# =============================================================================

class EventoPuntoInteresService(IEventoPuntoInteresService):

    async def listar_puntos_evento(self, evento_id: str) -> List[Dict[str, Any]]:
        logger.debug("[EventoPuntoInteresService] listar_puntos_evento: evento_id=%s", evento_id)
        result = _serialize_list(await sync_to_async(EventoPuntoInteres.get_by_evento)(evento_id))
        logger.info("[EventoPuntoInteresService] listar_puntos_evento: %d puntos para evento_id=%s", len(result), evento_id)
        return result

    async def agregar_punto(self, evento_id: str, punto_interes_id: str) -> Dict[str, Any]:
        logger.debug("[EventoPuntoInteresService] agregar_punto: evento_id=%s punto_interes_id=%s", evento_id, punto_interes_id)
        relacion_id = await sync_to_async(EventoPuntoInteres.create)(evento_id, punto_interes_id)
        rows = _serialize_list(await sync_to_async(EventoPuntoInteres.get_by_evento)(evento_id))
        result = next(r for r in rows if r["id"] == relacion_id)
        logger.info("[EventoPuntoInteresService] agregar_punto: relacion_id=%s creada", relacion_id)
        return result

    async def remover_punto(self, evento_punto_interes_id: str) -> bool:
        logger.debug("[EventoPuntoInteresService] remover_punto: evento_punto_interes_id=%s", evento_punto_interes_id)
        result = await sync_to_async(EventoPuntoInteres.delete)(evento_punto_interes_id)
        logger.info("[EventoPuntoInteresService] remover_punto: id=%s eliminado=%s", evento_punto_interes_id, result)
        return result

     
    async def reemplazar_puntos(
        self, evento_id: str, punto_interes_ids: List[str]
    ) -> List[Dict[str, Any]]:
        logger.debug("[EventoPuntoInteresService] reemplazar_puntos: evento_id=%s nuevos_ids=%s", evento_id, punto_interes_ids)
        await sync_to_async(EventoPuntoInteres.delete_by_evento)(evento_id)
        for punto_id in punto_interes_ids:
            await sync_to_async(EventoPuntoInteres.create)(evento_id, punto_id)
        result = _serialize_list(await sync_to_async(EventoPuntoInteres.get_by_evento)(evento_id))
        logger.info("[EventoPuntoInteresService] reemplazar_puntos: %d puntos asignados a evento_id=%s", len(result), evento_id)
        return result


# =============================================================================
# ASIGNACIÓN  (RF-EV-07 al RF-EV-14, RF-EV-23)
# =============================================================================

class AsignacionService(IAsignacionService):

    async def listar_asignaciones(self, evento_id: str) -> List[Dict[str, Any]]:
        logger.debug("[AsignacionService] listar_asignaciones: evento_id=%s", evento_id)
        result = _serialize_list(await sync_to_async(Asignacion.get_by_evento)(evento_id))
        logger.info("[AsignacionService] listar_asignaciones: %d asignaciones para evento_id=%s", len(result), evento_id)
        return result

     
    async def asignar_manual(
        self,
        evento_id: str,
        simpatizante_id: str,
        rol: Optional[str],
    ) -> Dict[str, Any]:
        logger.debug("[AsignacionService] asignar_manual: evento_id=%s simpatizante_id=%s rol=%s", evento_id, simpatizante_id, rol)
        if await sync_to_async(Asignacion.existe)(evento_id, simpatizante_id):
            logger.warning("[AsignacionService] asignar_manual: simpatizante_id=%s ya está asignado a evento_id=%s", simpatizante_id, evento_id)
            raise ValueError("El simpatizante ya está asignado a este evento.")
        asignacion_id = await sync_to_async(Asignacion.create)(evento_id, simpatizante_id, rol, "MANUAL")
        simpatizante = await sync_to_async(Simpatizante.get_by_id)(simpatizante_id)
        if simpatizante:
            await sync_to_async(Cobertura.incrementar_asignados)(evento_id, simpatizante["ocupacion"])
            logger.debug("[AsignacionService] asignar_manual: cobertura incrementada para ocupacion='%s'", simpatizante["ocupacion"])
        result = _serialize(await sync_to_async(Asignacion.get_by_id)(asignacion_id))
        logger.info("[AsignacionService] asignar_manual: asignacion_id=%s creada (MANUAL)", asignacion_id)
        return result

     
    async def asignar_automatico(
        self,
        evento_id: str,
        criterios: Dict[str, bool],
    ) -> List[Dict[str, Any]]:
        """
        RF-EV-08 — Asignación automática respetando los criterios configurables.
        Criterios soportados:
          - usar_horario (bool): filtra por compatibilidad de horario
          - usar_ocupacion (bool): prioriza la ocupación requerida por cobertura
          - usar_participacion_previa (bool): excluye quienes ya participaron en el barrio
        """
        logger.debug("[AsignacionService] asignar_automatico: evento_id=%s criterios=%s", evento_id, criterios)

        evento = await sync_to_async(Evento.get_by_id)(evento_id)
        if not evento:
            logger.error("[AsignacionService] asignar_automatico: evento_id=%s no encontrado", evento_id)
            raise ValueError("Evento no encontrado.")

        # Candidatos base: todos los simpatizantes del barrio del evento
        if evento["barrio_id"]:
            candidatos = await sync_to_async(Simpatizante.get_by_barrio)(evento["barrio_id"])
            logger.debug("[AsignacionService] asignar_automatico: %d candidatos en barrio_id=%s", len(candidatos), evento["barrio_id"])
        else:
            candidatos = await sync_to_async(Simpatizante.get_all)()
            logger.debug("[AsignacionService] asignar_automatico: %d candidatos (sin filtro de barrio)", len(candidatos))

        # Filtro por horario (RF-EV-22)
        if criterios.get("usar_horario", True):
            import datetime
            fecha_dt = evento["fecha"]
            if isinstance(fecha_dt, str):
                fecha_dt = datetime.date.fromisoformat(fecha_dt)
            dia_semana = fecha_dt.strftime("%A").upper()
            disponibles_ids = {
                str(d["id"])
                for d in await sync_to_async(HorarioDisponible.get_disponibles_para_evento)(
                    str(fecha_dt),
                    dia_semana,
                    str(evento["hora_inicio"]),
                    str(evento["hora_fin"]),
                )
            }
            candidatos = [c for c in candidatos if str(c["id"]) in disponibles_ids]
            logger.debug("[AsignacionService] asignar_automatico: %d candidatos tras filtro de horario", len(candidatos))

        # Filtro por participación previa en el barrio (RF-EV-23)
        if criterios.get("usar_participacion_previa", True):
            sin_conflicto = []
            for c in candidatos:
                barrios_recientes = await sync_to_async(Asignacion.get_barrios_recientes_simpatizante)(
                    str(c["id"])
                )
                if not barrios_recientes:
                    sin_conflicto.append(c)
                else:
                    logger.info(
                        "[AsignacionService] asignar_automatico: simpatizante_id=%s omitido por participación territorial reciente en barrio",
                        c["id"],
                    )
            candidatos = sin_conflicto
            logger.debug("[AsignacionService] asignar_automatico: %d candidatos tras filtro participación previa", len(candidatos))

        # Excluir ya asignados
        ya_asignados = {
            str(a["simpatizante_id"])
            for a in await sync_to_async(Asignacion.get_by_evento)(evento_id)
        }
        candidatos = [c for c in candidatos if str(c["id"]) not in ya_asignados]
        logger.debug("[AsignacionService] asignar_automatico: %d candidatos tras excluir ya asignados", len(candidatos))

        # Ordenar por ocupación si se usa cobertura
        if criterios.get("usar_ocupacion", True):
            coberturas = {
                c["ocupacion"]: c["requeridos"]
                for c in await sync_to_async(Cobertura.get_by_evento)(evento_id)
            }
            candidatos.sort(
                key=lambda c: coberturas.get(c["ocupacion"], 0),
                reverse=True,
            )
            logger.debug("[AsignacionService] asignar_automatico: candidatos ordenados por ocupación")

        # Asignar hasta completar capacidad del evento
        capacidad = evento.get("capacidad", 0)
        asignados = []
        for candidato in candidatos:
            if capacidad and len(asignados) >= capacidad:
                logger.debug("[AsignacionService] asignar_automatico: capacidad=%d alcanzada, deteniendo", capacidad)
                break
            asignacion_id = await sync_to_async(Asignacion.create)(
                evento_id, str(candidato["id"]), None, "AUTOMATICO"
            )
            await sync_to_async(Cobertura.incrementar_asignados)(evento_id, candidato["ocupacion"])
            asignados.append(_serialize(await sync_to_async(Asignacion.get_by_id)(asignacion_id)))
            logger.debug("[AsignacionService] asignar_automatico: asignado simpatizante_id=%s (asignacion_id=%s)", candidato["id"], asignacion_id)

        logger.info("[AsignacionService] asignar_automatico: %d asignaciones creadas para evento_id=%s", len(asignados), evento_id)
        return asignados

    async def actualizar_rol(
        self, asignacion_id: str, rol: str
    ) -> Optional[Dict[str, Any]]:
        logger.debug("[AsignacionService] actualizar_rol: asignacion_id=%s rol='%s'", asignacion_id, rol)
        await sync_to_async(Asignacion.update_rol)(asignacion_id, rol)
        result = _serialize(await sync_to_async(Asignacion.get_by_id)(asignacion_id))
        logger.info("[AsignacionService] actualizar_rol: asignacion_id=%s actualizado a rol='%s'", asignacion_id, rol)
        return result

    async def remover_asignacion(self, asignacion_id: str) -> bool:
        logger.debug("[AsignacionService] remover_asignacion: asignacion_id=%s", asignacion_id)
        
        # Obtener la asignación ANTES de borrarla para saber la ocupación
        asignacion = await sync_to_async(Asignacion.get_by_id)(asignacion_id)
        if asignacion:
            simpatizante = await sync_to_async(Simpatizante.get_by_id)(str(asignacion["simpatizante_id"]))
            if simpatizante:
                await sync_to_async(Cobertura.decrementar_asignados)(
                    str(asignacion["evento_id"]), simpatizante["ocupacion"]
                )

        result = await sync_to_async(Asignacion.delete)(asignacion_id)
        logger.info("[AsignacionService] remover_asignacion: asignacion_id=%s eliminado=%s", asignacion_id, result)
        return result

    async def registrar_asistencia(
        self, asignacion_id: str, asistio: bool
    ) -> Optional[Dict[str, Any]]:
        logger.debug("[AsignacionService] registrar_asistencia: asignacion_id=%s asistio=%s", asignacion_id, asistio)
        await sync_to_async(Asignacion.registrar_asistencia)(asignacion_id, asistio)
        result = _serialize(await sync_to_async(Asignacion.get_by_id)(asignacion_id))
        logger.info("[AsignacionService] registrar_asistencia: asignacion_id=%s registrada", asignacion_id)
        return result

    async def verificar_participacion_territorial(
        self, simpatizante_id: str, evento_id: str
    ) -> Dict[str, Any]:
        """
        RF-EV-23 — Advierte si hay participación reciente en el mismo barrio.
        Usa get_barrios_recientes_simpatizante (sector fue eliminado del esquema).
        """
        logger.debug("[AsignacionService] verificar_participacion_territorial: simpatizante_id=%s evento_id=%s", simpatizante_id, evento_id)
        evento = await sync_to_async(Evento.get_by_id)(evento_id)
        if not evento:
            logger.warning("[AsignacionService] verificar_participacion_territorial: evento_id=%s no encontrado", evento_id)
            return {"advertencia": False, "barrios": []}
        barrios_recientes = await sync_to_async(Asignacion.get_barrios_recientes_simpatizante)(simpatizante_id)
        advertencia = len(barrios_recientes) > 0
        logger.info(
            "[AsignacionService] verificar_participacion_territorial: simpatizante_id=%s advertencia=%s barrios=%s",
            simpatizante_id, advertencia, barrios_recientes,
        )
        return {
            "advertencia": advertencia,
            "barrios": barrios_recientes,
            "mensaje": (
                "Esta persona participó recientemente en actividades del mismo barrio."
                if advertencia
                else "Sin participación territorial reciente."
            ),
        }


# =============================================================================
# COBERTURA  (RF-EV-11)
# =============================================================================

class CoberturaService(ICoberturaService):

    async def listar_cobertura(self, evento_id: str) -> List[Dict[str, Any]]:
        logger.debug("[CoberturaService] listar_cobertura: evento_id=%s", evento_id)
        result = _serialize_list(await sync_to_async(Cobertura.get_by_evento)(evento_id))
        logger.info("[CoberturaService] listar_cobertura: %d registros para evento_id=%s", len(result), evento_id)
        return result

    async def registrar_cobertura(
        self, evento_id: str, ocupacion: str, requeridos: int
    ) -> Dict[str, Any]:
        logger.debug("[CoberturaService] registrar_cobertura: evento_id=%s ocupacion='%s' requeridos=%d", evento_id, ocupacion, requeridos)
        cobertura_id = await sync_to_async(Cobertura.create)(evento_id, ocupacion, requeridos)
        rows = _serialize_list(await sync_to_async(Cobertura.get_by_evento)(evento_id))
        result = next(r for r in rows if r["id"] == cobertura_id)
        logger.info("[CoberturaService] registrar_cobertura: creada cobertura_id=%s", cobertura_id)
        return result

    async def actualizar_cobertura(
        self,
        cobertura_id: str,
        ocupacion: str,
        requeridos: int,
        asignados: int,
    ) -> Optional[Dict[str, Any]]:
        logger.debug(
            "[CoberturaService] actualizar_cobertura: cobertura_id=%s ocupacion='%s' requeridos=%d asignados=%d",
            cobertura_id, ocupacion, requeridos, asignados,
        )
        await sync_to_async(Cobertura.update)(cobertura_id, ocupacion, requeridos, asignados)
        result = _serialize(await sync_to_async(Cobertura.get_by_evento_by_id)(cobertura_id))
        logger.info("[CoberturaService] actualizar_cobertura: actualizada cobertura_id=%s", cobertura_id)
        return result

    async def eliminar_cobertura(self, cobertura_id: str) -> bool:
        logger.debug("[CoberturaService] eliminar_cobertura: cobertura_id=%s", cobertura_id)
        result = await sync_to_async(Cobertura.delete)(cobertura_id)
        logger.info("[CoberturaService] eliminar_cobertura: cobertura_id=%s eliminada=%s", cobertura_id, result)
        return result


# =============================================================================
# OBSERVACIÓN  (RF-EV-12, RF-EV-13)
# =============================================================================

class ObservacionService(IObservacionService):

    MOMENTOS_VALIDOS = {"INICIAL", "FINAL"}

    async def listar_observaciones(self, evento_id: str) -> List[Dict[str, Any]]:
        logger.debug("[ObservacionService] listar_observaciones: evento_id=%s", evento_id)
        result = _serialize_list(await sync_to_async(Observacion.get_by_evento)(evento_id))
        logger.info("[ObservacionService] listar_observaciones: %d observaciones para evento_id=%s", len(result), evento_id)
        return result

    async def registrar_observacion(
        self, evento_id: str, momento: str, contenido: str
    ) -> Dict[str, Any]:
        logger.debug("[ObservacionService] registrar_observacion: evento_id=%s momento='%s'", evento_id, momento)
        if momento not in self.MOMENTOS_VALIDOS:
            logger.error("[ObservacionService] registrar_observacion: momento inválido '%s'", momento)
            raise ValueError(f"momento debe ser uno de: {self.MOMENTOS_VALIDOS}")
        obs_id = await sync_to_async(Observacion.create)(evento_id, momento, contenido)
        rows = _serialize_list(await sync_to_async(Observacion.get_by_evento)(evento_id))
        result = next(r for r in rows if r["id"] == obs_id)
        logger.info("[ObservacionService] registrar_observacion: creada obs_id=%s momento='%s'", obs_id, momento)
        return result

    async def eliminar_observacion(self, observacion_id: str) -> bool:
        logger.debug("[ObservacionService] eliminar_observacion: observacion_id=%s", observacion_id)
        result = await sync_to_async(Observacion.delete)(observacion_id)
        logger.info("[ObservacionService] eliminar_observacion: observacion_id=%s eliminada=%s", observacion_id, result)
        return result


# =============================================================================
# PARTICIPACIÓN EXTERNA  (RF-EV-18)
# =============================================================================

class ParticipacionExternaService(IParticipacionExternaService):

    async def obtener_participacion(self, evento_id: str) -> Optional[Dict[str, Any]]:
        logger.debug("[ParticipacionExternaService] obtener_participacion: evento_id=%s", evento_id)
        result = _serialize(await sync_to_async(ParticipacionExterna.get_by_evento)(evento_id))
        if result is None:
            logger.warning("[ParticipacionExternaService] obtener_participacion: sin registro para evento_id=%s", evento_id)
        else:
            logger.info("[ParticipacionExternaService] obtener_participacion: encontrado para evento_id=%s", evento_id)
        return result

    async def registrar_participacion(
        self, evento_id: str, cantidad: int, notas: Optional[str]
    ) -> Dict[str, Any]:
        logger.debug("[ParticipacionExternaService] registrar_participacion: evento_id=%s cantidad=%d", evento_id, cantidad)
        existente = await sync_to_async(ParticipacionExterna.get_by_evento)(evento_id)
        if existente:
            logger.debug("[ParticipacionExternaService] registrar_participacion: actualizando registro existente id=%s", existente["id"])
            await sync_to_async(ParticipacionExterna.update)(str(existente["id"]), cantidad, notas)
        else:
            await sync_to_async(ParticipacionExterna.create)(evento_id, cantidad, notas)
            logger.debug("[ParticipacionExternaService] registrar_participacion: nuevo registro creado para evento_id=%s", evento_id)
        result = _serialize(await sync_to_async(ParticipacionExterna.get_by_evento)(evento_id))
        logger.info("[ParticipacionExternaService] registrar_participacion: registrada para evento_id=%s", evento_id)
        return result

    async def actualizar_participacion(
        self,
        participacion_id: str,
        cantidad: int,
        notas: Optional[str],
    ) -> Optional[Dict[str, Any]]:
        logger.debug("[ParticipacionExternaService] actualizar_participacion: participacion_id=%s cantidad=%d", participacion_id, cantidad)
        await sync_to_async(ParticipacionExterna.update)(participacion_id, cantidad, notas)
        result = _serialize(await sync_to_async(ParticipacionExterna.get_by_id)(participacion_id))
        logger.info("[ParticipacionExternaService] actualizar_participacion: actualizada participacion_id=%s", participacion_id)
        return result


# =============================================================================
# MATERIAL PUBLICITARIO  (RF-EV-19)
# =============================================================================

class MaterialPublicitarioService(IMaterialPublicitarioService):

    async def obtener_material(self, evento_id: str) -> Optional[Dict[str, Any]]:
        logger.debug("[MaterialPublicitarioService] obtener_material: evento_id=%s", evento_id)
        result = _serialize(await sync_to_async(MaterialPublicitario.get_by_evento)(evento_id))
        if result is None:
            logger.warning("[MaterialPublicitarioService] obtener_material: sin registro para evento_id=%s", evento_id)
        else:
            logger.info("[MaterialPublicitarioService] obtener_material: encontrado para evento_id=%s", evento_id)
        return result

    async def registrar_material(
        self, evento_id: str, entregado: int, restante: int
    ) -> Dict[str, Any]:
        logger.debug("[MaterialPublicitarioService] registrar_material: evento_id=%s entregado=%d restante=%d", evento_id, entregado, restante)
        existente = await sync_to_async(MaterialPublicitario.get_by_evento)(evento_id)
        if existente:
            logger.debug("[MaterialPublicitarioService] registrar_material: actualizando registro existente id=%s", existente["id"])
            await sync_to_async(MaterialPublicitario.update)(str(existente["id"]), entregado, restante)
        else:
            await sync_to_async(MaterialPublicitario.create)(evento_id, entregado, restante)
            logger.debug("[MaterialPublicitarioService] registrar_material: nuevo registro creado para evento_id=%s", evento_id)
        result = _serialize(await sync_to_async(MaterialPublicitario.get_by_evento)(evento_id))
        logger.info("[MaterialPublicitarioService] registrar_material: registrado para evento_id=%s", evento_id)
        return result

    async def actualizar_material(
        self, material_id: str, entregado: int, restante: int
    ) -> Optional[Dict[str, Any]]:
        logger.debug("[MaterialPublicitarioService] actualizar_material: material_id=%s entregado=%d restante=%d", material_id, entregado, restante)
        await sync_to_async(MaterialPublicitario.update)(material_id, entregado, restante)
        result = _serialize(await sync_to_async(MaterialPublicitario.get_by_id)(material_id))
        logger.info("[MaterialPublicitarioService] actualizar_material: actualizado material_id=%s", material_id)
        return result


# =============================================================================
# ESTADO MATERIAL  (RF-EV-20, RF-EV-21, RF-EV-22)
# =============================================================================

class EstadoMaterialService(IEstadoMaterialService):

    ESTADOS_VALIDOS = {"CONSERVADO", "DETERIORADO", "RETIRADO", "VANDALIZADO"}

    async def listar_estados(self, evento_id: str) -> List[Dict[str, Any]]:
        logger.debug("[EstadoMaterialService] listar_estados: evento_id=%s", evento_id)
        result = _serialize_list(await sync_to_async(EstadoMaterial.get_by_evento)(evento_id))
        logger.info("[EstadoMaterialService] listar_estados: %d estados para evento_id=%s", len(result), evento_id)
        return result

    async def registrar_estado(
        self, evento_id: str, estado: str, notas: Optional[str]
    ) -> Dict[str, Any]:
        estado_upper = estado.upper()
        logger.debug("[EstadoMaterialService] registrar_estado: evento_id=%s estado='%s'", evento_id, estado_upper)
        if estado_upper not in self.ESTADOS_VALIDOS:
            logger.error("[EstadoMaterialService] registrar_estado: estado inválido '%s'", estado_upper)
            raise ValueError(f"Estado inválido. Opciones: {self.ESTADOS_VALIDOS}")
        estado_id = await sync_to_async(EstadoMaterial.create)(evento_id, estado_upper, notas)
        rows = _serialize_list(await sync_to_async(EstadoMaterial.get_by_evento)(evento_id))
        result = next(r for r in rows if r["id"] == estado_id)
        logger.info("[EstadoMaterialService] registrar_estado: creado estado_id=%s estado='%s'", estado_id, estado_upper)
        return result

     
    async def cargar_desde_csv(self, archivo_csv: Any) -> Dict[str, Any]:
        """
        RF-EV-21 — Procesa un archivo CSV con columnas:
        numero_evento (evento_id UUID), estado (1-5), notas.
        """
        logger.debug("[EstadoMaterialService] cargar_desde_csv: iniciando carga de CSV")
        if hasattr(archivo_csv, "read"):
            contenido = archivo_csv.read()
            if isinstance(contenido, bytes):
                contenido = contenido.decode("utf-8")
        else:
            contenido = archivo_csv

        lector = csv.DictReader(io.StringIO(contenido))
        filas_ok: List[Dict[str, Any]] = []
        errores: List[str] = []

        for i, fila in enumerate(lector, start=2):
            try:
                evento_id = fila.get("numero_evento", "").strip()
                estado_raw = fila.get("estado", "").strip()
                notas = fila.get("notas", "").strip() or None

                if not evento_id:
                    raise ValueError("numero_evento vacío")
                if not estado_raw:
                    raise ValueError("estado vacío")

                estado_num = int(estado_raw)
                if not (1 <= estado_num <= 5):
                    raise ValueError(f"estado debe ser 1-5, se recibió {estado_num}")

                filas_ok.append({"evento_id": evento_id, "estado": str(estado_num), "notas": notas})
                logger.debug("[EstadoMaterialService] cargar_desde_csv: fila %d válida evento_id=%s estado=%d", i, evento_id, estado_num)
            except Exception as exc:
                errores.append(f"Fila {i}: {exc}")
                logger.warning("[EstadoMaterialService] cargar_desde_csv: error en fila %d -> %s", i, exc)

        logger.debug("[EstadoMaterialService] cargar_desde_csv: %d filas válidas, %d errores", len(filas_ok), len(errores))
        insertados = await sync_to_async(EstadoMaterial.bulk_create_from_csv)(filas_ok)
        logger.info("[EstadoMaterialService] cargar_desde_csv: %d registros insertados, %d errores", insertados, len(errores))
        return {
            "insertados": insertados,
            "errores": errores,
            "total_procesadas": len(filas_ok) + len(errores),
        }

    async def calcular_promedio_estado(self, evento_id: str) -> Optional[float]:
        logger.debug("[EstadoMaterialService] calcular_promedio_estado: evento_id=%s", evento_id)
        result = await sync_to_async(EstadoMaterial.promedio_estado_numerico)(evento_id)
        logger.info("[EstadoMaterialService] calcular_promedio_estado: evento_id=%s promedio=%s", evento_id, result)
        return result


# =============================================================================
# AUDITORÍA
# =============================================================================

class AuditoriaService(IAuditoriaService):

    async def historial_registro(
        self, tabla: str, registro_id: str
    ) -> List[Dict[str, Any]]:
        logger.debug("[AuditoriaService] historial_registro: tabla='%s' registro_id=%s", tabla, registro_id)
        result = _serialize_list(await sync_to_async(Auditoria.get_by_tabla_registro)(tabla, registro_id))
        logger.info("[AuditoriaService] historial_registro: %d registros para tabla='%s' id=%s", len(result), tabla, registro_id)
        return result

    async def registros_recientes(self, limit: int = 50) -> List[Dict[str, Any]]:
        logger.debug("[AuditoriaService] registros_recientes: limit=%d", limit)
        result = _serialize_list(await sync_to_async(Auditoria.get_recientes)(limit))
        logger.info("[AuditoriaService] registros_recientes: %d registros recuperados", len(result))
        return result