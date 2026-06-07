import json
import logging
from typing import Callable

from django.http import JsonResponse
from django.shortcuts import render # Importación necesaria
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from Backend.moduloLogin.views import login_requerido, SESSION_KEY

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
# Vista para cargar el Frontend (Nueva)
# ─────────────────────────────────────────────────────────────────────────────
@login_requerido
def evento_crear_vista(request):
    """Carga el formulario de creación de evento."""
    return render(request, 'moduloEventos/eventos_form.html')

@login_requerido
def evento_detalle_vista(request, evento_id):
    """Carga la vista de detalle de un evento."""
    return render(request, 'moduloEventos/eventos_detalle.html', {'evento_id': evento_id})

@login_requerido
def evento_editar_vista(request, evento_id):
    """Carga el formulario de edición de un evento."""
    return render(request, 'moduloEventos/eventos_form.html', {'evento_id': evento_id})

@login_requerido
def eventos_vista(request):
    """Carga la interfaz del frontend de eventos."""
    return render(request, 'moduloEventos/eventos_lista.html')

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

def evento_crear_vista(request):
    """Carga el formulario de creación de evento."""
    return render(request, 'moduloEventos/eventos_form.html')

def evento_detalle_vista(request, evento_id):
    """Carga la vista de detalle de un evento."""
    return render(request, 'moduloEventos/eventos_detalle.html', {'evento_id': evento_id})

async def _handle(func: Callable) -> JsonResponse:
    """Envuelve la lógica de cada handler para capturar excepciones comunes."""
    try:
        return await func()
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

    async def get(self, request):
        logger.debug("[BarrioListView] GET listar_barrios")
        async def _():
            return _ok(await _barrio_svc.listar_barrios())
        return await _handle(_)

    async def post(self, request):
        data = _body(request)
        logger.debug("[BarrioListView] POST crear_barrio nombre=%s", data.get("nombre"))
        async def _():
            return _ok(await _barrio_svc.crear_barrio(data["nombre"]), 201)
        return await _handle(_)


@csrf_exempt_cbv
class BarrioDetailView(View):
    """GET|PUT|DELETE /eventos/barrios/<barrio_id>/"""

    async def get(self, request, barrio_id):
        logger.debug("[BarrioDetailView] GET obtener_barrio barrio_id=%s", barrio_id)
        async def _():
            obj = await _barrio_svc.obtener_barrio(barrio_id)
            return _ok(obj) if obj else _err("Barrio no encontrado.", 404)
        return await _handle(_)

    async def put(self, request, barrio_id):
        data = _body(request)
        logger.debug("[BarrioDetailView] PUT actualizar_barrio barrio_id=%s", barrio_id)
        async def _():
            return _ok(await _barrio_svc.actualizar_barrio(barrio_id, data["nombre"]))
        return await _handle(_)

    async def delete(self, request, barrio_id):
        logger.debug("[BarrioDetailView] DELETE eliminar_barrio barrio_id=%s", barrio_id)
        async def _():
            return _ok({"eliminado": await _barrio_svc.eliminar_barrio(barrio_id)})
        return await _handle(_)


# =============================================================================
# PUNTO DE INTERÉS
# =============================================================================

@csrf_exempt_cbv
class PuntoInteresListView(View):
    """GET /eventos/puntos/?barrio_id=  — POST /eventos/puntos/"""

    async def get(self, request):
        barrio_id = request.GET.get("barrio_id", "")
        logger.debug("[PuntoInteresListView] GET listar_puntos barrio_id=%s", barrio_id)
        async def _():
            return _ok(await _punto_svc.listar_puntos(barrio_id))
        return await _handle(_)

    async def post(self, request):
        data = _body(request)
        logger.debug("[PuntoInteresListView] POST crear_punto nombre=%s barrio_id=%s", data.get("nombre"), data.get("barrio_id"))
        async def _():
            return _ok(await _punto_svc.crear_punto(data["nombre"], data["barrio_id"]), 201)
        return await _handle(_)


@csrf_exempt_cbv
class PuntoInteresDetailView(View):
    """GET|PUT|DELETE /eventos/puntos/<punto_id>/"""

    async def get(self, request, punto_id):
        logger.debug("[PuntoInteresDetailView] GET obtener_punto punto_id=%s", punto_id)
        async def _():
            obj = await _punto_svc.obtener_punto(punto_id)
            return _ok(obj) if obj else _err("Punto de interés no encontrado.", 404)
        return await _handle(_)

    async def put(self, request, punto_id):
        data = _body(request)
        logger.debug("[PuntoInteresDetailView] PUT actualizar_punto punto_id=%s", punto_id)
        async def _():
            return _ok(await _punto_svc.actualizar_punto(punto_id, data["nombre"], data["barrio_id"]))
        return await _handle(_)

    async def delete(self, request, punto_id):
        logger.debug("[PuntoInteresDetailView] DELETE eliminar_punto punto_id=%s", punto_id)
        async def _():
            return _ok({"eliminado": await _punto_svc.eliminar_punto(punto_id)})
        return await _handle(_)


# =============================================================================
# COORDINADOR
# =============================================================================

@csrf_exempt_cbv
class CoordinadorListView(View):
    """GET /eventos/coordinadores/  — POST /eventos/coordinadores/"""

    async def get(self, request):
        logger.debug("[CoordinadorListView] GET listar_coordinadores")
        async def _():
            return _ok(await _coordinador_svc.listar_coordinadores())
        return await _handle(_)

    async def post(self, request):
        data = _body(request)
        logger.debug("[CoordinadorListView] POST crear_coordinador nombre=%s email=%s", data.get("nombre"), data.get("email"))
        async def _():
            return _ok(
                await _coordinador_svc.crear_coordinador(
                    data["nombre"], data["email"], data["password"]
                ), 201
            )
        return await _handle(_)


@csrf_exempt_cbv
class CoordinadorDetailView(View):
    """GET|PUT|DELETE /eventos/coordinadores/<coordinador_id>/"""

    async def get(self, request, coordinador_id):
        logger.debug("[CoordinadorDetailView] GET obtener_coordinador coordinador_id=%s", coordinador_id)
        async def _():
            obj = await _coordinador_svc.obtener_coordinador(coordinador_id)
            return _ok(obj) if obj else _err("Coordinador no encontrado.", 404)
        return await _handle(_)

    async def put(self, request, coordinador_id):
        data = _body(request)
        logger.debug("[CoordinadorDetailView] PUT actualizar_coordinador coordinador_id=%s", coordinador_id)
        async def _():
            return _ok(
                await _coordinador_svc.actualizar_coordinador(coordinador_id, data["nombre"], data["email"])
            )
        return await _handle(_)

    async def delete(self, request, coordinador_id):
        logger.debug("[CoordinadorDetailView] DELETE coordinador_id=%s (no permitido)", coordinador_id)
        return _err("Los coordinadores no se pueden eliminar.", 405)


@csrf_exempt_cbv
class CoordinadorPasswordView(View):
    """POST /eventos/coordinadores/<coordinador_id>/password/"""

    async def post(self, request, coordinador_id):
        data = _body(request)
        logger.debug("[CoordinadorPasswordView] POST cambiar_password coordinador_id=%s", coordinador_id)
        async def _():
            return _ok(
                {"actualizado": await _coordinador_svc.cambiar_password(coordinador_id, data["password"])}
            )
        return await _handle(_)


# =============================================================================
# SIMPATIZANTE
# =============================================================================

@csrf_exempt_cbv
class SimpatizanteListView(View):
    """GET /eventos/simpatizantes/?barrio_id=  — POST /eventos/simpatizantes/"""

    async def get(self, request):
        barrio_id = request.GET.get("barrio_id")
        logger.debug("[SimpatizanteListView] GET listar_simpatizantes barrio_id=%s", barrio_id)
        async def _():
            return _ok(await _simpatizante_svc.listar_simpatizantes(barrio_id))
        return await _handle(_)

    async def post(self, request):
        data = _body(request)
        logger.debug("[SimpatizanteListView] POST crear_simpatizante cedula=%s", data.get("cedula"))
        async def _():
            return _ok(await _simpatizante_svc.crear_simpatizante(data), 201)
        return await _handle(_)


@csrf_exempt_cbv
class SimpatizanteDetailView(View):
    """GET|PUT|DELETE /eventos/simpatizantes/<simpatizante_id>/"""

    async def get(self, request, simpatizante_id):
        logger.debug("[SimpatizanteDetailView] GET obtener_simpatizante simpatizante_id=%s", simpatizante_id)
        async def _():
            obj = await _simpatizante_svc.obtener_simpatizante(simpatizante_id)
            return _ok(obj) if obj else _err("Simpatizante no encontrado.", 404)
        return await _handle(_)

    async def put(self, request, simpatizante_id):
        data = _body(request)
        logger.debug("[SimpatizanteDetailView] PUT actualizar_simpatizante simpatizante_id=%s", simpatizante_id)
        async def _():
            return _ok(await _simpatizante_svc.actualizar_simpatizante(simpatizante_id, data))
        return await _handle(_)

    async def delete(self, request, simpatizante_id):
        logger.debug("[SimpatizanteDetailView] DELETE eliminar_simpatizante simpatizante_id=%s", simpatizante_id)
        async def _():
            return _ok({"eliminado": await _simpatizante_svc.eliminar_simpatizante(simpatizante_id)})
        return await _handle(_)


# =============================================================================
# HORARIO DISPONIBLE
# =============================================================================

@csrf_exempt_cbv
class HorarioListView(View):
    """
    GET  /eventos/simpatizantes/<simpatizante_id>/horarios/
    POST /eventos/simpatizantes/<simpatizante_id>/horarios/
    """

    async def get(self, request, simpatizante_id):
        logger.debug("[HorarioListView] GET listar_horarios simpatizante_id=%s", simpatizante_id)
        async def _():
            return _ok(await _horario_svc.listar_horarios(simpatizante_id))
        return await _handle(_)

    async def post(self, request, simpatizante_id):
        data = _body(request)
        logger.debug("[HorarioListView] POST crear_horario simpatizante_id=%s dia=%s", simpatizante_id, data.get("dia_semana"))
        async def _():
            return _ok(
                await _horario_svc.crear_horario(
                    simpatizante_id,
                    data["dia_semana"],
                    data["hora_inicio"],
                    data["hora_fin"],
                ), 201
            )
        return await _handle(_)


@csrf_exempt_cbv
class HorarioDetailView(View):
    """DELETE /eventos/horarios/<horario_id>/"""

    async def delete(self, request, horario_id):
        logger.debug("[HorarioDetailView] DELETE eliminar_horario horario_id=%s", horario_id)
        async def _():
            return _ok({"eliminado": await _horario_svc.eliminar_horario(horario_id)})
        return await _handle(_)


@csrf_exempt_cbv
class DisponiblesParaEventoView(View):
    """
    GET /eventos/<evento_id>/disponibles/
    RF-EV-06 — Consulta de disponibilidad para un evento.
    """

    async def get(self, request, evento_id):
        logger.debug("[DisponiblesParaEventoView] GET evento_id=%s", evento_id)
        async def _():
            ev = await _evento_svc.obtener_evento(evento_id)
            if not ev:
                return _err("Evento no encontrado.", 404)
            import datetime
            fecha = ev["fecha"]
            if isinstance(fecha, str):
                fecha_dt = datetime.date.fromisoformat(fecha)
            else:
                fecha_dt = fecha
            dia_semana = fecha_dt.strftime("%A").upper()
            disponibles = await _horario_svc.consultar_disponibles_para_evento(
                str(fecha_dt), dia_semana, str(ev["hora_inicio"]), str(ev["hora_fin"])
            )
            return _ok(disponibles)
        return await _handle(_)


# =============================================================================
# EVENTO  (RF-EV-01 al RF-EV-05)
# =============================================================================

@csrf_exempt_cbv
class EventoListView(View):
    """GET /eventos/  — POST /eventos/"""

    async def get(self, request):
        logger.debug("[EventoListView] GET listar_eventos")
        async def _():
            return _ok(await _evento_svc.listar_eventos())
        return await _handle(_)

    async def post(self, request):
        data = _body(request)
        logger.debug("[EventoListView] POST crear_evento nombre=%s", data.get("nombre"))
        async def _():
            return _ok(await _evento_svc.crear_evento(data), 201)
        return await _handle(_)


@csrf_exempt_cbv
class EventoDetailView(View):
    """GET|PUT|DELETE /eventos/<evento_id>/"""

    async def get(self, request, evento_id):
        logger.debug("[EventoDetailView] GET obtener_evento evento_id=%s", evento_id)
        async def _():
            obj = await _evento_svc.obtener_evento(evento_id)
            return _ok(obj) if obj else _err("Evento no encontrado.", 404)
        return await _handle(_)

    async def put(self, request, evento_id):
        data = _body(request)
        logger.debug("[EventoDetailView] PUT actualizar_evento evento_id=%s", evento_id)
        async def _():
            return _ok(await _evento_svc.actualizar_evento(evento_id, data))
        return await _handle(_)

    async def delete(self, request, evento_id):
        logger.debug("[EventoDetailView] DELETE eliminar_evento evento_id=%s", evento_id)
        async def _():
            return _ok({"eliminado": await _evento_svc.eliminar_evento(evento_id)})
        return await _handle(_)


@csrf_exempt_cbv
class EventoEstadoView(View):
    """PATCH|PUT /eventos/<evento_id>/estado/  — RF-EV-04"""

    async def patch(self, request, evento_id):
        data = _body(request)
        logger.debug("[EventoEstadoView] PATCH actualizar_estado evento_id=%s estado=%s", evento_id, data.get("estado"))
        async def _():
            return _ok(await _evento_svc.actualizar_estado(evento_id, data["estado"]))
        return await _handle(_)

    async def put(self, request, evento_id):
        data = _body(request)
        logger.debug("[EventoEstadoView] PUT actualizar_estado evento_id=%s estado=%s", evento_id, data.get("estado"))
        async def _():
            return _ok(await _evento_svc.actualizar_estado(evento_id, data["estado"]))
        return await _handle(_)
    



@csrf_exempt_cbv
class EventoTipoListView(View):
    """
    GET  /eventos/<evento_id>/tipos/
    POST /eventos/<evento_id>/tipos/
    RF-EV-05
    """

    async def get(self, request, evento_id):
        logger.debug("[EventoTipoListView] GET evento_id=%s", evento_id)
        async def _():
            ev = await _evento_svc.obtener_evento(evento_id)
            return _ok(ev["tipos"] if ev else [])
        return await _handle(_)

    async def post(self, request, evento_id):
        data = _body(request)
        logger.debug("[EventoTipoListView] POST agregar_tipo evento_id=%s tipo=%s", evento_id, data.get("tipo"))
        async def _():
            return _ok(await _evento_svc.agregar_tipo(evento_id, data["tipo"]), 201)
        return await _handle(_)


@csrf_exempt_cbv
class EventoTipoDetailView(View):
    """DELETE /eventos/tipos/<tipo_id>/  — RF-EV-05"""

    async def delete(self, request, tipo_id):
        logger.debug("[EventoTipoDetailView] DELETE eliminar_tipo tipo_id=%s", tipo_id)
        async def _():
            return _ok({"eliminado": await _evento_svc.eliminar_tipo(tipo_id)})
        return await _handle(_)


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

    async def get(self, request, evento_id):
        logger.debug("[EventoPuntoInteresListView] GET evento_id=%s", evento_id)
        async def _():
            return _ok(await _evento_punto_svc.listar_puntos_evento(evento_id))
        return await _handle(_)

    async def post(self, request, evento_id):
        data = _body(request)
        logger.debug("[EventoPuntoInteresListView] POST agregar_punto evento_id=%s punto_interes_id=%s", evento_id, data.get("punto_interes_id"))
        async def _():
            return _ok(
                await _evento_punto_svc.agregar_punto(evento_id, data["punto_interes_id"]), 201
            )
        return await _handle(_)

    async def put(self, request, evento_id):
        data = _body(request)
        logger.debug("[EventoPuntoInteresListView] PUT reemplazar_puntos evento_id=%s", evento_id)
        async def _():
            return _ok(
                await _evento_punto_svc.reemplazar_puntos(evento_id, data["punto_interes_ids"])
            )
        return await _handle(_)


@csrf_exempt_cbv
class EventoPuntoInteresDetailView(View):
    """DELETE /eventos/puntos-evento/<relacion_id>/  — remueve un punto del evento"""

    async def delete(self, request, relacion_id):
        logger.debug("[EventoPuntoInteresDetailView] DELETE relacion_id=%s", relacion_id)
        async def _():
            return _ok({"eliminado": await _evento_punto_svc.remover_punto(relacion_id)})
        return await _handle(_)


# =============================================================================
# ASIGNACIÓN  (RF-EV-07 al RF-EV-10, RF-EV-14, RF-EV-23)
# =============================================================================

@csrf_exempt_cbv
class AsignacionListView(View):
    """
    GET  /eventos/<evento_id>/asignaciones/
    POST /eventos/<evento_id>/asignaciones/        — asignación manual (RF-EV-07)
    """

    async def get(self, request, evento_id):
        logger.debug("[AsignacionListView] GET evento_id=%s", evento_id)
        async def _():
            return _ok(await _asignacion_svc.listar_asignaciones(evento_id))
        return await _handle(_)

    async def post(self, request, evento_id):
        data = _body(request)
        logger.debug("[AsignacionListView] POST asignar_manual evento_id=%s simpatizante_id=%s", evento_id, data.get("simpatizante_id"))
        async def _():
            return _ok(
                await _asignacion_svc.asignar_manual(
                    evento_id,
                    data["simpatizante_id"],
                    data.get("rol"),
                ), 201
            )
        return await _handle(_)


@csrf_exempt_cbv
class AsignacionAutomaticaView(View):
    """POST /eventos/<evento_id>/asignaciones/automatica/  — RF-EV-08"""

    async def post(self, request, evento_id):
        data = _body(request)
        criterios = data.get("criterios", {})
        logger.debug("[AsignacionAutomaticaView] POST asignar_automatico evento_id=%s criterios=%s", evento_id, criterios)
        async def _():
            return _ok(await _asignacion_svc.asignar_automatico(evento_id, criterios), 201)
        return await _handle(_)


@csrf_exempt_cbv
class AsignacionDetailView(View):
    """PUT|DELETE /eventos/asignaciones/<asignacion_id>/  — RF-EV-09"""

    async def put(self, request, asignacion_id):
        data = _body(request)
        logger.debug("[AsignacionDetailView] PUT actualizar_rol asignacion_id=%s rol=%s", asignacion_id, data.get("rol"))
        async def _():
            return _ok(await _asignacion_svc.actualizar_rol(asignacion_id, data["rol"]))
        return await _handle(_)

    async def delete(self, request, asignacion_id):
        logger.debug("[AsignacionDetailView] DELETE remover_asignacion asignacion_id=%s", asignacion_id)
        async def _():
            return _ok({"eliminado": await _asignacion_svc.remover_asignacion(asignacion_id)})
        return await _handle(_)


@csrf_exempt_cbv
class AsistenciaView(View):
    """PATCH /eventos/asignaciones/<asignacion_id>/asistencia/  — RF-EV-14"""

    async def patch(self, request, asignacion_id):
        data = _body(request)
        logger.debug("[AsistenciaView] PATCH registrar_asistencia asignacion_id=%s asistio=%s", asignacion_id, data.get("asistio"))
        async def _():
            return _ok(
                await _asignacion_svc.registrar_asistencia(asignacion_id, bool(data.get("asistio", False)))
            )
        return await _handle(_)


@csrf_exempt_cbv
class ParticipacionTerritorialView(View):
    """
    GET /eventos/<evento_id>/participacion-territorial/<simpatizante_id>/
    RF-EV-23 — Verifica participación territorial reciente.
    """

    async def get(self, request, evento_id, simpatizante_id):
        logger.debug("[ParticipacionTerritorialView] GET evento_id=%s simpatizante_id=%s", evento_id, simpatizante_id)
        async def _():
            return _ok(
                await _asignacion_svc.verificar_participacion_territorial(simpatizante_id, evento_id)
            )
        return await _handle(_)


# =============================================================================
# COBERTURA  (RF-EV-11)
# =============================================================================

@csrf_exempt_cbv
class CoberturaListView(View):
    """GET|POST /eventos/<evento_id>/cobertura/"""

    async def get(self, request, evento_id):
        logger.debug("[CoberturaListView] GET evento_id=%s", evento_id)
        async def _():
            return _ok(await _cobertura_svc.listar_cobertura(evento_id))
        return await _handle(_)

    async def post(self, request, evento_id):
        data = _body(request)
        logger.debug("[CoberturaListView] POST registrar_cobertura evento_id=%s ocupacion=%s requeridos=%s", evento_id, data.get("ocupacion"), data.get("requeridos"))
        async def _():
            return _ok(
                await _cobertura_svc.registrar_cobertura(evento_id, data["ocupacion"], int(data["requeridos"])), 201
            )
        return await _handle(_)


@csrf_exempt_cbv
class CoberturaDetailView(View):
    """PUT|DELETE /eventos/cobertura/<cobertura_id>/"""

    async def put(self, request, cobertura_id):
        data = _body(request)
        logger.debug("[CoberturaDetailView] PUT actualizar_cobertura cobertura_id=%s", cobertura_id)
        async def _():
            return _ok(
                await _cobertura_svc.actualizar_cobertura(
                    cobertura_id,
                    data["ocupacion"],
                    int(data["requeridos"]),
                    int(data.get("asignados", 0)),
                )
            )
        return await _handle(_)

    async def delete(self, request, cobertura_id):
        logger.debug("[CoberturaDetailView] DELETE eliminar_cobertura cobertura_id=%s", cobertura_id)
        async def _():
            return _ok({"eliminado": await _cobertura_svc.eliminar_cobertura(cobertura_id)})
        return await _handle(_)


# =============================================================================
# OBSERVACIÓN  (RF-EV-12, RF-EV-13)
# =============================================================================

@csrf_exempt_cbv
class ObservacionListView(View):
    """GET|POST /eventos/<evento_id>/observaciones/"""

    async def get(self, request, evento_id):
        logger.debug("[ObservacionListView] GET evento_id=%s", evento_id)
        async def _():
            return _ok(await _observacion_svc.listar_observaciones(evento_id))
        return await _handle(_)

    async def post(self, request, evento_id):
        data = _body(request)
        logger.debug("[ObservacionListView] POST registrar_observacion evento_id=%s momento=%s", evento_id, data.get("momento"))
        async def _():
            return _ok(
                await _observacion_svc.registrar_observacion(evento_id, data["momento"], data["contenido"]), 201
            )
        return await _handle(_)


@csrf_exempt_cbv
class ObservacionDetailView(View):
    """DELETE /eventos/observaciones/<observacion_id>/"""

    async def delete(self, request, observacion_id):
        logger.debug("[ObservacionDetailView] DELETE observacion_id=%s", observacion_id)
        async def _():
            return _ok({"eliminado": await _observacion_svc.eliminar_observacion(observacion_id)})
        return await _handle(_)


# =============================================================================
# PARTICIPACIÓN EXTERNA  (RF-EV-18)
# =============================================================================

@csrf_exempt_cbv
class ParticipacionExternaView(View):
    """GET|POST|PUT /eventos/<evento_id>/participacion-externa/"""

    async def get(self, request, evento_id):
        logger.debug("[ParticipacionExternaView] GET evento_id=%s", evento_id)
        async def _():
            return _ok(await _participacion_svc.obtener_participacion(evento_id))
        return await _handle(_)

    async def post(self, request, evento_id):
        data = _body(request)
        logger.debug("[ParticipacionExternaView] POST registrar_participacion evento_id=%s cantidad=%s", evento_id, data.get("cantidad"))
        async def _():
            return _ok(
                await _participacion_svc.registrar_participacion(evento_id, int(data["cantidad"]), data.get("notas")), 201
            )
        return await _handle(_)

    async def put(self, request, evento_id):
        data = _body(request)
        logger.debug("[ParticipacionExternaView] PUT actualizar_participacion evento_id=%s", evento_id)
        async def _():
            return _ok(
                await _participacion_svc.actualizar_participacion(data["id"], int(data["cantidad"]), data.get("notas"))
            )
        return await _handle(_)


# =============================================================================
# MATERIAL PUBLICITARIO  (RF-EV-19)
# =============================================================================

@csrf_exempt_cbv
class MaterialPublicitarioView(View):
    """GET|POST|PUT /eventos/<evento_id>/material/"""

    async def get(self, request, evento_id):
        logger.debug("[MaterialPublicitarioView] GET evento_id=%s", evento_id)
        async def _():
            return _ok(await _material_svc.obtener_material(evento_id))
        return await _handle(_)

    async def post(self, request, evento_id):
        data = _body(request)
        logger.debug("[MaterialPublicitarioView] POST registrar_material evento_id=%s entregado=%s restante=%s", evento_id, data.get("entregado"), data.get("restante"))
        async def _():
            return _ok(
                await _material_svc.registrar_material(evento_id, int(data["entregado"]), int(data["restante"])), 201
            )
        return await _handle(_)

    async def put(self, request, evento_id):
        data = _body(request)
        logger.debug("[MaterialPublicitarioView] PUT actualizar_material evento_id=%s", evento_id)
        async def _():
            return _ok(
                await _material_svc.actualizar_material(data["id"], int(data["entregado"]), int(data["restante"]))
            )
        return await _handle(_)


# =============================================================================
# ESTADO MATERIAL  (RF-EV-20, RF-EV-21, RF-EV-22)
# =============================================================================

@csrf_exempt_cbv
class EstadoMaterialListView(View):
    """GET|POST /eventos/<evento_id>/material/estado/"""

    async def get(self, request, evento_id):
        logger.debug("[EstadoMaterialListView] GET evento_id=%s", evento_id)
        async def _():
            return _ok(await _estado_material_svc.listar_estados(evento_id))
        return await _handle(_)

    async def post(self, request, evento_id):
        data = _body(request)
        logger.debug("[EstadoMaterialListView] POST registrar_estado evento_id=%s estado=%s", evento_id, data.get("estado"))
        async def _():
            return _ok(
                await _estado_material_svc.registrar_estado(evento_id, data["estado"], data.get("notas")), 201
            )
        return await _handle(_)


@csrf_exempt_cbv
class EstadoMaterialCSVView(View):
    """POST /eventos/material/estado/csv/  — RF-EV-21"""

    async def post(self, request):
        archivo = request.FILES.get("archivo")
        logger.debug("[EstadoMaterialCSVView] POST cargar_desde_csv archivo=%s", archivo)
        if not archivo:
            return _err("Se requiere un archivo CSV.", 400)
        async def _():
            return _ok(await _estado_material_svc.cargar_desde_csv(archivo))
        return await _handle(_)


@csrf_exempt_cbv
class PromedioEstadoMaterialView(View):
    """GET /eventos/<evento_id>/material/estado/promedio/  — RF-EV-22"""

    async def get(self, request, evento_id):
        logger.debug("[PromedioEstadoMaterialView] GET evento_id=%s", evento_id)
        async def _():
            return _ok({
                "evento_id": evento_id,
                "promedio": await _estado_material_svc.calcular_promedio_estado(evento_id),
            })
        return await _handle(_)


# =============================================================================
# AUDITORÍA
# =============================================================================

@csrf_exempt_cbv
class AuditoriaView(View):
    """GET /eventos/auditoria/?tabla=&registro_id=  — GET /eventos/auditoria/recientes/"""

    async def get(self, request):
        tabla       = request.GET.get("tabla")
        registro_id = request.GET.get("registro_id")
        logger.debug("[AuditoriaView] GET tabla=%s registro_id=%s", tabla, registro_id)
        if tabla and registro_id:
            async def _():
                return _ok(await _auditoria_svc.historial_registro(tabla, registro_id))
            return await _handle(_)
        limit = int(request.GET.get("limit", 50))
        async def _():
            return _ok(await _auditoria_svc.registros_recientes(limit))
        return await _handle(_)