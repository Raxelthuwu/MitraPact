import csv
import io
import logging
from typing import Any, Dict, List, Optional

from django.db import transaction

from Backend.moduloEventos.interfaces import (
    IBarrioService,
    ISectorService,
    IPuntoInteresService,
    ICoordinadorService,
    ISimpatizanteService,
    IHorarioDisponibleService,
    IEventoService,
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
    Sector,
    PuntoInteres,
    Coordinador,
    Simpatizante,
    HorarioDisponible,
    Evento,
    EventoTipo,
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

    def listar_barrios(self) -> List[Dict[str, Any]]:
        return _serialize_list(Barrio.get_all())

    def obtener_barrio(self, barrio_id: str) -> Optional[Dict[str, Any]]:
        return _serialize(Barrio.get_by_id(barrio_id))

    def crear_barrio(self, nombre: str) -> Dict[str, Any]:
        barrio_id = Barrio.create(nombre)
        return _serialize(Barrio.get_by_id(barrio_id))

    def actualizar_barrio(self, barrio_id: str, nombre: str) -> Optional[Dict[str, Any]]:
        Barrio.update(barrio_id, nombre)
        return _serialize(Barrio.get_by_id(barrio_id))

    def eliminar_barrio(self, barrio_id: str) -> bool:
        return Barrio.delete(barrio_id)


# =============================================================================
# SECTOR
# =============================================================================

class SectorService(ISectorService):

    def listar_sectores(self, barrio_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if barrio_id:
            return _serialize_list(Sector.get_by_barrio(barrio_id))
        return _serialize_list(Sector.get_all())

    def obtener_sector(self, sector_id: str) -> Optional[Dict[str, Any]]:
        return _serialize(Sector.get_by_id(sector_id))

    def crear_sector(self, nombre: str, barrio_id: str) -> Dict[str, Any]:
        sector_id = Sector.create(nombre, barrio_id)
        return _serialize(Sector.get_by_id(sector_id))

    def actualizar_sector(
        self, sector_id: str, nombre: str, barrio_id: str
    ) -> Optional[Dict[str, Any]]:
        Sector.update(sector_id, nombre, barrio_id)
        return _serialize(Sector.get_by_id(sector_id))

    def eliminar_sector(self, sector_id: str) -> bool:
        return Sector.delete(sector_id)


# =============================================================================
# PUNTO DE INTERÉS
# =============================================================================

class PuntoInteresService(IPuntoInteresService):

    def listar_puntos(self, sector_id: str) -> List[Dict[str, Any]]:
        return _serialize_list(PuntoInteres.get_by_sector(sector_id))

    def obtener_punto(self, punto_id: str) -> Optional[Dict[str, Any]]:
        return _serialize(PuntoInteres.get_by_id(punto_id))

    def crear_punto(self, nombre: str, sector_id: str) -> Dict[str, Any]:
        punto_id = PuntoInteres.create(nombre, sector_id)
        return _serialize(PuntoInteres.get_by_id(punto_id))

    def actualizar_punto(
        self, punto_id: str, nombre: str, sector_id: str
    ) -> Optional[Dict[str, Any]]:
        PuntoInteres.update(punto_id, nombre, sector_id)
        return _serialize(PuntoInteres.get_by_id(punto_id))

    def eliminar_punto(self, punto_id: str) -> bool:
        return PuntoInteres.delete(punto_id)


# =============================================================================
# COORDINADOR
# =============================================================================

class CoordinadorService(ICoordinadorService):

    @staticmethod
    def _hash(password_plano: str) -> str:
        import hashlib
        return hashlib.sha256(password_plano.encode()).hexdigest()

    def listar_coordinadores(self) -> List[Dict[str, Any]]:
        return _serialize_list(Coordinador.get_all())

    def obtener_coordinador(self, coordinador_id: str) -> Optional[Dict[str, Any]]:
        return _serialize(Coordinador.get_by_id(coordinador_id))

    def crear_coordinador(
        self, nombre: str, email: str, password_plano: str
    ) -> Dict[str, Any]:
        coordinador_id = Coordinador.create(nombre, email, self._hash(password_plano))
        return _serialize(Coordinador.get_by_id(coordinador_id))

    def actualizar_coordinador(
        self, coordinador_id: str, nombre: str, email: str
    ) -> Optional[Dict[str, Any]]:
        Coordinador.update(coordinador_id, nombre, email)
        return _serialize(Coordinador.get_by_id(coordinador_id))

    def cambiar_password(self, coordinador_id: str, password_plano: str) -> bool:
        return Coordinador.update_password(coordinador_id, self._hash(password_plano))


# =============================================================================
# SIMPATIZANTE
# =============================================================================

class SimpatizanteService(ISimpatizanteService):

    def listar_simpatizantes(
        self, barrio_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        if barrio_id:
            return _serialize_list(Simpatizante.get_by_barrio(barrio_id))
        return _serialize_list(Simpatizante.get_all())

    def obtener_simpatizante(self, simpatizante_id: str) -> Optional[Dict[str, Any]]:
        return _serialize(Simpatizante.get_by_id(simpatizante_id))

    def crear_simpatizante(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        simpatizante_id = Simpatizante.create(
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
        )
        return _serialize(Simpatizante.get_by_id(simpatizante_id))

    def actualizar_simpatizante(
        self, simpatizante_id: str, payload: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        Simpatizante.update(simpatizante_id, payload)
        return _serialize(Simpatizante.get_by_id(simpatizante_id))

    def eliminar_simpatizante(self, simpatizante_id: str) -> bool:
        return Simpatizante.delete(simpatizante_id)


# =============================================================================
# HORARIO DISPONIBLE
# =============================================================================

class HorarioDisponibleService(IHorarioDisponibleService):

    def listar_horarios(self, simpatizante_id: str) -> List[Dict[str, Any]]:
        return _serialize_list(HorarioDisponible.get_by_simpatizante(simpatizante_id))

    def crear_horario(
        self,
        simpatizante_id: str,
        dia_semana: str,
        hora_inicio: str,
        hora_fin: str,
    ) -> Dict[str, Any]:
        from django.db import connection
        horario_id = HorarioDisponible.create(
            simpatizante_id, dia_semana, hora_inicio, hora_fin
        )
        rows = _serialize_list(HorarioDisponible.get_by_simpatizante(simpatizante_id))
        return next(r for r in rows if r["id"] == horario_id)

    def eliminar_horario(self, horario_id: str) -> bool:
        return HorarioDisponible.delete(horario_id)

    def consultar_disponibles_para_evento(
        self,
        fecha: str,
        dia_semana: str,
        hora_inicio: str,
        hora_fin: str,
    ) -> List[Dict[str, Any]]:
        return _serialize_list(
            HorarioDisponible.get_disponibles_para_evento(
                fecha, dia_semana, hora_inicio, hora_fin
            )
        )


# =============================================================================
# EVENTO  (RF-EV-01 al RF-EV-05)
# =============================================================================

class EventoService(IEventoService):

    def listar_eventos(self) -> List[Dict[str, Any]]:
        eventos = _serialize_list(Evento.get_all())
        for ev in eventos:
            ev["tipos"] = _serialize_list(EventoTipo.get_by_evento(ev["id"]))
        return eventos

    def obtener_evento(self, evento_id: str) -> Optional[Dict[str, Any]]:
        ev = _serialize(Evento.get_by_id(evento_id))
        if ev is None:
            return None
        ev["tipos"] = _serialize_list(EventoTipo.get_by_evento(evento_id))
        return ev

    @transaction.atomic
    def crear_evento(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        tipos = payload.pop("tipos", [])
        evento_id = Evento.create(
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
            EventoTipo.create(evento_id, tipo)
        return self.obtener_evento(evento_id)

    @transaction.atomic
    def actualizar_evento(
        self, evento_id: str, payload: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        tipos = payload.pop("tipos", None)
        Evento.update(evento_id, payload)
        if tipos is not None:
            EventoTipo.delete_by_evento(evento_id)
            for tipo in tipos:
                EventoTipo.create(evento_id, tipo)
        return self.obtener_evento(evento_id)

    def actualizar_estado(
        self, evento_id: str, estado: str
    ) -> Optional[Dict[str, Any]]:
        estados_validos = {"PLANIFICADO", "EN_EJECUCION", "FINALIZADO", "CANCELADO"}
        if estado not in estados_validos:
            raise ValueError(f"Estado inválido. Opciones: {estados_validos}")
        Evento.update_estado(evento_id, estado)
        return self.obtener_evento(evento_id)

    def eliminar_evento(self, evento_id: str) -> bool:
        return Evento.delete(evento_id)

    def agregar_tipo(self, evento_id: str, tipo: str) -> Dict[str, Any]:
        tipo_id = EventoTipo.create(evento_id, tipo)
        return {"id": tipo_id, "evento_id": evento_id, "tipo": tipo}

    def eliminar_tipo(self, tipo_id: str) -> bool:
        return EventoTipo.delete(tipo_id)


# =============================================================================
# ASIGNACIÓN  (RF-EV-07 al RF-EV-14, RF-EV-23)
# =============================================================================

class AsignacionService(IAsignacionService):

    def listar_asignaciones(self, evento_id: str) -> List[Dict[str, Any]]:
        return _serialize_list(Asignacion.get_by_evento(evento_id))

    @transaction.atomic
    def asignar_manual(
        self,
        evento_id: str,
        simpatizante_id: str,
        rol: Optional[str],
    ) -> Dict[str, Any]:
        if Asignacion.existe(evento_id, simpatizante_id):
            raise ValueError("El simpatizante ya está asignado a este evento.")
        asignacion_id = Asignacion.create(evento_id, simpatizante_id, rol, "MANUAL")
        simpatizante = Simpatizante.get_by_id(simpatizante_id)
        if simpatizante:
            Cobertura.incrementar_asignados(evento_id, simpatizante["ocupacion"])
        return _serialize(Asignacion.get_by_id(asignacion_id))

    @transaction.atomic
    def asignar_automatico(
        self,
        evento_id: str,
        criterios: Dict[str, bool],
    ) -> List[Dict[str, Any]]:
        """
        RF-EV-08 — Asignación automática respetando los criterios configurables.
        Criterios soportados:
          - usar_horario (bool): filtra por compatibilidad de horario
          - usar_ocupacion (bool): prioriza la ocupación requerida por cobertura
          - usar_participacion_previa (bool): excluye quienes ya participaron en el sector
        """
        evento = Evento.get_by_id(evento_id)
        if not evento:
            raise ValueError("Evento no encontrado.")

        # Candidatos base: todos los simpatizantes del barrio del evento
        if evento["barrio_id"]:
            candidatos = Simpatizante.get_by_barrio(evento["barrio_id"])
        else:
            candidatos = Simpatizante.get_all()

        # Filtro por horario (RF-EV-22)
        if criterios.get("usar_horario", True):
            import datetime
            fecha_dt = evento["fecha"]
            if isinstance(fecha_dt, str):
                fecha_dt = datetime.date.fromisoformat(fecha_dt)
            dia_semana = fecha_dt.strftime("%A").upper()
            disponibles_ids = {
                str(d["id"])
                for d in HorarioDisponible.get_disponibles_para_evento(
                    str(fecha_dt),
                    dia_semana,
                    str(evento["hora_inicio"]),
                    str(evento["hora_fin"]),
                )
            }
            candidatos = [c for c in candidatos if str(c["id"]) in disponibles_ids]

        # Filtro por participación previa en el sector (RF-EV-23)
        if criterios.get("usar_participacion_previa", True):
            sin_conflicto = []
            for c in candidatos:
                sectores_recientes = Asignacion.get_sectores_recientes_simpatizante(
                    str(c["id"])
                )
                if not sectores_recientes:
                    sin_conflicto.append(c)
                else:
                    logger.info(
                        "[AsignacionService] Simpatizante %s omitido por participación territorial reciente.",
                        c["id"],
                    )
            candidatos = sin_conflicto

        # Excluir ya asignados
        ya_asignados = {
            str(a["simpatizante_id"])
            for a in Asignacion.get_by_evento(evento_id)
        }
        candidatos = [c for c in candidatos if str(c["id"]) not in ya_asignados]

        # Ordenar por ocupación si se usa cobertura
        if criterios.get("usar_ocupacion", True):
            coberturas = {c["ocupacion"]: c["requeridos"] for c in Cobertura.get_by_evento(evento_id)}
            candidatos.sort(
                key=lambda c: coberturas.get(c["ocupacion"], 0),
                reverse=True,
            )

        # Asignar hasta completar capacidad del evento
        capacidad = evento.get("capacidad", 0)
        asignados = []
        for candidato in candidatos:
            if capacidad and len(asignados) >= capacidad:
                break
            asignacion_id = Asignacion.create(
                evento_id, str(candidato["id"]), None, "AUTOMATICO"
            )
            Cobertura.incrementar_asignados(evento_id, candidato["ocupacion"])
            asignados.append(_serialize(Asignacion.get_by_id(asignacion_id)))

        return asignados

    def actualizar_rol(
        self, asignacion_id: str, rol: str
    ) -> Optional[Dict[str, Any]]:
        Asignacion.update_rol(asignacion_id, rol)
        return _serialize(Asignacion.get_by_id(asignacion_id))

    def remover_asignacion(self, asignacion_id: str) -> bool:
        return Asignacion.delete(asignacion_id)

    def registrar_asistencia(
        self, asignacion_id: str, asistio: bool
    ) -> Optional[Dict[str, Any]]:
        Asignacion.registrar_asistencia(asignacion_id, asistio)
        return _serialize(Asignacion.get_by_id(asignacion_id))

    def verificar_participacion_territorial(
        self, simpatizante_id: str, evento_id: str
    ) -> Dict[str, Any]:
        """RF-EV-23 — Advierte si hay participación reciente en el mismo sector."""
        evento = Evento.get_by_id(evento_id)
        if not evento:
            return {"advertencia": False, "sectores": []}
        sectores_recientes = Asignacion.get_sectores_recientes_simpatizante(simpatizante_id)
        advertencia = len(sectores_recientes) > 0
        return {
            "advertencia": advertencia,
            "sectores": sectores_recientes,
            "mensaje": (
                "Esta persona participó recientemente en actividades del mismo sector."
                if advertencia
                else "Sin participación territorial reciente."
            ),
        }


# =============================================================================
# COBERTURA  (RF-EV-11)
# =============================================================================

class CoberturaService(ICoberturaService):

    def listar_cobertura(self, evento_id: str) -> List[Dict[str, Any]]:
        return _serialize_list(Cobertura.get_by_evento(evento_id))

    def registrar_cobertura(
        self, evento_id: str, ocupacion: str, requeridos: int
    ) -> Dict[str, Any]:
        cobertura_id = Cobertura.create(evento_id, ocupacion, requeridos)
        rows = _serialize_list(Cobertura.get_by_evento(evento_id))
        return next(r for r in rows if r["id"] == cobertura_id)

    def actualizar_cobertura(
        self,
        cobertura_id: str,
        ocupacion: str,
        requeridos: int,
        asignados: int,
    ) -> Optional[Dict[str, Any]]:
        Cobertura.update(cobertura_id, ocupacion, requeridos, asignados)
        # Reconstruimos el objeto desde la BD
        from django.db import connection
        import db
        from Backend.moduloEventos.models import _fetchone
        with connection.cursor() as cur:
            cur.execute(
                f"SELECT id, evento_id, ocupacion, requeridos, asignados FROM {db.cobertura} WHERE id = %s",
                [cobertura_id],
            )
            return _serialize(_fetchone(cur))

    def eliminar_cobertura(self, cobertura_id: str) -> bool:
        return Cobertura.delete(cobertura_id)


# =============================================================================
# OBSERVACIÓN  (RF-EV-12, RF-EV-13)
# =============================================================================

class ObservacionService(IObservacionService):

    MOMENTOS_VALIDOS = {"INICIAL", "FINAL"}

    def listar_observaciones(self, evento_id: str) -> List[Dict[str, Any]]:
        return _serialize_list(Observacion.get_by_evento(evento_id))

    def registrar_observacion(
        self, evento_id: str, momento: str, contenido: str
    ) -> Dict[str, Any]:
        if momento not in self.MOMENTOS_VALIDOS:
            raise ValueError(f"momento debe ser uno de: {self.MOMENTOS_VALIDOS}")
        obs_id = Observacion.create(evento_id, momento, contenido)
        rows = _serialize_list(Observacion.get_by_evento(evento_id))
        return next(r for r in rows if r["id"] == obs_id)

    def eliminar_observacion(self, observacion_id: str) -> bool:
        return Observacion.delete(observacion_id)


# =============================================================================
# PARTICIPACIÓN EXTERNA  (RF-EV-18)
# =============================================================================

class ParticipacionExternaService(IParticipacionExternaService):

    def obtener_participacion(self, evento_id: str) -> Optional[Dict[str, Any]]:
        return _serialize(ParticipacionExterna.get_by_evento(evento_id))

    def registrar_participacion(
        self, evento_id: str, cantidad: int, notas: Optional[str]
    ) -> Dict[str, Any]:
        existente = ParticipacionExterna.get_by_evento(evento_id)
        if existente:
            ParticipacionExterna.update(str(existente["id"]), cantidad, notas)
            return _serialize(ParticipacionExterna.get_by_evento(evento_id))
        ParticipacionExterna.create(evento_id, cantidad, notas)
        return _serialize(ParticipacionExterna.get_by_evento(evento_id))

    def actualizar_participacion(
        self,
        participacion_id: str,
        cantidad: int,
        notas: Optional[str],
    ) -> Optional[Dict[str, Any]]:
        ParticipacionExterna.update(participacion_id, cantidad, notas)
        from django.db import connection
        import db
        from Backend.moduloEventos.models import _fetchone
        with connection.cursor() as cur:
            cur.execute(
                f"SELECT id, evento_id, cantidad, notas FROM {db.participacion_externa} WHERE id = %s",
                [participacion_id],
            )
            return _serialize(_fetchone(cur))


# =============================================================================
# MATERIAL PUBLICITARIO  (RF-EV-19)
# =============================================================================

class MaterialPublicitarioService(IMaterialPublicitarioService):

    def obtener_material(self, evento_id: str) -> Optional[Dict[str, Any]]:
        return _serialize(MaterialPublicitario.get_by_evento(evento_id))

    def registrar_material(
        self, evento_id: str, entregado: int, restante: int
    ) -> Dict[str, Any]:
        existente = MaterialPublicitario.get_by_evento(evento_id)
        if existente:
            MaterialPublicitario.update(str(existente["id"]), entregado, restante)
            return _serialize(MaterialPublicitario.get_by_evento(evento_id))
        MaterialPublicitario.create(evento_id, entregado, restante)
        return _serialize(MaterialPublicitario.get_by_evento(evento_id))

    def actualizar_material(
        self, material_id: str, entregado: int, restante: int
    ) -> Optional[Dict[str, Any]]:
        MaterialPublicitario.update(material_id, entregado, restante)
        from django.db import connection
        import db
        from Backend.moduloEventos.models import _fetchone
        with connection.cursor() as cur:
            cur.execute(
                f"SELECT id, evento_id, entregado, restante FROM {db.material_publicitario} WHERE id = %s",
                [material_id],
            )
            return _serialize(_fetchone(cur))


# =============================================================================
# ESTADO MATERIAL  (RF-EV-20, RF-EV-21, RF-EV-22)
# =============================================================================

class EstadoMaterialService(IEstadoMaterialService):

    ESTADOS_VALIDOS = {"CONSERVADO", "DETERIORADO", "RETIRADO", "VANDALIZADO"}

    def listar_estados(self, evento_id: str) -> List[Dict[str, Any]]:
        return _serialize_list(EstadoMaterial.get_by_evento(evento_id))

    def registrar_estado(
        self, evento_id: str, estado: str, notas: Optional[str]
    ) -> Dict[str, Any]:
        estado_upper = estado.upper()
        if estado_upper not in self.ESTADOS_VALIDOS:
            raise ValueError(f"Estado inválido. Opciones: {self.ESTADOS_VALIDOS}")
        estado_id = EstadoMaterial.create(evento_id, estado_upper, notas)
        rows = _serialize_list(EstadoMaterial.get_by_evento(evento_id))
        return next(r for r in rows if r["id"] == estado_id)

    @transaction.atomic
    def cargar_desde_csv(self, archivo_csv: Any) -> Dict[str, Any]:
        """
        RF-EV-21 — Procesa un archivo CSV con columnas:
        numero_evento (evento_id UUID), estado (1-5), notas.
        """
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
            except Exception as exc:
                errores.append(f"Fila {i}: {exc}")

        insertados = EstadoMaterial.bulk_create_from_csv(filas_ok)
        return {
            "insertados": insertados,
            "errores": errores,
            "total_procesadas": len(filas_ok) + len(errores),
        }

    def calcular_promedio_estado(self, evento_id: str) -> Optional[float]:
        return EstadoMaterial.promedio_estado_numerico(evento_id)


# =============================================================================
# AUDITORÍA
# =============================================================================

class AuditoriaService(IAuditoriaService):

    def historial_registro(
        self, tabla: str, registro_id: str
    ) -> List[Dict[str, Any]]:
        return _serialize_list(Auditoria.get_by_tabla_registro(tabla, registro_id))

    def registros_recientes(self, limit: int = 50) -> List[Dict[str, Any]]:
        return _serialize_list(Auditoria.get_recientes(limit))