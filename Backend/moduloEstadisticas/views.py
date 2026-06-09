import logging
from typing import Callable

from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.shortcuts import render
from Backend.moduloLogin.views import login_requerido

from Backend.moduloEstadisticas.services import (
    CatalogoOcupacionService,
    CatalogoInclinacionVotoService,
    CatalogoIntencionParticipacionService,
    CatalogoProblematicaService,
    RangoEdadService,
    PeriodoEstadisticoService,
    ImportacionCsvService,
    EncuestaService,
    SnapshotTerritorialService,
    VariacionTemporalService,
    RankingProblematicaService,
    ResultadoCruceService,
    CaracterizacionTerritorialService,
    ExportacionResultadoService,
    ResumenEstadisticoService,
)

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Instancias de servicios (singleton ligero — sin estado mutable)
# ─────────────────────────────────────────────────────────────────────────────
_catalogo_ocupacion_svc        = CatalogoOcupacionService()
_catalogo_inclinacion_svc      = CatalogoInclinacionVotoService()
_catalogo_intencion_svc        = CatalogoIntencionParticipacionService()
_catalogo_problematica_svc     = CatalogoProblematicaService()
_rango_edad_svc                = RangoEdadService()
_periodo_svc                   = PeriodoEstadisticoService()
_importacion_svc               = ImportacionCsvService()
_encuesta_svc                  = EncuestaService()
_snapshot_svc                  = SnapshotTerritorialService()
_variacion_svc                 = VariacionTemporalService()
_ranking_svc                   = RankingProblematicaService()
_cruce_svc                     = ResultadoCruceService()
_caracterizacion_svc           = CaracterizacionTerritorialService()
_exportacion_svc               = ExportacionResultadoService()
_resumen_svc                   = ResumenEstadisticoService()


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
@login_requerido
def dashboard_estadisticas(request):
    return render(
        request,
        "moduloEstadisticas/dashboard.html"
    )

@login_requerido
def cruces_estadisticas(request):
    return render(
        request,
        "moduloEstadisticas/cruces.html"
    )

@login_requerido
def importacion_estadisticas(request):
    return render(
        request,
        "moduloEstadisticas/importacion.html"
    )

@login_requerido
def analisis_territorial_estadisticas(request):
    return render(
        request,
        "moduloEstadisticas/analisis_territorial.html"
    )


def _ok(data=None, status: int = 200) -> JsonResponse:
    return JsonResponse({"ok": True, "data": data}, status=status)


def _err(mensaje: str, status: int = 400) -> JsonResponse:
    return JsonResponse({"ok": False, "error": mensaje}, status=status)


def _body(request) -> dict:
    try:
        import json
        return json.loads(request.body or "{}")
    except Exception:
        return {}


async def _handle(func: Callable) -> JsonResponse:
    """Envuelve la lógica de cada handler para capturar excepciones comunes."""
    try:
        return await func()
    except ValueError as exc:
        return _err(str(exc), 400)
    except Exception as exc:
        logger.exception("[moduloEstadisticas] Error inesperado: %s", exc)
        return _err("Error interno del servidor.", 500)


# ─────────────────────────────────────────────────────────────────────────────
# Decorador CSRF exento para todas las vistas (API interna)
# ─────────────────────────────────────────────────────────────────────────────
csrf_exempt_cbv = method_decorator(csrf_exempt, name="dispatch")


# =============================================================================
# CATÁLOGOS (solo lectura)
# =============================================================================

@csrf_exempt_cbv
class CatalogoOcupacionListView(View):
    """GET /estadisticas/catalogos/ocupaciones/"""

    async def get(self, request):
        logger.debug("[CatalogoOcupacionListView] GET listar")
        async def _():
            return _ok(await _catalogo_ocupacion_svc.listar())
        return await _handle(_)


@csrf_exempt_cbv
class CatalogoOcupacionDetailView(View):
    """GET /estadisticas/catalogos/ocupaciones/<codigo>/"""

    async def get(self, request, codigo):
        logger.debug("[CatalogoOcupacionDetailView] GET obtener codigo=%s", codigo)
        async def _():
            obj = await _catalogo_ocupacion_svc.obtener(int(codigo))
            return _ok(obj) if obj else _err("Ocupación no encontrada.", 404)
        return await _handle(_)


@csrf_exempt_cbv
class CatalogoInclinacionVotoListView(View):
    """GET /estadisticas/catalogos/inclinaciones-voto/"""

    async def get(self, request):
        logger.debug("[CatalogoInclinacionVotoListView] GET listar")
        async def _():
            return _ok(await _catalogo_inclinacion_svc.listar())
        return await _handle(_)


@csrf_exempt_cbv
class CatalogoInclinacionVotoDetailView(View):
    """GET /estadisticas/catalogos/inclinaciones-voto/<codigo>/"""

    async def get(self, request, codigo):
        logger.debug("[CatalogoInclinacionVotoDetailView] GET obtener codigo=%s", codigo)
        async def _():
            obj = await _catalogo_inclinacion_svc.obtener(int(codigo))
            return _ok(obj) if obj else _err("Inclinación de voto no encontrada.", 404)
        return await _handle(_)


@csrf_exempt_cbv
class CatalogoIntencionParticipacionListView(View):
    """GET /estadisticas/catalogos/intenciones-participacion/"""

    async def get(self, request):
        logger.debug("[CatalogoIntencionParticipacionListView] GET listar")
        async def _():
            return _ok(await _catalogo_intencion_svc.listar())
        return await _handle(_)


@csrf_exempt_cbv
class CatalogoIntencionParticipacionDetailView(View):
    """GET /estadisticas/catalogos/intenciones-participacion/<codigo>/"""

    async def get(self, request, codigo):
        logger.debug("[CatalogoIntencionParticipacionDetailView] GET obtener codigo=%s", codigo)
        async def _():
            obj = await _catalogo_intencion_svc.obtener(int(codigo))
            return _ok(obj) if obj else _err("Intención de participación no encontrada.", 404)
        return await _handle(_)


@csrf_exempt_cbv
class CatalogoProblematicaListView(View):
    """GET /estadisticas/catalogos/problematicas/"""

    async def get(self, request):
        logger.debug("[CatalogoProblematicaListView] GET listar")
        async def _():
            return _ok(await _catalogo_problematica_svc.listar())
        return await _handle(_)


@csrf_exempt_cbv
class CatalogoProblematicaDetailView(View):
    """GET /estadisticas/catalogos/problematicas/<codigo>/"""

    async def get(self, request, codigo):
        logger.debug("[CatalogoProblematicaDetailView] GET obtener codigo=%s", codigo)
        async def _():
            obj = await _catalogo_problematica_svc.obtener(int(codigo))
            return _ok(obj) if obj else _err("Problemática no encontrada.", 404)
        return await _handle(_)


# =============================================================================
# RANGO DE EDAD
# =============================================================================

@csrf_exempt_cbv
class RangoEdadListView(View):
    """
    GET  /estadisticas/rangos-edad/   — listar
    POST /estadisticas/rangos-edad/   — crear
    """

    async def get(self, request):
        logger.debug("[RangoEdadListView] GET listar")
        async def _():
            return _ok(await _rango_edad_svc.listar())
        return await _handle(_)

    async def post(self, request):
        data = _body(request)
        logger.debug(
            "[RangoEdadListView] POST crear etiqueta=%s edad_min=%s edad_max=%s",
            data.get("etiqueta"), data.get("edad_min"), data.get("edad_max"),
        )
        async def _():
            return _ok(
                await _rango_edad_svc.crear(
                    data["etiqueta"], int(data["edad_min"]), int(data["edad_max"])
                ), 201
            )
        return await _handle(_)


@csrf_exempt_cbv
class RangoEdadDetailView(View):
    """GET|PUT|DELETE /estadisticas/rangos-edad/<rango_id>/"""

    async def get(self, request, rango_id):
        logger.debug("[RangoEdadDetailView] GET obtener rango_id=%s", rango_id)
        async def _():
            obj = await _rango_edad_svc.obtener(rango_id)
            return _ok(obj) if obj else _err("Rango de edad no encontrado.", 404)
        return await _handle(_)

    async def put(self, request, rango_id):
        data = _body(request)
        logger.debug("[RangoEdadDetailView] PUT actualizar rango_id=%s", rango_id)
        async def _():
            obj = await _rango_edad_svc.actualizar(
                rango_id, data["etiqueta"], int(data["edad_min"]), int(data["edad_max"])
            )
            return _ok(obj) if obj else _err("Rango de edad no encontrado.", 404)
        return await _handle(_)

    async def delete(self, request, rango_id):
        logger.debug("[RangoEdadDetailView] DELETE eliminar rango_id=%s", rango_id)
        async def _():
            return _ok({"eliminado": await _rango_edad_svc.eliminar(rango_id)})
        return await _handle(_)


# =============================================================================
# PERÍODO ESTADÍSTICO
# =============================================================================

@csrf_exempt_cbv
class PeriodoEstadisticoListView(View):
    """
    GET  /estadisticas/periodos/   — listar
    POST /estadisticas/periodos/   — crear
    """

    async def get(self, request):
        logger.debug("[PeriodoEstadisticoListView] GET listar")
        async def _():
            return _ok(await _periodo_svc.listar())
        return await _handle(_)

    async def post(self, request):
        data = _body(request)
        logger.debug(
            "[PeriodoEstadisticoListView] POST crear etiqueta=%s %s→%s",
            data.get("etiqueta"), data.get("fecha_inicio"), data.get("fecha_fin"),
        )
        async def _():
            return _ok(
                await _periodo_svc.crear(
                    data["etiqueta"], data["fecha_inicio"], data["fecha_fin"]
                ), 201
            )
        return await _handle(_)


@csrf_exempt_cbv
class PeriodoEstadisticoDetailView(View):
    """GET|PUT|DELETE /estadisticas/periodos/<periodo_id>/"""

    async def get(self, request, periodo_id):
        logger.debug("[PeriodoEstadisticoDetailView] GET obtener periodo_id=%s", periodo_id)
        async def _():
            obj = await _periodo_svc.obtener(periodo_id)
            return _ok(obj) if obj else _err("Período estadístico no encontrado.", 404)
        return await _handle(_)

    async def put(self, request, periodo_id):
        data = _body(request)
        logger.debug("[PeriodoEstadisticoDetailView] PUT actualizar periodo_id=%s", periodo_id)
        async def _():
            obj = await _periodo_svc.actualizar(
                periodo_id, data["etiqueta"], data["fecha_inicio"], data["fecha_fin"]
            )
            return _ok(obj) if obj else _err("Período estadístico no encontrado.", 404)
        return await _handle(_)

    async def delete(self, request, periodo_id):
        logger.debug("[PeriodoEstadisticoDetailView] DELETE eliminar periodo_id=%s", periodo_id)
        async def _():
            return _ok({"eliminado": await _periodo_svc.eliminar(periodo_id)})
        return await _handle(_)


# =============================================================================
# IMPORTACIÓN CSV
# =============================================================================

@csrf_exempt_cbv
class ImportacionCsvListView(View):
    """
    GET  /estadisticas/importaciones/          — listar
    POST /estadisticas/importaciones/          — importar archivo CSV (multipart)
    """

    async def get(self, request):
        logger.debug("[ImportacionCsvListView] GET listar")
        async def _():
            return _ok(await _importacion_svc.listar())
        return await _handle(_)

    async def post(self, request):
        archivo    = request.FILES.get("archivo")
        periodo_id = request.POST.get("periodo_id")  # ── CAMBIO: capturar periodo_id del formulario
        logger.debug("[ImportacionCsvListView] POST importar archivo=%s periodo_id=%s", getattr(archivo, "name", None), periodo_id)
        
        # Ajustamos el mensaje para reflejar que acepta ambos formatos
        if not archivo:
            return _err("Se requiere un archivo CSV o Excel (.xlsx, .xls).", 400)
            
        async def _():
            nombre_archivo = archivo.name.lower()
            
            # ── DETECCIÓN DE FORMATO Y DERIVACIÓN AL SERVICIO CORRESPONDIENTE ──
            if nombre_archivo.endswith(('.xlsx', '.xls')):
                logger.info("[ImportacionCsvListView] Detectado archivo Excel. Derivando a importar_excel.")
                
                # CASO A: Si definiste 'importar_excel' como método ASÍNCRONO (async def) en tu servicio:
                resultado = await _importacion_svc.importar_excel(archivo, periodo_id=periodo_id)
                
                # CASO B: Si definiste 'importar_excel' como método SÍNCRONICO tradicional (def) debido a Pandas,
                # debes usar sync_to_async descomentando las siguientes dos líneas (y comentando la del CASO A):
                # from asgiref.sync import sync_to_async
                # resultado = await sync_to_async(_importacion_svc.importar_excel)(archivo, periodo_id=periodo_id)
            else:
                logger.info("[ImportacionCsvListView] Detectado archivo CSV. Derivando a importar estándar.")
                # Flujo normal de CSV original
                resultado = await _importacion_svc.importar(archivo, periodo_id=periodo_id)  # ── CAMBIO: pasar periodo_id al servicio

            # ── PIPELINE AUTOMÁTICO POST-IMPORTACIÓN ──
            # Dispara la regeneración completa de estadísticas para que los
            # tableros muestren datos inmediatamente sin ir al dashboard.
            if periodo_id:
                try:
                    import asyncio
                    logger.info(
                        "[ImportacionCsvListView] Iniciando pipeline automático para periodo_id=%s",
                        periodo_id,
                    )
                    # Paso 1: snapshots (los rankings los necesitan)
                    await _snapshot_svc.generar_todos(periodo_id)
                    # Paso 2: rankings + caracterizaciones + resúmenes en paralelo
                    await asyncio.gather(
                        _ranking_svc.calcular_todos(periodo_id),
                        _caracterizacion_svc.generar_todos(periodo_id),
                        _resumen_svc.generar_todos(periodo_id),
                    )
                    logger.info(
                        "[ImportacionCsvListView] Pipeline completado para periodo_id=%s",
                        periodo_id,
                    )
                except Exception as pipeline_err:
                    # El pipeline falló pero la importación fue exitosa;
                    # se registra sin interrumpir la respuesta al cliente.
                    logger.error(
                        "[ImportacionCsvListView] Error en pipeline post-importación: %s",
                        str(pipeline_err),
                        exc_info=True,
                    )

            return _ok(resultado, 201)
        return await _handle(_)


@csrf_exempt_cbv
class ImportacionCsvDetailView(View):
    """GET /estadisticas/importaciones/<importacion_id>/"""

    async def get(self, request, importacion_id):
        logger.debug("[ImportacionCsvDetailView] GET obtener importacion_id=%s", importacion_id)
        async def _():
            obj = await _importacion_svc.obtener(importacion_id)
            return _ok(obj) if obj else _err("Importación no encontrada.", 404)
        return await _handle(_)


@csrf_exempt_cbv
class ImportacionCsvEstadoView(View):
    """GET /estadisticas/importaciones/<importacion_id>/estado/"""

    async def get(self, request, importacion_id):
        logger.debug("[ImportacionCsvEstadoView] GET obtener_estado importacion_id=%s", importacion_id)
        async def _():
            obj = await _importacion_svc.obtener_estado(importacion_id)
            return _ok(obj) if obj else _err("Importación no encontrada.", 404)
        return await _handle(_)


# =============================================================================
# ENCUESTA
# =============================================================================

@csrf_exempt_cbv
class EncuestaListView(View):
    """
    GET  /estadisticas/encuestas/?importacion_id=&barrio_id=&periodo_id=
    POST /estadisticas/encuestas/
    """

    async def get(self, request):
        importacion_id = request.GET.get("importacion_id")
        barrio_id      = request.GET.get("barrio_id")
        periodo_id     = request.GET.get("periodo_id")
        logger.debug(
            "[EncuestaListView] GET listar importacion_id=%s barrio_id=%s periodo_id=%s",
            importacion_id, barrio_id, periodo_id,
        )
        async def _():
            return _ok(await _encuesta_svc.listar(
                importacion_id=importacion_id,
                barrio_id=barrio_id,
                periodo_id=periodo_id,
            ))
        return await _handle(_)

    async def post(self, request):
        data = _body(request)
        logger.debug("[EncuestaListView] POST crear encuesta")
        async def _():
            return _ok(await _encuesta_svc.crear(data), 201)
        return await _handle(_)


@csrf_exempt_cbv
class EncuestaDetailView(View):
    """GET|PUT|DELETE /estadisticas/encuestas/<encuesta_id>/"""

    async def get(self, request, encuesta_id):
        logger.debug("[EncuestaDetailView] GET obtener encuesta_id=%s", encuesta_id)
        async def _():
            obj = await _encuesta_svc.obtener(encuesta_id)
            return _ok(obj) if obj else _err("Encuesta no encontrada.", 404)
        return await _handle(_)

    async def put(self, request, encuesta_id):
        data = _body(request)
        logger.debug("[EncuestaDetailView] PUT actualizar encuesta_id=%s", encuesta_id)
        async def _():
            obj = await _encuesta_svc.actualizar(encuesta_id, data)
            return _ok(obj) if obj else _err("Encuesta no encontrada.", 404)
        return await _handle(_)

    async def delete(self, request, encuesta_id):
        logger.debug("[EncuestaDetailView] DELETE eliminar encuesta_id=%s", encuesta_id)
        async def _():
            return _ok({"eliminado": await _encuesta_svc.eliminar(encuesta_id)})
        return await _handle(_)


# =============================================================================
# SNAPSHOT TERRITORIAL
# =============================================================================

@csrf_exempt_cbv
class SnapshotTerritorialListView(View):
    """GET /estadisticas/snapshots/?barrio_id=&periodo_id="""

    async def get(self, request):
        barrio_id  = request.GET.get("barrio_id")
        periodo_id = request.GET.get("periodo_id")
        logger.debug(
            "[SnapshotTerritorialListView] GET listar barrio_id=%s periodo_id=%s",
            barrio_id, periodo_id,
        )
        async def _():
            return _ok(await _snapshot_svc.listar(barrio_id=barrio_id, periodo_id=periodo_id))
        return await _handle(_)


@csrf_exempt_cbv
class SnapshotTerritorialDetailView(View):
    """GET|DELETE /estadisticas/snapshots/<snapshot_id>/"""

    async def get(self, request, snapshot_id):
        logger.debug("[SnapshotTerritorialDetailView] GET obtener snapshot_id=%s", snapshot_id)
        async def _():
            obj = await _snapshot_svc.obtener(snapshot_id)
            return _ok(obj) if obj else _err("Snapshot no encontrado.", 404)
        return await _handle(_)

    async def delete(self, request, snapshot_id):
        logger.debug("[SnapshotTerritorialDetailView] DELETE eliminar snapshot_id=%s", snapshot_id)
        async def _():
            return _ok({"eliminado": await _snapshot_svc.eliminar(snapshot_id)})
        return await _handle(_)


@csrf_exempt_cbv
class SnapshotGenerarView(View):
    """
    POST /estadisticas/periodos/<periodo_id>/snapshots/generar/
         body: { "barrio_id": "..." }   — genera snapshot de un barrio
    POST /estadisticas/periodos/<periodo_id>/snapshots/generar-todos/
                                         — genera snapshot de todos los barrios
    """

    async def post(self, request, periodo_id):
        data = _body(request)
        barrio_id = data.get("barrio_id")
        logger.debug(
            "[SnapshotGenerarView] POST generar periodo_id=%s barrio_id=%s",
            periodo_id, barrio_id,
        )
        async def _():
            if barrio_id:
                return _ok(await _snapshot_svc.generar(barrio_id, periodo_id), 201)
            return _err("Se requiere barrio_id.", 400)
        return await _handle(_)


@csrf_exempt_cbv
class SnapshotGenerarTodosView(View):
    """POST /estadisticas/periodos/<periodo_id>/snapshots/generar-todos/"""

    async def post(self, request, periodo_id):
        logger.debug("[SnapshotGenerarTodosView] POST generar_todos periodo_id=%s", periodo_id)
        async def _():
            return _ok(await _snapshot_svc.generar_todos(periodo_id), 201)
        return await _handle(_)


# =============================================================================
# VARIACIÓN TEMPORAL
# =============================================================================

@csrf_exempt_cbv
class VariacionTemporalListView(View):
    """GET /estadisticas/variaciones/?barrio_id=&periodo_actual_id="""

    async def get(self, request):
        barrio_id         = request.GET.get("barrio_id")
        periodo_actual_id = request.GET.get("periodo_actual_id")
        logger.debug(
            "[VariacionTemporalListView] GET listar barrio_id=%s periodo_actual_id=%s",
            barrio_id, periodo_actual_id,
        )
        async def _():
            return _ok(await _variacion_svc.listar(
                barrio_id=barrio_id, periodo_actual_id=periodo_actual_id
            ))
        return await _handle(_)


@csrf_exempt_cbv
class VariacionTemporalDetailView(View):
    """GET /estadisticas/variaciones/<variacion_id>/"""

    async def get(self, request, variacion_id):
        logger.debug("[VariacionTemporalDetailView] GET obtener variacion_id=%s", variacion_id)
        async def _():
            obj = await _variacion_svc.obtener(variacion_id)
            return _ok(obj) if obj else _err("Variación temporal no encontrada.", 404)
        return await _handle(_)


@csrf_exempt_cbv
class VariacionCalcularView(View):
    """
    POST /estadisticas/variaciones/calcular/
         body: { "barrio_id", "periodo_anterior_id", "periodo_actual_id" }
    """

    async def post(self, request):
        data = _body(request)
        logger.debug(
            "[VariacionCalcularView] POST calcular barrio_id=%s %s→%s",
            data.get("barrio_id"), data.get("periodo_anterior_id"), data.get("periodo_actual_id"),
        )
        async def _():
            obj = await _variacion_svc.calcular(
                data["barrio_id"], data["periodo_anterior_id"], data["periodo_actual_id"]
            )
            return _ok(obj, 201) if obj else _err("No hay datos suficientes para calcular la variación.", 422)
        return await _handle(_)


@csrf_exempt_cbv
class VariacionCalcularTodosView(View):
    """
    POST /estadisticas/variaciones/calcular-todos/
         body: { "periodo_anterior_id", "periodo_actual_id" }
    """

    async def post(self, request):
        data = _body(request)
        logger.debug(
            "[VariacionCalcularTodosView] POST calcular_todos %s→%s",
            data.get("periodo_anterior_id"), data.get("periodo_actual_id"),
        )
        async def _():
            return _ok(
                await _variacion_svc.calcular_todos(
                    data["periodo_anterior_id"], data["periodo_actual_id"]
                ), 201
            )
        return await _handle(_)


# =============================================================================
# RANKING PROBLEMÁTICA
# =============================================================================

@csrf_exempt_cbv
class RankingProblematicaListView(View):
    """GET /estadisticas/rankings/?periodo_id=&barrio_id="""

    async def get(self, request):
        periodo_id = request.GET.get("periodo_id")
        barrio_id  = request.GET.get("barrio_id")
        logger.debug(
            "[RankingProblematicaListView] GET listar periodo_id=%s barrio_id=%s",
            periodo_id, barrio_id,
        )
        async def _():
            return _ok(await _ranking_svc.listar(periodo_id=periodo_id, barrio_id=barrio_id))
        return await _handle(_)


@csrf_exempt_cbv
class RankingProblematicaDetailView(View):
    """GET /estadisticas/rankings/<ranking_id>/"""

    async def get(self, request, ranking_id):
        logger.debug("[RankingProblematicaDetailView] GET obtener ranking_id=%s", ranking_id)
        async def _():
            obj = await _ranking_svc.obtener(ranking_id)
            return _ok(obj) if obj else _err("Ranking no encontrado.", 404)
        return await _handle(_)


@csrf_exempt_cbv
class RankingCalcularView(View):
    """
    POST /estadisticas/rankings/calcular/
         body: { "barrio_id", "periodo_id" }
    """

    async def post(self, request):
        data = _body(request)
        logger.debug(
            "[RankingCalcularView] POST calcular barrio_id=%s periodo_id=%s",
            data.get("barrio_id"), data.get("periodo_id"),
        )
        async def _():
            return _ok(
                await _ranking_svc.calcular(data["barrio_id"], data["periodo_id"]), 201
            )
        return await _handle(_)


@csrf_exempt_cbv
class RankingCalcularTodosView(View):
    """
    POST /estadisticas/rankings/calcular-todos/
         body: { "periodo_id" }
    """

    async def post(self, request):
        data = _body(request)
        logger.debug(
            "[RankingCalcularTodosView] POST calcular_todos periodo_id=%s", data.get("periodo_id")
        )
        async def _():
            return _ok(await _ranking_svc.calcular_todos(data["periodo_id"]), 201)
        return await _handle(_)


# =============================================================================
# RESULTADO CRUCE
# =============================================================================

@csrf_exempt_cbv
class ResultadoCruceListView(View):
    """GET /estadisticas/cruces/?periodo_id="""

    async def get(self, request):
        periodo_id = request.GET.get("periodo_id", "")
        logger.debug("[ResultadoCruceListView] GET listar periodo_id=%s", periodo_id)
        async def _():
            return _ok(await _cruce_svc.listar(periodo_id))
        return await _handle(_)


@csrf_exempt_cbv
class ResultadoCruceDetailView(View):
    """GET /estadisticas/cruces/<cruce_id>/"""

    async def get(self, request, cruce_id):
        logger.debug("[ResultadoCruceDetailView] GET obtener cruce_id=%s", cruce_id)
        async def _():
            obj = await _cruce_svc.obtener(cruce_id)
            return _ok(obj) if obj else _err("Cruce no encontrado.", 404)
        return await _handle(_)


@csrf_exempt_cbv
class ResultadoCruceCalcularView(View):
    """
    POST /estadisticas/cruces/calcular/
         body: { "periodo_id", "dimension_a", "dimension_b" }
    """

    async def post(self, request):
        data = _body(request)
        logger.debug(
            "[ResultadoCruceCalcularView] POST calcular periodo_id=%s %s×%s",
            data.get("periodo_id"), data.get("dimension_a"), data.get("dimension_b"),
        )
        async def _():
            return _ok(
                await _cruce_svc.calcular(
                    data["periodo_id"], data["dimension_a"], data["dimension_b"]
                ), 201
            )
        return await _handle(_)


@csrf_exempt_cbv
class ResultadoCruceCalcularMultiplesView(View):
    """
    POST /estadisticas/cruces/calcular-multiples/
         body: { "periodo_id", "cruces": [{"dimension_a": ..., "dimension_b": ...}] }
    """

    async def post(self, request):
        data = _body(request)
        logger.debug(
            "[ResultadoCruceCalcularMultiplesView] POST calcular_multiples periodo_id=%s cruces=%d",
            data.get("periodo_id"), len(data.get("cruces", [])),
        )
        async def _():
            return _ok(
                await _cruce_svc.calcular_multiples(data["periodo_id"], data["cruces"]), 201
            )
        return await _handle(_)


@csrf_exempt_cbv
class ResultadoCruceEliminarPeriodoView(View):
    """DELETE /estadisticas/cruces/periodo/<periodo_id>/"""

    async def delete(self, request, periodo_id):
        logger.debug(
            "[ResultadoCruceEliminarPeriodoView] DELETE eliminar_por_periodo periodo_id=%s", periodo_id
        )
        async def _():
            return _ok({"eliminados": await _cruce_svc.eliminar_por_periodo(periodo_id)})
        return await _handle(_)


# =============================================================================
# CARACTERIZACIÓN TERRITORIAL
# =============================================================================

@csrf_exempt_cbv
class CaracterizacionTerritorialListView(View):
    """GET /estadisticas/caracterizaciones/?barrio_id=&periodo_id="""

    async def get(self, request):
        barrio_id  = request.GET.get("barrio_id")
        periodo_id = request.GET.get("periodo_id")
        logger.debug(
            "[CaracterizacionTerritorialListView] GET listar barrio_id=%s periodo_id=%s",
            barrio_id, periodo_id,
        )
        async def _():
            return _ok(await _caracterizacion_svc.listar(barrio_id=barrio_id, periodo_id=periodo_id))
        return await _handle(_)


@csrf_exempt_cbv
class CaracterizacionTerritorialDetailView(View):
    """GET /estadisticas/caracterizaciones/<caracterizacion_id>/"""

    async def get(self, request, caracterizacion_id):
        logger.debug(
            "[CaracterizacionTerritorialDetailView] GET obtener caracterizacion_id=%s", caracterizacion_id
        )
        async def _():
            obj = await _caracterizacion_svc.obtener(caracterizacion_id)
            return _ok(obj) if obj else _err("Caracterización no encontrada.", 404)
        return await _handle(_)


@csrf_exempt_cbv
class CaracterizacionGenerarView(View):
    """
    POST /estadisticas/periodos/<periodo_id>/caracterizaciones/generar/
         body: { "barrio_id": "..." }
    """

    async def post(self, request, periodo_id):
        data = _body(request)
        barrio_id = data.get("barrio_id")
        logger.debug(
            "[CaracterizacionGenerarView] POST generar periodo_id=%s barrio_id=%s",
            periodo_id, barrio_id,
        )
        async def _():
            if not barrio_id:
                return _err("Se requiere barrio_id.", 400)
            obj = await _caracterizacion_svc.generar(barrio_id, periodo_id)
            return _ok(obj, 201) if obj else _err("No hay datos suficientes para generar la caracterización.", 422)
        return await _handle(_)


@csrf_exempt_cbv
class CaracterizacionGenerarTodosView(View):
    """POST /estadisticas/periodos/<periodo_id>/caracterizaciones/generar-todos/"""

    async def post(self, request, periodo_id):
        logger.debug(
            "[CaracterizacionGenerarTodosView] POST generar_todos periodo_id=%s", periodo_id
        )
        async def _():
            return _ok(await _caracterizacion_svc.generar_todos(periodo_id), 201)
        return await _handle(_)


# =============================================================================
# EXPORTACIÓN RESULTADO
# =============================================================================

@csrf_exempt_cbv
class ExportacionResultadoListView(View):
    """GET /estadisticas/exportaciones/?periodo_id="""

    async def get(self, request):
        periodo_id = request.GET.get("periodo_id")
        logger.debug("[ExportacionResultadoListView] GET listar periodo_id=%s", periodo_id)
        async def _():
            return _ok(await _exportacion_svc.listar(periodo_id=periodo_id))
        return await _handle(_)


@csrf_exempt_cbv
class ExportacionResultadoDetailView(View):
    """GET /estadisticas/exportaciones/<exportacion_id>/"""

    async def get(self, request, exportacion_id):
        logger.debug(
            "[ExportacionResultadoDetailView] GET obtener exportacion_id=%s", exportacion_id
        )
        async def _():
            obj = await _exportacion_svc.obtener(exportacion_id)
            return _ok(obj) if obj else _err("Exportación no encontrada.", 404)
        return await _handle(_)


@csrf_exempt_cbv
class ExportacionResultadoExportarView(View):
    """
    POST /estadisticas/exportaciones/exportar/
         body: { "periodo_id", "tipo_analisis", "formato", "coordinador_id"? }
         tipos válidos: snapshot | variacion | ranking | cruce | caracterizacion
         formatos válidos: CSV | JSON
    """

    async def post(self, request):
        data = _body(request)
        logger.debug(
            "[ExportacionResultadoExportarView] POST exportar periodo_id=%s tipo=%s formato=%s",
            data.get("periodo_id"), data.get("tipo_analisis"), data.get("formato"),
        )
        async def _():
            return _ok(
                await _exportacion_svc.exportar(
                    periodo_id=data["periodo_id"],
                    tipo_analisis=data["tipo_analisis"],
                    formato=data["formato"],
                    coordinador_id=data.get("coordinador_id"),
                ), 201
            )
        return await _handle(_)


# =============================================================================
# RESUMEN ESTADÍSTICO
# =============================================================================

@csrf_exempt_cbv
class ResumenEstadisticoListView(View):
    """GET /estadisticas/resumenes/?barrio_id=&periodo_id="""

    async def get(self, request):
        barrio_id  = request.GET.get("barrio_id")
        periodo_id = request.GET.get("periodo_id")
        logger.debug(
            "[ResumenEstadisticoListView] GET listar barrio_id=%s periodo_id=%s",
            barrio_id, periodo_id,
        )
        async def _():
            return _ok(await _resumen_svc.listar(barrio_id=barrio_id, periodo_id=periodo_id))
        return await _handle(_)


@csrf_exempt_cbv
class ResumenEstadisticoDetailView(View):
    """GET /estadisticas/resumenes/<resumen_id>/"""

    async def get(self, request, resumen_id):
        logger.debug("[ResumenEstadisticoDetailView] GET obtener resumen_id=%s", resumen_id)
        async def _():
            obj = await _resumen_svc.obtener(resumen_id)
            return _ok(obj) if obj else _err("Resumen estadístico no encontrado.", 404)
        return await _handle(_)


@csrf_exempt_cbv
class ResumenGenerarView(View):
    """
    POST /estadisticas/periodos/<periodo_id>/resumenes/generar/
         body: { "barrio_id": "..." }
    """

    async def post(self, request, periodo_id):
        data = _body(request)
        barrio_id = data.get("barrio_id")
        logger.debug(
            "[ResumenGenerarView] POST generar periodo_id=%s barrio_id=%s",
            periodo_id, barrio_id,
        )
        async def _():
            if not barrio_id:
                return _err("Se requiere barrio_id.", 400)
            return _ok(await _resumen_svc.generar(barrio_id, periodo_id), 201)
        return await _handle(_)


@csrf_exempt_cbv
class ResumenGenerarTodosView(View):
    """POST /estadisticas/periodos/<periodo_id>/resumenes/generar-todos/"""

    async def post(self, request, periodo_id):
        logger.debug(
            "[ResumenGenerarTodosView] POST generar_todos periodo_id=%s", periodo_id
        )
        async def _():
            return _ok(await _resumen_svc.generar_todos(periodo_id), 201)
        return await _handle(_)