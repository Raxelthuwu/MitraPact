from django.urls import path
from backend.moduloEventos import views

app_name = 'eventos'

urlpatterns = [

    # -------------------------------------------------------------------------
    # EVENTOS
    # -------------------------------------------------------------------------
    path('', views.evento_lista, name='evento_lista'),
    path('crear/', views.evento_crear, name='evento_crear'),
    path('<uuid:pk>/', views.evento_detalle, name='evento_detalle'),
    path('<uuid:pk>/editar/', views.evento_editar, name='evento_editar'),

    # -------------------------------------------------------------------------
    # TIPOS DE EVENTO
    # -------------------------------------------------------------------------
    path('<uuid:evento_pk>/tipos/agregar/', views.evento_tipo_agregar, name='evento_tipo_agregar'),
    path('tipos/<uuid:pk>/eliminar/', views.evento_tipo_eliminar, name='evento_tipo_eliminar'),

    # -------------------------------------------------------------------------
    # ASIGNACIÓN DE PERSONAL
    # -------------------------------------------------------------------------
    path('<uuid:evento_pk>/asignaciones/', views.asignacion_lista, name='asignacion_lista'),
    path('<uuid:evento_pk>/asignaciones/manual/', views.asignacion_manual, name='asignacion_manual'),
    path('<uuid:evento_pk>/asignaciones/automatica/', views.asignacion_automatica, name='asignacion_automatica'),
    path('asignaciones/<uuid:pk>/editar/', views.asignacion_editar, name='asignacion_editar'),
    path('asignaciones/<uuid:pk>/eliminar/', views.asignacion_eliminar, name='asignacion_eliminar'),

    # -------------------------------------------------------------------------
    # COBERTURA
    # -------------------------------------------------------------------------
    path('<uuid:evento_pk>/cobertura/', views.cobertura_lista, name='cobertura_lista'),
    path('<uuid:evento_pk>/cobertura/agregar/', views.cobertura_agregar, name='cobertura_agregar'),
    path('cobertura/<uuid:pk>/eliminar/', views.cobertura_eliminar, name='cobertura_eliminar'),

    # -------------------------------------------------------------------------
    # REGISTRO OPERATIVO
    # -------------------------------------------------------------------------
    path('<uuid:evento_pk>/observaciones/agregar/', views.observacion_agregar, name='observacion_agregar'),
    path('<uuid:evento_pk>/asistencia/', views.asistencia_registrar, name='asistencia_registrar'),
    path('<uuid:evento_pk>/participacion-externa/', views.participacion_externa_registrar, name='participacion_externa_registrar'),

    # -------------------------------------------------------------------------
    # MATERIAL PUBLICITARIO
    # -------------------------------------------------------------------------
    path('<uuid:evento_pk>/material/', views.material_detalle, name='material_detalle'),
    path('<uuid:evento_pk>/material/registrar/', views.material_registrar, name='material_registrar'),
    path('<uuid:evento_pk>/material/estado/registrar/', views.estado_material_registrar, name='estado_material_registrar'),
    path('<uuid:evento_pk>/material/estado/cargar-csv/', views.estado_material_cargar_csv, name='estado_material_cargar_csv'),

    # -------------------------------------------------------------------------
    # DISPONIBILIDAD DE SIMPATIZANTES
    # -------------------------------------------------------------------------
    path('<uuid:evento_pk>/disponibilidad/', views.consultar_disponibilidad, name='consultar_disponibilidad'),
]