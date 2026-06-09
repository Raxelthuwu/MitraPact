from django.urls import path
from .views import dashboard_estadisticas, cruces_estadisticas, importacion_estadisticas, analisis_territorial_estadisticas

from Backend.moduloEstadisticas.views import (
    # Catálogos
    CatalogoOcupacionListView,
    CatalogoOcupacionDetailView,
    CatalogoInclinacionVotoListView,
    CatalogoInclinacionVotoDetailView,
    CatalogoIntencionParticipacionListView,
    CatalogoIntencionParticipacionDetailView,
    CatalogoProblematicaListView,
    CatalogoProblematicaDetailView,
    # Rango de edad
    RangoEdadListView,
    RangoEdadDetailView,
    # Período estadístico
    PeriodoEstadisticoListView,
    PeriodoEstadisticoDetailView,
    # Importación CSV
    ImportacionCsvListView,
    ImportacionCsvDetailView,
    ImportacionCsvEstadoView,
    # Encuesta
    EncuestaListView,
    EncuestaDetailView,
    # Snapshot territorial
    SnapshotTerritorialListView,
    SnapshotTerritorialDetailView,
    SnapshotGenerarView,
    SnapshotGenerarTodosView,
    # Variación temporal
    VariacionTemporalListView,
    VariacionTemporalDetailView,
    VariacionCalcularView,
    VariacionCalcularTodosView,
    # Ranking problemática
    RankingProblematicaListView,
    RankingProblematicaDetailView,
    RankingCalcularView,
    RankingCalcularTodosView,
    # Resultado cruce
    ResultadoCruceListView,
    ResultadoCruceDetailView,
    ResultadoCruceCalcularView,
    ResultadoCruceCalcularMultiplesView,
    ResultadoCruceEliminarPeriodoView,
    # Caracterización territorial
    CaracterizacionTerritorialListView,
    CaracterizacionTerritorialDetailView,
    CaracterizacionGenerarView,
    CaracterizacionGenerarTodosView,
    # Exportación resultado
    ExportacionResultadoListView,
    ExportacionResultadoDetailView,
    ExportacionResultadoExportarView,
    # Resumen estadístico
    ResumenEstadisticoListView,
    ResumenEstadisticoDetailView,
    ResumenGenerarView,
    ResumenGenerarTodosView,
)

app_name = "moduloEstadisticas"

urlpatterns = [

    # ─── Vistas HTML ─────────────────────────────────────────────────────────
    path(
        "dashboard/",
        dashboard_estadisticas,
        name="dashboard-estadisticas"
    ),
    path(
        "analisis_territorial/",
        analisis_territorial_estadisticas,
        name="analisis_territorial-estadisticas"
    ),
    path(
        "cruces/",
        cruces_estadisticas,
        name="cruces-estadisticas"
    ),
    path(
        "importacion/",
        importacion_estadisticas,
        name="importacion-estadisticas"
    ),

    # ─── API REST — Catálogos (solo lectura) ──────────────────────────────────
    path(
        "api/catalogos/ocupaciones/",
        CatalogoOcupacionListView.as_view(),
        name="catalogo-ocupacion-list",
    ),
    path(
        "api/catalogos/ocupaciones/<int:codigo>/",
        CatalogoOcupacionDetailView.as_view(),
        name="catalogo-ocupacion-detail",
    ),
    path(
        "api/catalogos/inclinaciones-voto/",
        CatalogoInclinacionVotoListView.as_view(),
        name="catalogo-inclinacion-list",
    ),
    path(
        "api/catalogos/inclinaciones-voto/<int:codigo>/",
        CatalogoInclinacionVotoDetailView.as_view(),
        name="catalogo-inclinacion-detail",
    ),
    path(
        "api/catalogos/intenciones-participacion/",
        CatalogoIntencionParticipacionListView.as_view(),
        name="catalogo-intencion-list",
    ),
    path(
        "api/catalogos/intenciones-participacion/<int:codigo>/",
        CatalogoIntencionParticipacionDetailView.as_view(),
        name="catalogo-intencion-detail",
    ),
    path(
        "api/catalogos/problematicas/",
        CatalogoProblematicaListView.as_view(),
        name="catalogo-problematica-list",
    ),
    path(
        "api/catalogos/problematicas/<int:codigo>/",
        CatalogoProblematicaDetailView.as_view(),
        name="catalogo-problematica-detail",
    ),

    # ─── API REST — Rango de edad ─────────────────────────────────────────────
    path(
        "api/rangos-edad/",
        RangoEdadListView.as_view(),
        name="rango-edad-list",
    ),
    path(
        "api/rangos-edad/<str:rango_id>/",
        RangoEdadDetailView.as_view(),
        name="rango-edad-detail",
    ),

    # ─── API REST — Período estadístico ──────────────────────────────────────
    path(
        "api/periodos/",
        PeriodoEstadisticoListView.as_view(),
        name="periodo-list",
    ),
    path(
        "api/periodos/<str:periodo_id>/",
        PeriodoEstadisticoDetailView.as_view(),
        name="periodo-detail",
    ),

    # ─── API REST — Acciones anidadas bajo período ────────────────────────────
    path(
        "api/periodos/<str:periodo_id>/snapshots/generar/",
        SnapshotGenerarView.as_view(),
        name="snapshot-generar",
    ),
    path(
        "api/periodos/<str:periodo_id>/snapshots/generar-todos/",
        SnapshotGenerarTodosView.as_view(),
        name="snapshot-generar-todos",
    ),
    path(
        "api/periodos/<str:periodo_id>/caracterizaciones/generar/",
        CaracterizacionGenerarView.as_view(),
        name="caracterizacion-generar",
    ),
    path(
        "api/periodos/<str:periodo_id>/caracterizaciones/generar-todos/",
        CaracterizacionGenerarTodosView.as_view(),
        name="caracterizacion-generar-todos",
    ),
    path(
        "api/periodos/<str:periodo_id>/resumenes/generar/",
        ResumenGenerarView.as_view(),
        name="resumen-generar",
    ),
    path(
        "api/periodos/<str:periodo_id>/resumenes/generar-todos/",
        ResumenGenerarTodosView.as_view(),
        name="resumen-generar-todos",
    ),

    # ─── API REST — Importación CSV ───────────────────────────────────────────
    path(
        "api/importaciones/",
        ImportacionCsvListView.as_view(),
        name="importacion-list",
    ),
    path(
        "api/importaciones/<str:importacion_id>/estado/",
        ImportacionCsvEstadoView.as_view(),
        name="importacion-estado",
    ),
    path(
        "api/importaciones/<str:importacion_id>/",
        ImportacionCsvDetailView.as_view(),
        name="importacion-detail",
    ),

    # ─── API REST — Encuesta ──────────────────────────────────────────────────
    path(
        "api/encuestas/",
        EncuestaListView.as_view(),
        name="encuesta-list",
    ),
    path(
        "api/encuestas/<str:encuesta_id>/",
        EncuestaDetailView.as_view(),
        name="encuesta-detail",
    ),

    # ─── API REST — Snapshot territorial ─────────────────────────────────────
    path(
        "api/snapshots/",
        SnapshotTerritorialListView.as_view(),
        name="snapshot-list",
    ),
    path(
        "api/snapshots/<str:snapshot_id>/",
        SnapshotTerritorialDetailView.as_view(),
        name="snapshot-detail",
    ),

    # ─── API REST — Variación temporal ───────────────────────────────────────
    path(
        "api/variaciones/",
        VariacionTemporalListView.as_view(),
        name="variacion-list",
    ),
    # rutas fijas ANTES de <str:variacion_id> para evitar sombrado
    path(
        "api/variaciones/calcular/",
        VariacionCalcularView.as_view(),
        name="variacion-calcular",
    ),
    path(
        "api/variaciones/calcular-todos/",
        VariacionCalcularTodosView.as_view(),
        name="variacion-calcular-todos",
    ),
    path(
        "api/variaciones/<str:variacion_id>/",
        VariacionTemporalDetailView.as_view(),
        name="variacion-detail",
    ),

    # ─── API REST — Ranking problemática ─────────────────────────────────────
    path(
        "api/rankings/",
        RankingProblematicaListView.as_view(),
        name="ranking-list",
    ),
    # rutas fijas ANTES de <str:ranking_id>
    path(
        "api/rankings/calcular/",
        RankingCalcularView.as_view(),
        name="ranking-calcular",
    ),
    path(
        "api/rankings/calcular-todos/",
        RankingCalcularTodosView.as_view(),
        name="ranking-calcular-todos",
    ),
    path(
        "api/rankings/<str:ranking_id>/",
        RankingProblematicaDetailView.as_view(),
        name="ranking-detail",
    ),

    # ─── API REST — Resultado cruce ───────────────────────────────────────────
    path(
        "api/cruces/",
        ResultadoCruceListView.as_view(),
        name="cruce-list",
    ),
    # rutas fijas ANTES de <str:cruce_id>
    path(
        "api/cruces/calcular/",
        ResultadoCruceCalcularView.as_view(),
        name="cruce-calcular",
    ),
    path(
        "api/cruces/calcular-multiples/",
        ResultadoCruceCalcularMultiplesView.as_view(),
        name="cruce-calcular-multiples",
    ),
    path(
        "api/cruces/periodo/<str:periodo_id>/",
        ResultadoCruceEliminarPeriodoView.as_view(),
        name="cruce-eliminar-periodo",
    ),
    path(
        "api/cruces/<str:cruce_id>/",
        ResultadoCruceDetailView.as_view(),
        name="cruce-detail",
    ),

    # ─── API REST — Caracterización territorial ───────────────────────────────
    path(
        "api/caracterizaciones/",
        CaracterizacionTerritorialListView.as_view(),
        name="caracterizacion-list",
    ),
    path(
        "api/caracterizaciones/<str:caracterizacion_id>/",
        CaracterizacionTerritorialDetailView.as_view(),
        name="caracterizacion-detail",
    ),

    # ─── API REST — Exportación resultado ────────────────────────────────────
    path(
        "api/exportaciones/",
        ExportacionResultadoListView.as_view(),
        name="exportacion-list",
    ),
    # ruta fija ANTES de <str:exportacion_id>
    path(
        "api/exportaciones/exportar/",
        ExportacionResultadoExportarView.as_view(),
        name="exportacion-exportar",
    ),
    path(
        "api/exportaciones/<str:exportacion_id>/",
        ExportacionResultadoDetailView.as_view(),
        name="exportacion-detail",
    ),

    # ─── API REST — Resumen estadístico ──────────────────────────────────────
    path(
        "api/resumenes/",
        ResumenEstadisticoListView.as_view(),
        name="resumen-list",
    ),
    path(
        "api/resumenes/<str:resumen_id>/",
        ResumenEstadisticoDetailView.as_view(),
        name="resumen-detail",
    ),
]