import json
import logging
from typing import Callable

from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from Backend.moduloEventos.services import (
    BarrioService,
    PuntoInteresService,
    CoordinadorService,
    SimpatizanteService,
    HorarioDisponibleService,
    EventoService,
    EventoPuntoInteresService,
    AsignacionService,
    CoberturaService,
    ObservacionService,
    ParticipacionExternaService,
    MaterialPublicitarioService,
    EstadoMaterialService,
    AuditoriaService,
)

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Instancias de servicios (singleton ligero — sin estado mutable)
# ─────────────────────────────────────────────────────────────────────────────
_barrio_svc             = BarrioService()
_punto_svc              = PuntoInteresService()
_coordinador_svc        = CoordinadorService()
_simpatizante_svc       = SimpatizanteService()
_horario_svc            = HorarioDisponibleService()
_evento_svc             = EventoService()
_evento_punto_svc       = EventoPuntoInteresService()
_asignacion_svc         = AsignacionService()
_cobertura_svc          = CoberturaService()
_observacion_svc        = ObservacionService()
_participacion_svc      = ParticipacionExternaService()
_material_svc           = MaterialPublicitarioService()
_estado_material_svc    = EstadoMaterialService()
_auditoria_svc          = AuditoriaService()


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _ok(data=None, status: int = 200) -> JsonResponse:
    return JsonResponse({"ok": True, "data": data}, status=status)


def _err(mensaje: str, status: int = 400) -> JsonResponse:
    return JsonResponse({"ok": False, "error": mensaje}, status=status)


def _body(request) -> dict:
    try:
        return json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return {}


def _handle(func: Callable) -> JsonResponse:
    """Envuelve la lógica de cada handler para capturar excepciones comunes."""
    try:
        return func()
    except ValueError as exc:
        return _err(str(exc), 400)
    except Exception as exc:
        logger.exception("[moduloEventos] Error inesperado: %s", exc)
        return _err("Error interno del servidor.", 500)


# ─────────────────────────────────────────────────────────────────────────────
# Decorador CSRF exento para todas las vistas (API interna)
# ─────────────────────────────────────────────────────────────────────────────
csrf_exempt_cbv = method_decorator(csrf_exempt, name="dispatch")


# =============================================================================
# BARRIO
# =============================================================================

@csrf_exempt_cbv
class BarrioListView(View):
    """GET /eventos/barrios/  — POST /eventos/barrios/"""

    def get(self, request):
        return _handle(lambda: _ok(_barrio_svc.listar_barrios()))

    def post(self, request):
        data = _body(request)
        return _handle(lambda: _ok(_barrio_svc.crear_barrio(data["nombre"]), 201))


@csrf_exempt_cbv
class BarrioDetailView(View):
    """GET|PUT|DELETE /eventos/barrios/<barrio_id>/"""

    def get(self, request, barrio_id):
        def _():
            obj = _barrio_svc.obtener_barrio(barrio_id)
            return _ok(obj) if obj else _err("Barrio no encontrado.", 404)
        return _handle(_)

    def put(self, request, barrio_id):
        data = _body(request)
        return _handle(lambda: _ok(_barrio_svc.actualizar_barrio(barrio_id, data["nombre"])))

    def delete(self, request, barrio_id):
        return _handle(lambda: _ok({"eliminado": _barrio_svc.eliminar_barrio(barrio_id)}))


# =============================================================================
# PUNTO DE INTERÉS
# — sector eliminado: punto_interes ahora referencia barrio_id directamente
# =============================================================================

@csrf_exempt_cbv
class PuntoInteresListView(View):
    """GET /eventos/puntos/?barrio_id=  — POST /eventos/puntos/"""

    def get(self, request):
        barrio_id = request.GET.get("barrio_id", "")
        return _handle(lambda: _ok(_punto_svc.listar_puntos(barrio_id)))

    def post(self, request):
        data = _body(request)
        return _handle(lambda: _ok(_punto_svc.crear_punto(data["nombre"], data["barrio_id"]), 201))


@csrf_exempt_cbv
class PuntoInteresDetailView(View):
    """GET|PUT|DELETE /eventos/puntos/<punto_id>/"""

    def get(self, request, punto_id):
        def _():
            obj = _punto_svc.obtener_punto(punto_id)
            return _ok(obj) if obj else _err("Punto de interés no encontrado.", 404)
        return _handle(_)

    def put(self, request, punto_id):
        data = _body(request)
        return _handle(lambda: _ok(_punto_svc.actualizar_punto(punto_id, data["nombre"], data["barrio_id"])))

    def delete(self, request, punto_id):
        return _handle(lambda: _ok({"eliminado": _punto_svc.eliminar_punto(punto_id)}))


# =============================================================================
# COORDINADOR
# =============================================================================

@csrf_exempt_cbv
class CoordinadorListView(View):
    """GET /eventos/coordinadores/  — POST /eventos/coordinadores/"""

    def get(self, request):
        return _handle(lambda: _ok(_coordinador_svc.listar_coordinadores()))

    def post(self, request):
        data = _body(request)
        return _handle(lambda: _ok(
            _coordinador_svc.crear_coordinador(
                data["nombre"], data["email"], data["password"]
            ), 201
        ))


@csrf_exempt_cbv
class CoordinadorDetailView(View):
    """GET|PUT|DELETE /eventos/coordinadores/<coordinador_id>/"""

    def get(self, request, coordinador_id):
        def _():
            obj = _coordinador_svc.obtener_coordinador(coordinador_id)
            return _ok(obj) if obj else _err("Coordinador no encontrado.", 404)
        return _handle(_)

    def put(self, request, coordinador_id):
        data = _body(request)
        return _handle(lambda: _ok(
            _coordinador_svc.actualizar_coordinador(coordinador_id, data["nombre"], data["email"])
        ))

    def delete(self, request, coordinador_id):
        return _err("Los coordinadores no se pueden eliminar.", 405)


@csrf_exempt_cbv
class CoordinadorPasswordView(View):
    """POST /eventos/coordinadores/<coordinador_id>/password/"""

    def post(self, request, coordinador_id):
        data = _body(request)
        return _handle(lambda: _ok(
            {"actualizado": _coordinador_svc.cambiar_password(coordinador_id, data["password"])}
        ))


# =============================================================================
# SIMPATIZANTE
# =============================================================================

@csrf_exempt_cbv
class SimpatizanteListView(View):
    """GET /eventos/simpatizantes/?barrio_id=  — POST /eventos/simpatizantes/"""

    def get(self, request):
        barrio_id = request.GET.get("barrio_id")
        return _handle(lambda: _ok(_simpatizante_svc.listar_simpatizantes(barrio_id)))

    def post(self, request):
        data = _body(request)
        return _handle(lambda: _ok(_simpatizante_svc.crear_simpatizante(data), 201))


@csrf_exempt_cbv
class SimpatizanteDetailView(View):
    """GET|PUT|DELETE /eventos/simpatizantes/<simpatizante_id>/"""

    def get(self, request, simpatizante_id):
        def _():
            obj = _simpatizante_svc.obtener_simpatizante(simpatizante_id)
            return _ok(obj) if obj else _err("Simpatizante no encontrado.", 404)
        return _handle(_)

    def put(self, request, simpatizante_id):
        data = _body(request)
        return _handle(lambda: _ok(_simpatizante_svc.actualizar_simpatizante(simpatizante_id, data)))

    def delete(self, request, simpatizante_id):
        return _handle(lambda: _ok({"eliminado": _simpatizante_svc.eliminar_simpatizante(simpatizante_id)}))


# =============================================================================
# HORARIO DISPONIBLE
# =============================================================================

@csrf_exempt_cbv
class HorarioListView(View):
    """
    GET  /eventos/simpatizantes/<simpatizante_id>/horarios/
    POST /eventos/simpatizantes/<simpatizante_id>/horarios/
    """

    def get(self, request, simpatizante_id):
        return _handle(lambda: _ok(_horario_svc.listar_horarios(simpatizante_id)))

    def post(self, request, simpatizante_id):
        data = _body(request)
        return _handle(lambda: _ok(
            _horario_svc.crear_horario(
                simpatizante_id,
                data["dia_semana"],
                data["hora_inicio"],
                data["hora_fin"],
            ), 201
        ))


@csrf_exempt_cbv
class HorarioDetailView(View):
    """DELETE /eventos/horarios/<horario_id>/"""

    def delete(self, request, horario_id):
        return _handle(lambda: _ok({"eliminado": _horario_svc.eliminar_horario(horario_id)}))


@csrf_exempt_cbv
class DisponiblesParaEventoView(View):
    """
    GET /eventos/<evento_id>/disponibles/
    RF-EV-06 — Consulta de disponibilidad para un evento.
    """

    def get(self, request, evento_id):
        def _():
            ev = _evento_svc.obtener_evento(evento_id)
            if not ev:
                return _err("Evento no encontrado.", 404)
            import datetime
            fecha = ev["fecha"]
            if isinstance(fecha, str):
                fecha_dt = datetime.date.fromisoformat(fecha)
            else:
                fecha_dt = fecha
            dia_semana = fecha_dt.strftime("%A").upper()
            disponibles = _horario_svc.consultar_disponibles_para_evento(
                str(fecha_dt), dia_semana, str(ev["hora_inicio"]), str(ev["hora_fin"])
            )
            return _ok(disponibles)
        return _handle(_)


# =============================================================================
# EVENTO  (RF-EV-01 al RF-EV-05)
# =============================================================================

@csrf_exempt_cbv
class EventoListView(View):
    """GET /eventos/  — POST /eventos/"""

    def get(self, request):
        return _handle(lambda: _ok(_evento_svc.listar_eventos()))

    def post(self, request):
        data = _body(request)
        return _handle(lambda: _ok(_evento_svc.crear_evento(data), 201))


@csrf_exempt_cbv
class EventoDetailView(View):
    """GET|PUT|DELETE /eventos/<evento_id>/"""

    def get(self, request, evento_id):
        def _():
            obj = _evento_svc.obtener_evento(evento_id)
            return _ok(obj) if obj else _err("Evento no encontrado.", 404)
        return _handle(_)

    def put(self, request, evento_id):
        data = _body(request)
        return _handle(lambda: _ok(_evento_svc.actualizar_evento(evento_id, data)))

    def delete(self, request, evento_id):
        return _handle(lambda: _ok({"eliminado": _evento_svc.eliminar_evento(evento_id)}))


@csrf_exempt_cbv
class EventoEstadoView(View):
    """PATCH /eventos/<evento_id>/estado/  — RF-EV-04"""

    def patch(self, request, evento_id):
        data = _body(request)
        return _handle(lambda: _ok(_evento_svc.actualizar_estado(evento_id, data["estado"])))


@csrf_exempt_cbv
class EventoTipoListView(View):
    """
    GET  /eventos/<evento_id>/tipos/
    POST /eventos/<evento_id>/tipos/
    RF-EV-05
    """

    def get(self, request, evento_id):
        def _():
            ev = _evento_svc.obtener_evento(evento_id)
            return _ok(ev["tipos"] if ev else [])
        return _handle(_)

    def post(self, request, evento_id):
        data = _body(request)
        return _handle(lambda: _ok(_evento_svc.agregar_tipo(evento_id, data["tipo"]), 201))


@csrf_exempt_cbv
class EventoTipoDetailView(View):
    """DELETE /eventos/tipos/<tipo_id>/  — RF-EV-05"""

    def delete(self, request, tipo_id):
        return _handle(lambda: _ok({"eliminado": _evento_svc.eliminar_tipo(tipo_id)}))


# =============================================================================
# EVENTO PUNTO DE INTERÉS
# =============================================================================

@csrf_exempt_cbv
class EventoPuntoInteresListView(View):
    """
    GET /eventos/<evento_id>/puntos/  — lista puntos del evento
    POST /eventos/<evento_id>/puntos/ — agrega un punto al evento
    PUT  /eventos/<evento_id>/puntos/ — reemplaza todos los puntos del evento
    """

    def get(self, request, evento_id):
        return _handle(lambda: _ok(_evento_punto_svc.listar_puntos_evento(evento_id)))

    def post(self, request, evento_id):
        data = _body(request)
        return _handle(lambda: _ok(
            _evento_punto_svc.agregar_punto(evento_id, data["punto_interes_id"]), 201
        ))

    def put(self, request, evento_id):
        data = _body(request)
        return _handle(lambda: _ok(
            _evento_punto_svc.reemplazar_puntos(evento_id, data["punto_interes_ids"])
        ))


@csrf_exempt_cbv
class EventoPuntoInteresDetailView(View):
    """DELETE /eventos/puntos-evento/<relacion_id>/  — remueve un punto del evento"""

    def delete(self, request, relacion_id):
        return _handle(lambda: _ok({"eliminado": _evento_punto_svc.remover_punto(relacion_id)}))


# =============================================================================
# ASIGNACIÓN  (RF-EV-07 al RF-EV-10, RF-EV-14, RF-EV-23)
# =============================================================================

@csrf_exempt_cbv
class AsignacionListView(View):
    """
    GET  /eventos/<evento_id>/asignaciones/
    POST /eventos/<evento_id>/asignaciones/       — asignación manual (RF-EV-07)
    """

    def get(self, request, evento_id):
        return _handle(lambda: _ok(_asignacion_svc.listar_asignaciones(evento_id)))

    def post(self, request, evento_id):
        data = _body(request)
        return _handle(lambda: _ok(
            _asignacion_svc.asignar_manual(
                evento_id,
                data["simpatizante_id"],
                data.get("rol"),
            ), 201
        ))


@csrf_exempt_cbv
class AsignacionAutomaticaView(View):
    """POST /eventos/<evento_id>/asignaciones/automatica/  — RF-EV-08"""

    def post(self, request, evento_id):
        data = _body(request)
        criterios = data.get("criterios", {})
        return _handle(lambda: _ok(_asignacion_svc.asignar_automatico(evento_id, criterios), 201))


@csrf_exempt_cbv
class AsignacionDetailView(View):
    """PUT|DELETE /eventos/asignaciones/<asignacion_id>/  — RF-EV-09"""

    def put(self, request, asignacion_id):
        data = _body(request)
        return _handle(lambda: _ok(_asignacion_svc.actualizar_rol(asignacion_id, data["rol"])))

    def delete(self, request, asignacion_id):
        return _handle(lambda: _ok({"eliminado": _asignacion_svc.remover_asignacion(asignacion_id)}))


@csrf_exempt_cbv
class AsistenciaView(View):
    """PATCH /eventos/asignaciones/<asignacion_id>/asistencia/  — RF-EV-14"""

    def patch(self, request, asignacion_id):
        data = _body(request)
        return _handle(lambda: _ok(
            _asignacion_svc.registrar_asistencia(asignacion_id, bool(data.get("asistio", False)))
        ))


@csrf_exempt_cbv
class ParticipacionTerritorialView(View):
    """
    GET /eventos/<evento_id>/participacion-territorial/<simpatizante_id>/
    RF-EV-23 — Verifica participación territorial reciente.
    """

    def get(self, request, evento_id, simpatizante_id):
        return _handle(lambda: _ok(
            _asignacion_svc.verificar_participacion_territorial(simpatizante_id, evento_id)
        ))


# =============================================================================
# COBERTURA  (RF-EV-11)
# =============================================================================

@csrf_exempt_cbv
class CoberturaListView(View):
    """GET|POST /eventos/<evento_id>/cobertura/"""

    def get(self, request, evento_id):
        return _handle(lambda: _ok(_cobertura_svc.listar_cobertura(evento_id)))

    def post(self, request, evento_id):
        data = _body(request)
        return _handle(lambda: _ok(
            _cobertura_svc.registrar_cobertura(evento_id, data["ocupacion"], int(data["requeridos"])), 201
        ))


@csrf_exempt_cbv
class CoberturaDetailView(View):
    """PUT|DELETE /eventos/cobertura/<cobertura_id>/"""

    def put(self, request, cobertura_id):
        data = _body(request)
        return _handle(lambda: _ok(
            _cobertura_svc.actualizar_cobertura(
                cobertura_id,
                data["ocupacion"],
                int(data["requeridos"]),
                int(data.get("asignados", 0)),
            )
        ))

    def delete(self, request, cobertura_id):
        return _handle(lambda: _ok({"eliminado": _cobertura_svc.eliminar_cobertura(cobertura_id)}))


# =============================================================================
# OBSERVACIÓN  (RF-EV-12, RF-EV-13)
# =============================================================================

@csrf_exempt_cbv
class ObservacionListView(View):
    """GET|POST /eventos/<evento_id>/observaciones/"""

    def get(self, request, evento_id):
        return _handle(lambda: _ok(_observacion_svc.listar_observaciones(evento_id)))

    def post(self, request, evento_id):
        data = _body(request)
        return _handle(lambda: _ok(
            _observacion_svc.registrar_observacion(evento_id, data["momento"], data["contenido"]), 201
        ))


@csrf_exempt_cbv
class ObservacionDetailView(View):
    """DELETE /eventos/observaciones/<observacion_id>/"""

    def delete(self, request, observacion_id):
        return _handle(lambda: _ok({"eliminado": _observacion_svc.eliminar_observacion(observacion_id)}))


# =============================================================================
# PARTICIPACIÓN EXTERNA  (RF-EV-18)
# =============================================================================

@csrf_exempt_cbv
class ParticipacionExternaView(View):
    """GET|POST|PUT /eventos/<evento_id>/participacion-externa/"""

    def get(self, request, evento_id):
        return _handle(lambda: _ok(_participacion_svc.obtener_participacion(evento_id)))

    def post(self, request, evento_id):
        data = _body(request)
        return _handle(lambda: _ok(
            _participacion_svc.registrar_participacion(evento_id, int(data["cantidad"]), data.get("notas")), 201
        ))

    def put(self, request, evento_id):
        data = _body(request)
        return _handle(lambda: _ok(
            _participacion_svc.actualizar_participacion(data["id"], int(data["cantidad"]), data.get("notas"))
        ))


# =============================================================================
# MATERIAL PUBLICITARIO  (RF-EV-19)
# =============================================================================

@csrf_exempt_cbv
class MaterialPublicitarioView(View):
    """GET|POST|PUT /eventos/<evento_id>/material/"""

    def get(self, request, evento_id):
        return _handle(lambda: _ok(_material_svc.obtener_material(evento_id)))

    def post(self, request, evento_id):
        data = _body(request)
        return _handle(lambda: _ok(
            _material_svc.registrar_material(evento_id, int(data["entregado"]), int(data["restante"])), 201
        ))

    def put(self, request, evento_id):
        data = _body(request)
        return _handle(lambda: _ok(
            _material_svc.actualizar_material(data["id"], int(data["entregado"]), int(data["restante"]))
        ))


# =============================================================================
# ESTADO MATERIAL  (RF-EV-20, RF-EV-21, RF-EV-22)
# =============================================================================

@csrf_exempt_cbv
class EstadoMaterialListView(View):
    """GET|POST /eventos/<evento_id>/material/estado/"""

    def get(self, request, evento_id):
        return _handle(lambda: _ok(_estado_material_svc.listar_estados(evento_id)))

    def post(self, request, evento_id):
        data = _body(request)
        return _handle(lambda: _ok(
            _estado_material_svc.registrar_estado(evento_id, data["estado"], data.get("notas")), 201
        ))


@csrf_exempt_cbv
class EstadoMaterialCSVView(View):
    """POST /eventos/material/estado/csv/  — RF-EV-21"""

    def post(self, request):
        archivo = request.FILES.get("archivo")
        if not archivo:
            return _err("Se requiere un archivo CSV.", 400)
        return _handle(lambda: _ok(_estado_material_svc.cargar_desde_csv(archivo)))


@csrf_exempt_cbv
class PromedioEstadoMaterialView(View):
    """GET /eventos/<evento_id>/material/estado/promedio/  — RF-EV-22"""

    def get(self, request, evento_id):
        return _handle(lambda: _ok({
            "evento_id": evento_id,
            "promedio": _estado_material_svc.calcular_promedio_estado(evento_id),
        }))


# =============================================================================
# AUDITORÍA
# =============================================================================

@csrf_exempt_cbv
class AuditoriaView(View):
    """GET /eventos/auditoria/?tabla=&registro_id=  — GET /eventos/auditoria/recientes/"""

    def get(self, request):
        tabla       = request.GET.get("tabla")
        registro_id = request.GET.get("registro_id")
        if tabla and registro_id:
            return _handle(lambda: _ok(_auditoria_svc.historial_registro(tabla, registro_id)))
        limit = int(request.GET.get("limit", 50))
        return _handle(lambda: _ok(_auditoria_svc.registros_recientes(limit)))