import uuid
from django.db import models


# =============================================================================
# CATÁLOGOS  (PK = integer codigo, sin UUID)
# =============================================================================

class CatalogoOcupacion(models.Model):
    codigo      = models.IntegerField(primary_key=True)
    descripcion = models.CharField(max_length=255)

    class Meta:
        managed  = False
        db_table = 'estadistico_territorial\".\"catalogo_ocupacion'

    def __str__(self):
        return self.descripcion


class CatalogoInclinacionVoto(models.Model):
    codigo      = models.IntegerField(primary_key=True)
    descripcion = models.CharField(max_length=255)

    class Meta:
        managed  = False
        db_table = 'estadistico_territorial\".\"catalogo_inclinacion_voto'

    def __str__(self):
        return self.descripcion


class CatalogoIntencionParticipacion(models.Model):
    codigo      = models.IntegerField(primary_key=True)
    descripcion = models.CharField(max_length=255)

    class Meta:
        managed  = False
        db_table = 'estadistico_territorial\".\"catalogo_intencion_participacion'

    def __str__(self):
        return self.descripcion


class CatalogoProblematica(models.Model):
    codigo      = models.IntegerField(primary_key=True)
    descripcion = models.CharField(max_length=255)

    class Meta:
        managed  = False
        db_table = 'estadistico_territorial\".\"catalogo_problematica'

    def __str__(self):
        return self.descripcion


# =============================================================================
# RANGO DE EDAD
# =============================================================================

class RangoEdad(models.Model):
    id       = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    etiqueta = models.CharField(max_length=100)
    edad_min = models.IntegerField()
    edad_max = models.IntegerField()

    class Meta:
        managed  = False
        db_table = 'estadistico_territorial\".\"rango_edad'

    def __str__(self):
        return self.etiqueta


# =============================================================================
# PERIODO ESTADÍSTICO
# =============================================================================

class PeriodoEstadistico(models.Model):
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    etiqueta     = models.CharField(max_length=150)
    fecha_inicio = models.DateField()
    fecha_fin    = models.DateField()

    class Meta:
        managed  = False
        db_table = 'estadistico_territorial\".\"periodo_estadistico'

    def __str__(self):
        return self.etiqueta


# =============================================================================
# IMPORTACIÓN CSV
# =============================================================================

class ImportacionCsv(models.Model):
    id                  = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre_archivo      = models.CharField(max_length=255)
    fecha_importacion   = models.DateField(auto_now_add=True)
    procesado_en        = models.DateTimeField(null=True, blank=True)
    estado              = models.CharField(max_length=50, default='PENDIENTE')
    total_registros     = models.IntegerField(default=0)
    registros_validos   = models.IntegerField(default=0)
    registros_invalidos = models.IntegerField(default=0)
    errores_detalle     = models.TextField(null=True, blank=True)

    class Meta:
        managed  = False
        db_table = 'estadistico_territorial\".\"importacion_csv'

    def __str__(self):
        return self.nombre_archivo


# =============================================================================
# ENCUESTA
# =============================================================================

class Encuesta(models.Model):
    id                          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    importacion                 = models.ForeignKey(
                                    ImportacionCsv,
                                    on_delete=models.CASCADE,
                                    db_column='importacion_id',
                                    related_name='encuestas',
                                  )
    fecha                       = models.DateField()
    edad                        = models.IntegerField()
    barrio                      = models.CharField(max_length=255, null=True, blank=True)
    # barrio_id referencia a gestion_eventos.barrio; se guarda como UUID puro
    # para evitar dependencia circular entre esquemas.
    barrio_id                   = models.UUIDField(null=True, blank=True, db_index=True)
    ocupacion_cod               = models.ForeignKey(
                                    CatalogoOcupacion,
                                    null=True, blank=True,
                                    on_delete=models.SET_NULL,
                                    db_column='ocupacion_cod',
                                    related_name='+',
                                  )
    inclinacion_voto_cod        = models.ForeignKey(
                                    CatalogoInclinacionVoto,
                                    null=True, blank=True,
                                    on_delete=models.SET_NULL,
                                    db_column='inclinacion_voto_cod',
                                    related_name='+',
                                  )
    intencion_participacion_cod = models.ForeignKey(
                                    CatalogoIntencionParticipacion,
                                    null=True, blank=True,
                                    on_delete=models.SET_NULL,
                                    db_column='intencion_participacion_cod',
                                    related_name='+',
                                  )
    prob_1_cod                  = models.ForeignKey(
                                    CatalogoProblematica,
                                    null=True, blank=True,
                                    on_delete=models.SET_NULL,
                                    db_column='prob_1_cod',
                                    related_name='encuestas_prob1',
                                  )
    prob_2_cod                  = models.ForeignKey(
                                    CatalogoProblematica,
                                    null=True, blank=True,
                                    on_delete=models.SET_NULL,
                                    db_column='prob_2_cod',
                                    related_name='encuestas_prob2',
                                  )
    prob_otra                   = models.CharField(max_length=500, null=True, blank=True)
    opinion_politica            = models.TextField(null=True, blank=True)

    class Meta:
        managed  = False
        db_table = 'estadistico_territorial\".\"encuesta'

    def __str__(self):
        return f"Encuesta {self.id} – {self.fecha}"


# =============================================================================
# SNAPSHOT TERRITORIAL
# =============================================================================

class SnapshotTerritorial(models.Model):
    id                     = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # barrio_id referencia a gestion_eventos.barrio (esquema externo)
    barrio_id              = models.UUIDField(db_index=True)
    periodo                = models.ForeignKey(
                               PeriodoEstadistico,
                               on_delete=models.CASCADE,
                               db_column='periodo_id',
                               related_name='snapshots',
                             )
    total_simpatizantes    = models.IntegerField(default=0)
    total_indecisos        = models.IntegerField(default=0)
    total_no_simpatizantes = models.IntegerField(default=0)
    total_no_votantes      = models.IntegerField(default=0)
    pct_simpatizantes      = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    pct_indecisos          = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    pct_no_simpatizantes   = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    pct_no_votantes        = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    total_intension_votar  = models.IntegerField(default=0)
    total_abstencion       = models.IntegerField(default=0)
    pct_participacion      = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    indice_intervencion    = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    generado_en            = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed  = False
        db_table = 'estadistico_territorial\".\"snapshot_territorial'

    def __str__(self):
        return f"Snapshot barrio={self.barrio_id} periodo={self.periodo_id}"


# =============================================================================
# VARIACIÓN TEMPORAL
# =============================================================================

class VariacionTemporal(models.Model):
    id                         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # barrio_id referencia a gestion_eventos.barrio (esquema externo)
    barrio_id                  = models.UUIDField(db_index=True)
    periodo_anterior           = models.ForeignKey(
                                   PeriodoEstadistico,
                                   on_delete=models.CASCADE,
                                   db_column='periodo_anterior_id',
                                   related_name='variaciones_como_anterior',
                                 )
    periodo_actual             = models.ForeignKey(
                                   PeriodoEstadistico,
                                   on_delete=models.CASCADE,
                                   db_column='periodo_actual_id',
                                   related_name='variaciones_como_actual',
                                 )
    variacion_simpatizantes    = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    variacion_indecisos        = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    variacion_no_simpatizantes = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    variacion_participacion    = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    cambio_significativo       = models.BooleanField(default=False)

    class Meta:
        managed  = False
        db_table = 'estadistico_territorial\".\"variacion_temporal'

    def __str__(self):
        return f"Variación barrio={self.barrio_id} ({self.periodo_anterior_id} → {self.periodo_actual_id})"


# =============================================================================
# RANKING PROBLEMÁTICA
# =============================================================================

class RankingProblematica(models.Model):
    id               = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    periodo          = models.ForeignKey(
                         PeriodoEstadistico,
                         on_delete=models.CASCADE,
                         db_column='periodo_id',
                         related_name='rankings_problematica',
                       )
    # barrio_id referencia a gestion_eventos.barrio (esquema externo)
    barrio_id        = models.UUIDField(db_index=True)
    problematica_cod = models.ForeignKey(
                         CatalogoProblematica,
                         on_delete=models.RESTRICT,
                         db_column='problematica_cod',
                         related_name='rankings',
                       )
    frecuencia       = models.IntegerField(default=0)
    pct_frecuencia   = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    posicion_ranking = models.IntegerField()

    class Meta:
        managed  = False
        db_table = 'estadistico_territorial\".\"ranking_problematica'

    def __str__(self):
        return f"Ranking pos={self.posicion_ranking} barrio={self.barrio_id}"


# =============================================================================
# RESULTADO CRUCE
# =============================================================================

class ResultadoCruce(models.Model):
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    periodo     = models.ForeignKey(
                    PeriodoEstadistico,
                    on_delete=models.CASCADE,
                    db_column='periodo_id',
                    related_name='resultados_cruce',
                  )
    dimension_a = models.CharField(max_length=100)
    valor_a     = models.CharField(max_length=255)
    dimension_b = models.CharField(max_length=100)
    valor_b     = models.CharField(max_length=255)
    cantidad    = models.IntegerField(default=0)
    porcentaje  = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    generado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed  = False
        db_table = 'estadistico_territorial\".\"resultado_cruce'

    def __str__(self):
        return f"Cruce {self.dimension_a}×{self.dimension_b} periodo={self.periodo_id}"


# =============================================================================
# CARACTERIZACIÓN TERRITORIAL
# =============================================================================

class CaracterizacionTerritorial(models.Model):
    id                            = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # barrio_id referencia a gestion_eventos.barrio (esquema externo)
    barrio_id                     = models.UUIDField(db_index=True)
    periodo                       = models.ForeignKey(
                                      PeriodoEstadistico,
                                      on_delete=models.CASCADE,
                                      db_column='periodo_id',
                                      related_name='caracterizaciones',
                                    )
    afinidad_predominante         = models.CharField(max_length=100, null=True, blank=True)
    ocupacion_predominante        = models.CharField(max_length=100, null=True, blank=True)
    problematica_predominante_cod = models.ForeignKey(
                                      CatalogoProblematica,
                                      null=True, blank=True,
                                      on_delete=models.SET_NULL,
                                      db_column='problematica_predominante_cod',
                                      related_name='caracterizaciones',
                                    )
    participacion_predominante    = models.CharField(max_length=100, null=True, blank=True)
    pct_indecision                = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    pct_apoyo                     = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    cantidad_eventos              = models.IntegerField(default=0)
    frecuencia_problematicas      = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    es_prioritario                = models.BooleanField(default=False)
    alto_potencial_crecimiento    = models.BooleanField(default=False)
    generado_en                   = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed  = False
        db_table = 'estadistico_territorial\".\"caracterizacion_territorial'

    def __str__(self):
        return f"Caracterización barrio={self.barrio_id} periodo={self.periodo_id}"


# =============================================================================
# EXPORTACIÓN RESULTADO
# =============================================================================

class ExportacionResultado(models.Model):
    id             = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    periodo        = models.ForeignKey(
                       PeriodoEstadistico,
                       on_delete=models.CASCADE,
                       db_column='periodo_id',
                       related_name='exportaciones',
                     )
    tipo_analisis  = models.CharField(max_length=100)
    formato        = models.CharField(max_length=50)
    ruta_archivo   = models.CharField(max_length=500)
    generado_en    = models.DateTimeField(auto_now_add=True)
    # coordinador_id referencia a gestion_eventos.coordinador (esquema externo)
    coordinador_id = models.UUIDField(null=True, blank=True)

    class Meta:
        managed  = False
        db_table = 'estadistico_territorial\".\"exportacion_resultado'

    def __str__(self):
        return f"{self.tipo_analisis} ({self.formato}) – {self.generado_en:%Y-%m-%d}"


# =============================================================================
# RESUMEN ESTADÍSTICO
# =============================================================================

class ResumenEstadistico(models.Model):
    id            = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    periodo       = models.ForeignKey(
                      PeriodoEstadistico,
                      on_delete=models.CASCADE,
                      db_column='periodo_id',
                      related_name='resumenes',
                    )
    # barrio_id referencia a gestion_eventos.barrio (esquema externo)
    barrio_id     = models.UUIDField(db_index=True)
    resumen_texto = models.TextField()
    generado_en   = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed  = False
        db_table = 'estadistico_territorial\".\"resumen_estadistico'

    def __str__(self):
        return f"Resumen barrio={self.barrio_id} periodo={self.periodo_id}"