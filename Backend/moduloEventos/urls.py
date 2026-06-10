from django.urls import path
from . import views
from .views import (
    BarrioListView,
    BarrioDetailView,
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
    EventoPuntoInteresListView,
    EventoPuntoInteresDetailView,
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
    # Vistas frontend
    eventos_vista,
    evento_crear_vista,
    evento_detalle_vista,
    evento_editar_vista,
    territorios_vista,
    simpatizantes_vista,
)

urlpatterns = [

    # =========================================================================
    # FRONTEND
    # =========================================================================
    path("", eventos_vista, name="eventos_frontend"),
    path("crear/", evento_crear_vista, name="evento-crear"),
    path("<str:evento_id>/detalle/", evento_detalle_vista, name="evento-detalle"),
    path("<str:evento_id>/editar/", evento_editar_vista, name="evento-editar"),
    path("territorios/", territorios_vista, name="territorios"),
    path("simpatizantes/", simpatizantes_vista, name="simpatizantes"),
    # =========================================================================
    # BARRIOS
    # =========================================================================
    path("api/barrios/", BarrioListView.as_view(), name="barrio-list"),
    path("api/barrios/<str:barrio_id>/", BarrioDetailView.as_view(), name="barrio-detail"),

    # =========================================================================
    # PUNTOS DE INTERÉS
    # =========================================================================
    path("api/puntos/", PuntoInteresListView.as_view(), name="punto-list"),
    path("api/puntos/<str:punto_id>/", PuntoInteresDetailView.as_view(), name="punto-detail"),

    # =========================================================================
    # COORDINADORES
    # =========================================================================
    path("api/coordinadores/", CoordinadorListView.as_view(), name="coordinador-list"),
    path("api/coordinadores/<str:coordinador_id>/", CoordinadorDetailView.as_view(), name="coordinador-detail"),
    path("api/coordinadores/<str:coordinador_id>/password/", CoordinadorPasswordView.as_view(), name="coordinador-password"),

    # =========================================================================
    # SIMPATIZANTES
    # =========================================================================
    path("api/simpatizantes/", SimpatizanteListView.as_view(), name="simpatizante-list"),
    path("api/simpatizantes/<str:simpatizante_id>/", SimpatizanteDetailView.as_view(), name="simpatizante-detail"),

    # =========================================================================
    # HORARIOS
    # =========================================================================
    path("api/simpatizantes/<str:simpatizante_id>/horarios/", HorarioListView.as_view(), name="horario-list"),
    path("api/horarios/<str:horario_id>/", HorarioDetailView.as_view(), name="horario-detail"),
    path("api/<str:evento_id>/disponibles/", DisponiblesParaEventoView.as_view(), name="evento-disponibles"),

    # =========================================================================
    # EVENTOS
    # =========================================================================
    path("api/", EventoListView.as_view(), name="evento-list"),
    path("api/<str:evento_id>/", EventoDetailView.as_view(), name="evento-detail"),
    path("api/<str:evento_id>/estado/", EventoEstadoView.as_view(), name="evento-estado"),
    path("api/<str:evento_id>/tipos/", EventoTipoListView.as_view(), name="evento-tipos"),
    path("api/tipos/<str:tipo_id>/", EventoTipoDetailView.as_view(), name="evento-tipo-detail"),

    # =========================================================================
    # EVENTO PUNTO DE INTERÉS
    # =========================================================================
    path("api/<str:evento_id>/puntos/", EventoPuntoInteresListView.as_view(), name="evento-punto-list"),
    path("api/puntos-evento/<str:relacion_id>/", EventoPuntoInteresDetailView.as_view(), name="evento-punto-detail"),

    # =========================================================================
    # ASIGNACIONES
    # =========================================================================
    path("api/<str:evento_id>/asignaciones/", AsignacionListView.as_view(), name="asignacion-list"),
    path("api/<str:evento_id>/asignaciones/automatica/", AsignacionAutomaticaView.as_view(), name="asignacion-automatica"),
    path("api/asignaciones/<str:asignacion_id>/", AsignacionDetailView.as_view(), name="asignacion-detail"),
    path("api/asignaciones/<str:asignacion_id>/asistencia/", AsistenciaView.as_view(), name="asignacion-asistencia"),
    path("api/<str:evento_id>/participacion-territorial/<str:simpatizante_id>/", ParticipacionTerritorialView.as_view(), name="participacion-territorial"),

    # =========================================================================
    # COBERTURA
    # =========================================================================
    path("api/<str:evento_id>/cobertura/", CoberturaListView.as_view(), name="cobertura-list"),
    path("api/cobertura/<str:cobertura_id>/", CoberturaDetailView.as_view(), name="cobertura-detail"),

    # =========================================================================
    # OBSERVACIONES
    # =========================================================================
    path("api/<str:evento_id>/observaciones/", ObservacionListView.as_view(), name="observacion-list"),
    path("api/observaciones/<str:observacion_id>/", ObservacionDetailView.as_view(), name="observacion-detail"),

    # =========================================================================
    # PARTICIPACIÓN EXTERNA
    # =========================================================================
    path("api/<str:evento_id>/participacion-externa/", ParticipacionExternaView.as_view(), name="participacion-externa"),

    # =========================================================================
    # MATERIAL PUBLICITARIO
    # =========================================================================
    path("api/<str:evento_id>/material/", MaterialPublicitarioView.as_view(), name="material-publicitario"),

    # =========================================================================
    # ESTADO MATERIAL
    # =========================================================================
    path("api/<str:evento_id>/material/estado/", EstadoMaterialListView.as_view(), name="estado-material-list"),
    path("api/material/estado/csv/", EstadoMaterialCSVView.as_view(), name="estado-material-csv"),
    path("api/<str:evento_id>/material/estado/promedio/", PromedioEstadoMaterialView.as_view(), name="estado-material-promedio"),

    # =========================================================================
    # AUDITORÍA
    # =========================================================================
    path("api/auditoria/", AuditoriaView.as_view(), name="auditoria"),
]