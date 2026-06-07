from django.urls import path
from .views import (
    # Catálogos
    CatalogoOcupacionView,
    CatalogoInclinacionVotoView,
    CatalogoIntencionParticipacionView,
    CatalogoProblematicaView,
    # Rango de edad
    RangoEdadListView,
    RangoEdadDetailView,
    # Período estadístico
    PeriodoListView,
    PeriodoDetailView,
    # Importación CSV
    ImportacionListView,
    ImportacionUploadView,
    ImportacionDetailView,
    # Encuesta
    EncuestaListView,
    EncuestaDetailView,
    # Snapshot territorial
    SnapshotListView,
    SnapshotDetailView,
    SnapshotGenerarView,
    SnapshotGenerarTodosView,
    # Variación temporal
    VariacionListView,
    VariacionDetailView,
    VariacionCalcularView,
    VariacionCalcularTodosView,
    # Ranking problemática
    RankingListView,
    RankingDetailView,
    RankingCalcularView,
    RankingCalcularTodosView,
    # Resultado cruce
    CruceListView,
    CruceDetailView,
    CruceCalcularView,
    CruceCalcularMultiplesView,
    CruceEliminarPeriodoView,
    # Caracterización territorial
    CaracterizacionListView,
    CaracterizacionDetailView,
    CaracterizacionGenerarView,
    CaracterizacionGenerarTodosView,
    # Exportación
    ExportacionListView,
    ExportacionDetailView,
    ExportacionGenerarView,
    # Resumen estadístico
    ResumenListView,
    ResumenDetailView,
    ResumenGenerarView,
    ResumenGenerarTodosView,
)

urlpatterns = [

    # =========================================================================
    # CATÁLOGOS  (solo lectura — RF-EST-03, 06, 08, 11)
    # =========================================================================
    path(
        "catalogos/ocupacion/",
        CatalogoOcupacionView.as_view(),
        name="catalogo-ocupacion",
    ),
    path(
        "catalogos/inclinacion-voto/",
        CatalogoInclinacionVotoView.as_view(),
        name="catalogo-inclinacion-voto",
    ),
    path(
        "catalogos/intencion-participacion/",
        CatalogoIntencionParticipacionView.as_view(),
        name="catalogo-intencion-participacion",
    ),
    path(
        "catalogos/problematica/",
        CatalogoProblematicaView.as_view(),
        name="catalogo-problematica",
    ),

    # =========================================================================
    # RANGOS DE EDAD  (RF-EST-36, 37, 38)
    # =========================================================================
    path(
        "rangos-edad/",
        RangoEdadListView.as_view(),
        name="rango-edad-list",
    ),
    path(
        "rangos-edad/<str:rango_id>/",
        RangoEdadDetailView.as_view(),
        name="rango-edad-detail",
    ),

    # =========================================================================
    # PERÍODOS ESTADÍSTICOS  (RF-EST-05, 33)
    # =========================================================================
    path(
        "periodos/",
        PeriodoListView.as_view(),
        name="periodo-list",
    ),
    path(
        "periodos/<str:periodo_id>/",
        PeriodoDetailView.as_view(),
        name="periodo-detail",
    ),

    # =========================================================================
    # IMPORTACIÓN CSV  (RF-EST-01, 02)
    # =========================================================================
    path(
        "importaciones/",
        ImportacionListView.as_view(),
        name="importacion-list",
    ),
    path(
        "importaciones/upload/",
        ImportacionUploadView.as_view(),
        name="importacion-upload",
    ),
    path(
        "importaciones/<str:importacion_id>/",
        ImportacionDetailView.as_view(),
        name="importacion-detail",
    ),

    # =========================================================================
    # ENCUESTAS  (RF-EST-03 al 07, 11)
    # Filtros vía query params: ?importacion_id= | ?barrio_id= | ?periodo_id=
    # =========================================================================
    path(
        "encuestas/",
        EncuestaListView.as_view(),
        name="encuesta-list",
    ),
    path(
        "encuestas/<str:encuesta_id>/",
        EncuestaDetailView.as_view(),
        name="encuesta-detail",
    ),

    # =========================================================================
    # SNAPSHOTS TERRITORIALES  (RF-EST-03, 04, 06, 07, 35)
    # Filtros: ?barrio_id= | ?periodo_id=
    # =========================================================================
    path(
        "snapshots/",
        SnapshotListView.as_view(),
        name="snapshot-list",
    ),
    path(
        "snapshots/generar/",
        SnapshotGenerarView.as_view(),
        name="snapshot-generar",
    ),
    path(
        "snapshots/generar-todos/",
        SnapshotGenerarTodosView.as_view(),
        name="snapshot-generar-todos",
    ),
    path(
        "snapshots/<str:snapshot_id>/",
        SnapshotDetailView.as_view(),
        name="snapshot-detail",
    ),

    # =========================================================================
    # VARIACIÓN TEMPORAL  (RF-EST-05, 33)
    # Filtros: ?barrio_id= | ?periodo_actual_id=
    # =========================================================================
    path(
        "variaciones/",
        VariacionListView.as_view(),
        name="variacion-list",
    ),
    path(
        "variaciones/calcular/",
        VariacionCalcularView.as_view(),
        name="variacion-calcular",
    ),
    path(
        "variaciones/calcular-todos/",
        VariacionCalcularTodosView.as_view(),
        name="variacion-calcular-todos",
    ),
    path(
        "variaciones/<str:variacion_id>/",
        VariacionDetailView.as_view(),
        name="variacion-detail",
    ),

    # =========================================================================
    # RANKING PROBLEMÁTICA  (RF-EST-08, 09, 10, 19)
    # Filtros: ?periodo_id= | ?barrio_id=
    # =========================================================================
    path(
        "rankings/",
        RankingListView.as_view(),
        name="ranking-list",
    ),
    path(
        "rankings/calcular/",
        RankingCalcularView.as_view(),
        name="ranking-calcular",
    ),
    path(
        "rankings/calcular-todos/",
        RankingCalcularTodosView.as_view(),
        name="ranking-calcular-todos",
    ),
    path(
        "rankings/<str:ranking_id>/",
        RankingDetailView.as_view(),
        name="ranking-detail",
    ),

    # =========================================================================
    # CRUCES  (RF-EST-12, 13, 18, 20, 30, 31, 36, 37)
    # GET requiere ?periodo_id=
    # =========================================================================
    path(
        "cruces/",
        CruceListView.as_view(),
        name="cruce-list",
    ),
    path(
        "cruces/calcular/",
        CruceCalcularView.as_view(),
        name="cruce-calcular",
    ),
    path(
        "cruces/calcular-multiples/",
        CruceCalcularMultiplesView.as_view(),
        name="cruce-calcular-multiples",
    ),
    path(
        "cruces/periodo/<str:periodo_id>/",
        CruceEliminarPeriodoView.as_view(),
        name="cruce-eliminar-periodo",
    ),
    path(
        "cruces/<str:cruce_id>/",
        CruceDetailView.as_view(),
        name="cruce-detail",
    ),

    # =========================================================================
    # CARACTERIZACIÓN TERRITORIAL
    # (RF-EST-21, 22, 23, 27, 28, 29, 32, 35)
    # Filtros: ?barrio_id= | ?periodo_id=
    # =========================================================================
    path(
        "caracterizaciones/",
        CaracterizacionListView.as_view(),
        name="caracterizacion-list",
    ),
    path(
        "caracterizaciones/generar/",
        CaracterizacionGenerarView.as_view(),
        name="caracterizacion-generar",
    ),
    path(
        "caracterizaciones/generar-todos/",
        CaracterizacionGenerarTodosView.as_view(),
        name="caracterizacion-generar-todos",
    ),
    path(
        "caracterizaciones/<str:caracterizacion_id>/",
        CaracterizacionDetailView.as_view(),
        name="caracterizacion-detail",
    ),

    # =========================================================================
    # EXPORTACIÓN  (RF-EST-26)
    # Filtro GET: ?periodo_id=
    # =========================================================================
    path(
        "exportaciones/",
        ExportacionListView.as_view(),
        name="exportacion-list",
    ),
    path(
        "exportaciones/generar/",
        ExportacionGenerarView.as_view(),
        name="exportacion-generar",
    ),
    path(
        "exportaciones/<str:exportacion_id>/",
        ExportacionDetailView.as_view(),
        name="exportacion-detail",
    ),

    # =========================================================================
    # RESUMEN ESTADÍSTICO  (RF-EST-34)
    # Filtros: ?barrio_id= | ?periodo_id=
    # =========================================================================
    path(
        "resumenes/",
        ResumenListView.as_view(),
        name="resumen-list",
    ),
    path(
        "resumenes/generar/",
        ResumenGenerarView.as_view(),
        name="resumen-generar",
    ),
    path(
        "resumenes/generar-todos/",
        ResumenGenerarTodosView.as_view(),
        name="resumen-generar-todos",
    ),
    path(
        "resumenes/<str:resumen_id>/",
        ResumenDetailView.as_view(),
        name="resumen-detail",
    ),
]