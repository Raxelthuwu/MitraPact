import logging
from django.db import connection

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

logging.info("[DbTables] Inicializando mapeo de tablas de la base de datos...")

# ESQUEMAS

# busqueda_semantica
logging.info("[DbTables] Cargando esquema: 'busqueda_semantica'...")
documento               = 'busqueda_semantica.documento'
fragmento               = 'busqueda_semantica.fragmento'
opinion_clasificada     = 'busqueda_semantica.opinion_clasificada'
argumento               = 'busqueda_semantica.argumento'
argumento_documento     = 'busqueda_semantica.argumento_documento'
tema_documento          = 'busqueda_semantica.tema_documento'

# estadistico_territorial
logging.info("[DbTables] Cargando esquema: 'estadistico_territorial'...")
catalogo_ocupacion                = 'estadistico_territorial.catalogo_ocupacion'
catalogo_inclinacion_voto         = 'estadistico_territorial.catalogo_inclinacion_voto'
catalogo_intencion_participacion  = 'estadistico_territorial.catalogo_intencion_participacion'
catalogo_problematica             = 'estadistico_territorial.catalogo_problematica'
rango_edad                        = 'estadistico_territorial.rango_edad'
periodo_estadistico               = 'estadistico_territorial.periodo_estadistico'
importacion_csv                   = 'estadistico_territorial.importacion_csv'
encuesta                          = 'estadistico_territorial.encuesta'
snapshot_territorial              = 'estadistico_territorial.snapshot_territorial'
variacion_temporal                = 'estadistico_territorial.variacion_temporal'
ranking_problematica              = 'estadistico_territorial.ranking_problematica'
resultado_cruce                   = 'estadistico_territorial.resultado_cruce'
caracterizacion_territorial       = 'estadistico_territorial.caracterizacion_territorial'
exportacion_resultado             = 'estadistico_territorial.exportacion_resultado'
resumen_estadistico               = 'estadistico_territorial.resumen_estadistico'

# gestion_eventos
logging.info("[DbTables] Cargando esquema: 'gestion_eventos'...")
barrio                  = 'gestion_eventos.barrio'
punto_interes           = 'gestion_eventos.punto_interes'        # barrio_id directo (sector eliminado)
coordinador             = 'gestion_eventos.coordinador'
simpatizante            = 'gestion_eventos.simpatizante'
horario_disponible      = 'gestion_eventos.horario_disponible'
evento                  = 'gestion_eventos.evento'
evento_punto_interes    = 'gestion_eventos.evento_punto_interes'  # nueva — N:M evento <-> punto_interes
evento_tipo             = 'gestion_eventos.evento_tipo'
asignacion              = 'gestion_eventos.asignacion'
cobertura               = 'gestion_eventos.cobertura'
observacion             = 'gestion_eventos.observacion'
participacion_externa   = 'gestion_eventos.participacion_externa'
material_publicitario   = 'gestion_eventos.material_publicitario'
estado_material         = 'gestion_eventos.estado_material'
auditoria               = 'gestion_eventos.auditoria'

logging.info("[DbTables] Mapeo de tablas cargado exitosamente en memoria.")