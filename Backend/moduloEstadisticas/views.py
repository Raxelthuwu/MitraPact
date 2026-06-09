import json
import logging
from typing import Callable

from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

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
# Instancias de servicios
# ─────────────────────────────────────────────────────────────────────────────
_cat_ocupacion_svc      = CatalogoOcupacionService()
_cat_inclinacion_svc    = CatalogoInclinacionVotoService()
_cat_participacion_svc  = CatalogoIntencionParticipacionService()
_cat_problematica_svc   = CatalogoProblematicaService()
_rango_edad_svc         = RangoEdadService()
_periodo_svc            = PeriodoEstadisticoService()
_importacion_svc        = ImportacionCsvService()
_encuesta_svc           = EncuestaService()
_snapshot_svc           = SnapshotTerritorialService()
_variacion_svc          = VariacionTemporalService()
_ranking_svc            = RankingProblematicaService()
_cruce_svc              = ResultadoCruceService()
_caracterizacion_svc    = CaracterizacionTerritorialService()
_exportacion_svc        = ExportacionResultadoService()
_resumen_svc            = ResumenEstadisticoService()


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


async def _handle(func: Callable) -> JsonResponse:
    try:
        return await func()
    except ValueError as exc:
        return _err(str(exc), 400)
    except Exception as exc:
        logger.exception("[moduloEstadisticas] Error inesperado: %s", exc)
        return _err("Error interno del servidor.", 500)


csrf_exempt_cbv = method_decorator(csrf_exempt, name="dispatch")


# =============================================================================
# CATÁLOGOS  (solo lectura)
# RF-EST-03, RF-EST-06, RF-EST-08, RF-EST-11
# =============================================================================

@csrf_exempt_cbv
class CatalogoOcupacionView(View):
    """GET /estadisticas/catalogos/ocupacion/"""

    async def get(self, request):
        async def _():
            return _ok(await _cat_ocupacion_svc.listar())
        return await _handle(_)


@csrf_exempt_cbv
class CatalogoInclinacionVotoView(View):
    """GET /estadisticas/catalogos/inclinacion-voto/"""

    async def get(self, request):
        async def _():
            return _ok(await _cat_inclinacion_svc.listar())
        return await _handle(_)


@csrf_exempt_cbv
class CatalogoIntencionParticipacionView(View):
    """GET /estadisticas/catalogos/intencion-participacion/"""

    async def get(self, request):
        async def _():
            return _ok(await _cat_participacion_svc.listar())
        return await _handle(_)


@csrf_exempt_cbv
class CatalogoProblematicaView(View):
    """GET /estadisticas/catalogos/problematica/"""

    async def get(self, request):
        async def _():
            return _ok(await _cat_problematica_svc.listar())
        return await _handle(_)


# =============================================================================
# RANGO DE EDAD
# RF-EST-36, RF-EST-37, RF-EST-38
# =============================================================================

@csrf_exempt_cbv
class RangoEdadListView(View):
    """GET /estadisticas/rangos-edad/  — POST /estadisticas/rangos-edad/"""

    async def get(self, request):
        async def _():
            return _ok(await _rango_edad_svc.listar())
        return await _handle(_)

    async def post(self, request):
        data = _body(request)
        async def _():
            return _ok(await _rango_edad_svc.crear(
                data["etiqueta"], int(data["edad_min"]), int(data["edad_max"])
            ), 201)
        return await _handle(_)


@csrf_exempt_cbv
class RangoEdadDetailView(View):
    """GET|PUT|DELETE /estadisticas/rangos-edad/<rango_id>/"""

    async def get(self, request, rango_id):
        async def _():
            obj = await _rango_edad_svc.obtener(rango_id)
            return _ok(obj) if obj else _err("Rango de edad no encontrado.", 404)
        return await _handle(_)

    async def put(self, request, rango_id):
        data = _body(request)
        async def _():
            obj = await _rango_edad_svc.actualizar(
                rango_id, data["etiqueta"], int(data["edad_min"]), int(data["edad_max"])
            )
            return _ok(obj) if obj else _err("Rango de edad no encontrado.", 404)
        return await _handle(_)

    async def delete(self, request, rango_id):
        async def _():
            return _ok({"eliminado": await _rango_edad_svc.eliminar(rango_id)})
        return await _handle(_)


# =============================================================================
# PERÍODO ESTADÍSTICO
# RF-EST-05, RF-EST-33
# =============================================================================

@csrf_exempt_cbv
class PeriodoListView(View):
    """GET /estadisticas/periodos/  — POST /estadisticas/periodos/"""

    async def get(self, request):
        async def _():
            return _ok(await _periodo_svc.listar())
        return await _handle(_)

    async def post(self, request):
        data = _body(request)
        async def _():
            return _ok(await _periodo_svc.crear(
                data["etiqueta"], data["fecha_inicio"], data["fecha_fin"]
            ), 201)
        return await _handle(_)


@csrf_exempt_cbv
class PeriodoDetailView(View):
    """GET|PUT|DELETE /estadisticas/periodos/<periodo_id>/"""

    async def get(self, request, periodo_id):
        async def _():
            obj = await _periodo_svc.obtener(periodo_id)
            return _ok(obj) if obj else _err("Período no encontrado.", 404)
        return await _handle(_)

    async def put(self, request, periodo_id):
        data = _body(request)
        async def _():
            obj = await _periodo_svc.actualizar(
                periodo_id, data["etiqueta"], data["fecha_inicio"], data["fecha_fin"]
            )
            return _ok(obj) if obj else _err("Período no encontrado.", 404)
        return await _handle(_)

    async def delete(self, request, periodo_id):
        async def _():
            return _ok({"eliminado": await _periodo_svc.eliminar(periodo_id)})
        return await _handle(_)


# =============================================================================
# IMPORTACIÓN CSV
# RF-EST-01, RF-EST-02
# =============================================================================

@csrf_exempt_cbv
class ImportacionListView(View):
    """GET /estadisticas/importaciones/"""

    async def get(self, request):
        async def _():
            return _ok(await _importacion_svc.listar())
        return await _handle(_)


@csrf_exempt_cbv
class ImportacionUploadView(View):
    """POST /estadisticas/importaciones/upload/"""

    async def post(self, request):
        async def _():
            archivo = request.FILES.get("archivo")
            if not archivo:
                return _err("Se requiere el archivo CSV en el campo 'archivo'.", 400)
            return _ok(await _importacion_svc.importar(archivo), 201)
        return await _handle(_)


@csrf_exempt_cbv
class ImportacionDetailView(View):
    """GET /estadisticas/importaciones/<importacion_id>/"""

    async def get(self, request, importacion_id):
        async def _():
            obj = await _importacion_svc.obtener(importacion_id)
            return _ok(obj) if obj else _err("Importación no encontrada.", 404)
        return await _handle(_)


# =============================================================================
# ENCUESTA
# RF-EST-03 al RF-EST-07, RF-EST-11
# =============================================================================

@csrf_exempt_cbv
class EncuestaListView(View):
    """
    GET  /estadisticas/encuestas/
         ?importacion_id=  ?barrio_id=  ?periodo_id=
    POST /estadisticas/encuestas/
    """

    async def get(self, request):
        async def _():
            return _ok(await _encuesta_svc.listar(
                importacion_id=request.GET.get("importacion_id"),
                barrio_id=request.GET.get("barrio_id"),
                periodo_id=request.GET.get("periodo_id"),
            ))
        return await _handle(_)

    async def post(self, request):
        data = _body(request)
        async def _():
            return _ok(await _encuesta_svc.crear(data), 201)
        return await _handle(_)


@csrf_exempt_cbv
class EncuestaDetailView(View):
    """GET|PUT|DELETE /estadisticas/encuestas/<encuesta_id>/"""

    async def get(self, request, encuesta_id):
        async def _():
            obj = await _encuesta_svc.obtener(encuesta_id)
            return _ok(obj) if obj else _err("Encuesta no encontrada.", 404)
        return await _handle(_)

    async def put(self, request, encuesta_id):
        data = _body(request)
        async def _():
            obj = await _encuesta_svc.actualizar(encuesta_id, data)
            return _ok(obj) if obj else _err("Encuesta no encontrada.", 404)
        return await _handle(_)

    async def delete(self, request, encuesta_id):
        async def _():
            return _ok({"eliminado": await _encuesta_svc.eliminar(encuesta_id)})
        return await _handle(_)


# =============================================================================
# SNAPSHOT TERRITORIAL
# RF-EST-03, RF-EST-04, RF-EST-06, RF-EST-07, RF-EST-35
# =============================================================================

@csrf_exempt_cbv
class SnapshotListView(View):
    """
    GET /estadisticas/snapshots/
        ?barrio_id=  ?periodo_id=
    """

    async def get(self, request):
        async def _():
            return _ok(await _snapshot_svc.listar(
                barrio_id=request.GET.get("barrio_id"),
                periodo_id=request.GET.get("periodo_id"),
            ))
        return await _handle(_)


@csrf_exempt_cbv
class SnapshotDetailView(View):
    """GET|DELETE /estadisticas/snapshots/<snapshot_id>/"""

    async def get(self, request, snapshot_id):
        async def _():
            obj = await _snapshot_svc.obtener(snapshot_id)
            return _ok(obj) if obj else _err("Snapshot no encontrado.", 404)
        return await _handle(_)

    async def delete(self, request, snapshot_id):
        async def _():
            return _ok({"eliminado": await _snapshot_svc.eliminar(snapshot_id)})
        return await _handle(_)


@csrf_exempt_cbv
class SnapshotGenerarView(View):
    """
    POST /estadisticas/snapshots/generar/
         { barrio_id, periodo_id }
    """

    async def post(self, request):
        data = _body(request)
        async def _():
            return _ok(await _snapshot_svc.generar(
                data["barrio_id"], data["periodo_id"]
            ), 201)
        return await _handle(_)


@csrf_exempt_cbv
class SnapshotGenerarTodosView(View):
    """
    POST /estadisticas/snapshots/generar-todos/
         { periodo_id }
    """

    async def post(self, request):
        data = _body(request)
        async def _():
            return _ok(await _snapshot_svc.generar_todos(data["periodo_id"]), 201)
        return await _handle(_)


# =============================================================================
# VARIACIÓN TEMPORAL
# RF-EST-05, RF-EST-33
# =============================================================================

@csrf_exempt_cbv
class VariacionListView(View):
    """
    GET /estadisticas/variaciones/
        ?barrio_id=  ?periodo_actual_id=
    """

    async def get(self, request):
        async def _():
            return _ok(await _variacion_svc.listar(
                barrio_id=request.GET.get("barrio_id"),
                periodo_actual_id=request.GET.get("periodo_actual_id"),
            ))
        return await _handle(_)


@csrf_exempt_cbv
class VariacionDetailView(View):
    """GET /estadisticas/variaciones/<variacion_id>/"""

    async def get(self, request, variacion_id):
        async def _():
            obj = await _variacion_svc.obtener(variacion_id)
            return _ok(obj) if obj else _err("Variación no encontrada.", 404)
        return await _handle(_)


@csrf_exempt_cbv
class VariacionCalcularView(View):
    """
    POST /estadisticas/variaciones/calcular/
         { barrio_id, periodo_anterior_id, periodo_actual_id }
    """

    async def post(self, request):
        data = _body(request)
        async def _():
            return _ok(await _variacion_svc.calcular(
                data["barrio_id"],
                data["periodo_anterior_id"],
                data["periodo_actual_id"],
            ), 201)
        return await _handle(_)


@csrf_exempt_cbv
class VariacionCalcularTodosView(View):
    """
    POST /estadisticas/variaciones/calcular-todos/
         { periodo_anterior_id, periodo_actual_id }
    """

    async def post(self, request):
        data = _body(request)
        async def _():
            return _ok(await _variacion_svc.calcular_todos(
                data["periodo_anterior_id"], data["periodo_actual_id"]
            ), 201)
        return await _handle(_)


# =============================================================================
# RANKING PROBLEMÁTICA
# RF-EST-08, RF-EST-09, RF-EST-10, RF-EST-19
# =============================================================================

@csrf_exempt_cbv
class RankingListView(View):
    """
    GET /estadisticas/rankings/
        ?periodo_id=  ?barrio_id=
    """

    async def get(self, request):
        async def _():
            return _ok(await _ranking_svc.listar(
                periodo_id=request.GET.get("periodo_id"),
                barrio_id=request.GET.get("barrio_id"),
            ))
        return await _handle(_)


@csrf_exempt_cbv
class RankingDetailView(View):
    """GET /estadisticas/rankings/<ranking_id>/"""

    async def get(self, request, ranking_id):
        async def _():
            obj = await _ranking_svc.obtener(ranking_id)
            return _ok(obj) if obj else _err("Ranking no encontrado.", 404)
        return await _handle(_)


@csrf_exempt_cbv
class RankingCalcularView(View):
    """
    POST /estadisticas/rankings/calcular/
         { barrio_id, periodo_id }
    """

    async def post(self, request):
        data = _body(request)
        async def _():
            return _ok(await _ranking_svc.calcular(
                data["barrio_id"], data["periodo_id"]
            ), 201)
        return await _handle(_)


@csrf_exempt_cbv
class RankingCalcularTodosView(View):
    """
    POST /estadisticas/rankings/calcular-todos/
         { periodo_id }
    """

    async def post(self, request):
        data = _body(request)
        async def _():
            return _ok(await _ranking_svc.calcular_todos(data["periodo_id"]), 201)
        return await _handle(_)


# =============================================================================
# RESULTADO CRUCE
# RF-EST-12, RF-EST-13, RF-EST-18, RF-EST-20, RF-EST-30, RF-EST-31,
# RF-EST-36, RF-EST-37
# =============================================================================

@csrf_exempt_cbv
class CruceListView(View):
    """GET /estadisticas/cruces/?periodo_id=<uuid>"""

    async def get(self, request):
        async def _():
            periodo_id = request.GET.get("periodo_id")
            if not periodo_id:
                return _err("Se requiere el parámetro periodo_id.", 400)
            return _ok(await _cruce_svc.listar(periodo_id))
        return await _handle(_)


@csrf_exempt_cbv
class CruceDetailView(View):
    """GET /estadisticas/cruces/<cruce_id>/"""

    async def get(self, request, cruce_id):
        async def _():
            obj = await _cruce_svc.obtener(cruce_id)
            return _ok(obj) if obj else _err("Cruce no encontrado.", 404)
        return await _handle(_)


@csrf_exempt_cbv
class CruceCalcularView(View):
    """
    POST /estadisticas/cruces/calcular/
         { periodo_id, dimension_a, dimension_b }

    Dimensiones válidas: ocupacion | inclinacion_voto | intencion_participacion
                         | problematica_1 | problematica_2
    """

    async def post(self, request):
        data = _body(request)
        async def _():
            return _ok(await _cruce_svc.calcular(
                data["periodo_id"], data["dimension_a"], data["dimension_b"]
            ), 201)
        return await _handle(_)


@csrf_exempt_cbv
class CruceCalcularMultiplesView(View):
    """
    POST /estadisticas/cruces/calcular-multiples/
         { periodo_id, cruces: [{ dimension_a, dimension_b }, ...] }
    """

    async def post(self, request):
        data = _body(request)
        async def _():
            return _ok(await _cruce_svc.calcular_multiples(
                data["periodo_id"], data["cruces"]
            ), 201)
        return await _handle(_)


@csrf_exempt_cbv
class CruceEliminarPeriodoView(View):
    """DELETE /estadisticas/cruces/periodo/<periodo_id>/"""

    async def delete(self, request, periodo_id):
        async def _():
            return _ok({"eliminados": await _cruce_svc.eliminar_por_periodo(periodo_id)})
        return await _handle(_)


# =============================================================================
# CARACTERIZACIÓN TERRITORIAL
# RF-EST-21, RF-EST-22, RF-EST-23, RF-EST-27, RF-EST-28, RF-EST-29,
# RF-EST-32, RF-EST-35
# =============================================================================

@csrf_exempt_cbv
class CaracterizacionListView(View):
    """
    GET /estadisticas/caracterizaciones/
        ?barrio_id=  ?periodo_id=
    """

    async def get(self, request):
        async def _():
            return _ok(await _caracterizacion_svc.listar(
                barrio_id=request.GET.get("barrio_id"),
                periodo_id=request.GET.get("periodo_id"),
            ))
        return await _handle(_)


@csrf_exempt_cbv
class CaracterizacionDetailView(View):
    """GET /estadisticas/caracterizaciones/<caracterizacion_id>/"""

    async def get(self, request, caracterizacion_id):
        async def _():
            obj = await _caracterizacion_svc.obtener(caracterizacion_id)
            return _ok(obj) if obj else _err("Caracterización no encontrada.", 404)
        return await _handle(_)


@csrf_exempt_cbv
class CaracterizacionGenerarView(View):
    """
    POST /estadisticas/caracterizaciones/generar/
         { barrio_id, periodo_id }
    """

    async def post(self, request):
        data = _body(request)
        async def _():
            return _ok(await _caracterizacion_svc.generar(
                data["barrio_id"], data["periodo_id"]
            ), 201)
        return await _handle(_)


@csrf_exempt_cbv
class CaracterizacionGenerarTodosView(View):
    """
    POST /estadisticas/caracterizaciones/generar-todos/
         { periodo_id }
    """

    async def post(self, request):
        data = _body(request)
        async def _():
            return _ok(await _caracterizacion_svc.generar_todos(data["periodo_id"]), 201)
        return await _handle(_)


# =============================================================================
# EXPORTACIÓN DE RESULTADOS
# RF-EST-26
# =============================================================================

@csrf_exempt_cbv
class ExportacionListView(View):
    """GET /estadisticas/exportaciones/?periodo_id="""

    async def get(self, request):
        async def _():
            return _ok(await _exportacion_svc.listar(
                periodo_id=request.GET.get("periodo_id")
            ))
        return await _handle(_)


@csrf_exempt_cbv
class ExportacionDetailView(View):
    """GET /estadisticas/exportaciones/<exportacion_id>/"""

    async def get(self, request, exportacion_id):
        async def _():
            obj = await _exportacion_svc.obtener(exportacion_id)
            return _ok(obj) if obj else _err("Exportación no encontrada.", 404)
        return await _handle(_)


@csrf_exempt_cbv
class ExportacionGenerarView(View):
    """
    POST /estadisticas/exportaciones/generar/
         { periodo_id, tipo_analisis, formato, coordinador_id? }

    tipo_analisis: snapshot | variacion | ranking | cruce | caracterizacion
    formato:       CSV | JSON
    """

    async def post(self, request):
        data = _body(request)
        async def _():
            return _ok(await _exportacion_svc.exportar(
                data["periodo_id"],
                data["tipo_analisis"],
                data["formato"],
                data.get("coordinador_id"),
            ), 201)
        return await _handle(_)


# =============================================================================
# RESUMEN ESTADÍSTICO
# RF-EST-34
# =============================================================================

@csrf_exempt_cbv
class ResumenListView(View):
    """
    GET /estadisticas/resumenes/
        ?barrio_id=  ?periodo_id=
    """

    async def get(self, request):
        async def _():
            return _ok(await _resumen_svc.listar(
                barrio_id=request.GET.get("barrio_id"),
                periodo_id=request.GET.get("periodo_id"),
            ))
        return await _handle(_)


@csrf_exempt_cbv
class ResumenDetailView(View):
    """GET /estadisticas/resumenes/<resumen_id>/"""

    async def get(self, request, resumen_id):
        async def _():
            obj = await _resumen_svc.obtener(resumen_id)
            return _ok(obj) if obj else _err("Resumen no encontrado.", 404)
        return await _handle(_)


@csrf_exempt_cbv
class ResumenGenerarView(View):
    """
    POST /estadisticas/resumenes/generar/
         { barrio_id, periodo_id }
    """

    async def post(self, request):
        data = _body(request)
        async def _():
            return _ok(await _resumen_svc.generar(
                data["barrio_id"], data["periodo_id"]
            ), 201)
        return await _handle(_)


@csrf_exempt_cbv
class ResumenGenerarTodosView(View):
    """
    POST /estadisticas/resumenes/generar-todos/
         { periodo_id }
    """

    async def post(self, request):
        data = _body(request)
        async def _():
            return _ok(await _resumen_svc.generar_todos(data["periodo_id"]), 201)
        return await _handle(_)