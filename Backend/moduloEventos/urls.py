from django.urls import path

from .views import (
    BarrioListView,
    BarrioDetailView,

    SectorListView,
    SectorDetailView,

    PuntoInteresListView,
    PuntoInteresDetailView,

    CoordinadorListView,
    CoordinadorDetailView,
    CoordinadorPasswordView,

    SimpatizanteListView,
    SimpatizanteDetailView,

    HorarioListView,
    HorarioDetailView,
    DisponiblesParaEventoView,

    EventoListView,
    EventoDetailView,
    EventoEstadoView,
    EventoTipoListView,
    EventoTipoDetailView,

    AsignacionListView,
    AsignacionAutomaticaView,
    AsignacionDetailView,
    AsistenciaView,
    ParticipacionTerritorialView,

    CoberturaListView,
    CoberturaDetailView,

    ObservacionListView,
    ObservacionDetailView,

    ParticipacionExternaView,

    MaterialPublicitarioView,

    EstadoMaterialListView,
    EstadoMaterialCSVView,
    PromedioEstadoMaterialView,

    AuditoriaView,
)

urlpatterns = [

    # =========================================================================
    # BARRIOS
    # =========================================================================

    path(
        "barrios/",
        BarrioListView.as_view(),
        name="barrio-list"
    ),

    path(
        "barrios/<str:barrio_id>/",
        BarrioDetailView.as_view(),
        name="barrio-detail"
    ),

    # =========================================================================
    # SECTORES
    # =========================================================================

    path(
        "sectores/",
        SectorListView.as_view(),
        name="sector-list"
    ),

    path(
        "sectores/<str:sector_id>/",
        SectorDetailView.as_view(),
        name="sector-detail"
    ),

    # =========================================================================
    # PUNTOS DE INTERÉS
    # =========================================================================

    path(
        "puntos/",
        PuntoInteresListView.as_view(),
        name="punto-list"
    ),

    path(
        "puntos/<str:punto_id>/",
        PuntoInteresDetailView.as_view(),
        name="punto-detail"
    ),

    # =========================================================================
    # COORDINADORES
    # =========================================================================

    path(
        "coordinadores/",
        CoordinadorListView.as_view(),
        name="coordinador-list"
    ),

    path(
        "coordinadores/<str:coordinador_id>/",
        CoordinadorDetailView.as_view(),
        name="coordinador-detail"
    ),

    path(
        "coordinadores/<str:coordinador_id>/password/",
        CoordinadorPasswordView.as_view(),
        name="coordinador-password"
    ),

    # =========================================================================
    # SIMPATIZANTES
    # =========================================================================

    path(
        "simpatizantes/",
        SimpatizanteListView.as_view(),
        name="simpatizante-list"
    ),

    path(
        "simpatizantes/<str:simpatizante_id>/",
        SimpatizanteDetailView.as_view(),
        name="simpatizante-detail"
    ),

    # =========================================================================
    # HORARIOS
    # =========================================================================

    path(
        "simpatizantes/<str:simpatizante_id>/horarios/",
        HorarioListView.as_view(),
        name="horario-list"
    ),

    path(
        "horarios/<str:horario_id>/",
        HorarioDetailView.as_view(),
        name="horario-detail"
    ),

    path(
        "<str:evento_id>/disponibles/",
        DisponiblesParaEventoView.as_view(),
        name="evento-disponibles"
    ),

    # =========================================================================
    # EVENTOS
    # =========================================================================

    path(
        "",
        EventoListView.as_view(),
        name="evento-list"
    ),

    path(
        "<str:evento_id>/",
        EventoDetailView.as_view(),
        name="evento-detail"
    ),

    path(
        "<str:evento_id>/estado/",
        EventoEstadoView.as_view(),
        name="evento-estado"
    ),

    path(
        "<str:evento_id>/tipos/",
        EventoTipoListView.as_view(),
        name="evento-tipos"
    ),

    path(
        "tipos/<str:tipo_id>/",
        EventoTipoDetailView.as_view(),
        name="evento-tipo-detail"
    ),

    # =========================================================================
    # ASIGNACIONES
    # =========================================================================

    path(
        "<str:evento_id>/asignaciones/",
        AsignacionListView.as_view(),
        name="asignacion-list"
    ),

    path(
        "<str:evento_id>/asignaciones/automatica/",
        AsignacionAutomaticaView.as_view(),
        name="asignacion-automatica"
    ),

    path(
        "asignaciones/<str:asignacion_id>/",
        AsignacionDetailView.as_view(),
        name="asignacion-detail"
    ),

    path(
        "asignaciones/<str:asignacion_id>/asistencia/",
        AsistenciaView.as_view(),
        name="asignacion-asistencia"
    ),

    path(
        "<str:evento_id>/participacion-territorial/<str:simpatizante_id>/",
        ParticipacionTerritorialView.as_view(),
        name="participacion-territorial"
    ),

    # =========================================================================
    # COBERTURA
    # =========================================================================

    path(
        "<str:evento_id>/cobertura/",
        CoberturaListView.as_view(),
        name="cobertura-list"
    ),

    path(
        "cobertura/<str:cobertura_id>/",
        CoberturaDetailView.as_view(),
        name="cobertura-detail"
    ),

    # =========================================================================
    # OBSERVACIONES
    # =========================================================================

    path(
        "<str:evento_id>/observaciones/",
        ObservacionListView.as_view(),
        name="observacion-list"
    ),

    path(
        "observaciones/<str:observacion_id>/",
        ObservacionDetailView.as_view(),
        name="observacion-detail"
    ),

    # =========================================================================
    # PARTICIPACIÓN EXTERNA
    # =========================================================================

    path(
        "<str:evento_id>/participacion-externa/",
        ParticipacionExternaView.as_view(),
        name="participacion-externa"
    ),

    # =========================================================================
    # MATERIAL PUBLICITARIO
    # =========================================================================

    path(
        "<str:evento_id>/material/",
        MaterialPublicitarioView.as_view(),
        name="material-publicitario"
    ),

    # =========================================================================
    # ESTADO MATERIAL
    # =========================================================================

    path(
        "<str:evento_id>/material/estado/",
        EstadoMaterialListView.as_view(),
        name="estado-material-list"
    ),

    path(
        "material/estado/csv/",
        EstadoMaterialCSVView.as_view(),
        name="estado-material-csv"
    ),

    path(
        "<str:evento_id>/material/estado/promedio/",
        PromedioEstadoMaterialView.as_view(),
        name="estado-material-promedio"
    ),

    # =========================================================================
    # AUDITORÍA
    # =========================================================================

    path(
        "auditoria/",
        AuditoriaView.as_view(),
        name="auditoria"
    ),
]