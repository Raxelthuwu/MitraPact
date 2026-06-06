import uuid
from django.db import models


# =============================================================================
# BARRIO
# =============================================================================
class Barrio(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=255, unique=True)

    class Meta:
        managed = False
        db_table = 'barrio' # Esquema manejado mediante search_path para evitar errores de escape
        verbose_name = "Barrio"
        verbose_name_plural = "Barrios"

    def __str__(self):
        return self.nombre


# =============================================================================
# SECTOR
# =============================================================================
class Sector(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=255)
    barrio = models.ForeignKey(
        Barrio,
        on_delete=models.CASCADE,
        related_name="sectores",
        db_column="barrio_id",
    )

    class Meta:
        managed = False
        db_table = 'sector'
        verbose_name = "Sector"
        verbose_name_plural = "Sectores"

    def __str__(self):
        return f"{self.nombre} ({self.barrio.nombre})"


# =============================================================================
# PUNTO_INTERES
# =============================================================================
class PuntoInteres(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=255)
    sector = models.ForeignKey(
        Sector,
        on_delete=models.CASCADE,
        related_name="puntos_interes",
        db_column="sector_id",
    )

    class Meta:
        managed = False
        db_table = 'punto_interes'
        verbose_name = "Punto de Interés"
        verbose_name_plural = "Puntos de Interés"

    def __str__(self):
        return self.nombre


# =============================================================================
# COORDINADOR
# =============================================================================
class Coordinador(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=255)
    email = models.CharField(max_length=255, unique=True)
    password_hash = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'coordinador'
        verbose_name = "Coordinador"
        verbose_name_plural = "Coordinadores"

    def __str__(self):
        return self.nombre


# =============================================================================
# SIMPATIZANTE
# =============================================================================
class Simpatizante(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=255)
    cedula = models.CharField(max_length=50, unique=True)
    telefono = models.CharField(max_length=50, null=True, blank=True)
    edad = models.IntegerField()
    ocupacion = models.CharField(max_length=255)
    lugar_votacion = models.CharField(max_length=255)
    puesto_votacion = models.CharField(max_length=255)
    mesa_votacion = models.CharField(max_length=100)
    opinion_politica = models.TextField(null=True, blank=True)
    barrio = models.ForeignKey(
        Barrio,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="simpatizantes",
        db_column="barrio_id",
    )

    class Meta:
        managed = False
        db_table = 'simpatizante'
        verbose_name = "Simpatizante"
        verbose_name_plural = "Simpatizantes"

    def __str__(self):
        return f"{self.nombre} ({self.cedula})"


# =============================================================================
# HORARIO_DISPONIBLE
# =============================================================================
class HorarioDisponible(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    simpatizante = models.ForeignKey(
        Simpatizante,
        on_delete=models.CASCADE,
        related_name="horarios",
        db_column="simpatizante_id",
    )
    dia_semana = models.CharField(max_length=20)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    class Meta:
        managed = False
        db_table = 'horario_disponible'
        verbose_name = "Horario Disponible"
        verbose_name_plural = "Horarios Disponibles"

    def __str__(self):
        return f"{self.simpatizante.nombre} — {self.dia_semana} {self.hora_inicio}–{self.hora_fin}"


# =============================================================================
# EVENTO
# =============================================================================
class Evento(models.Model):

    class Estado(models.TextChoices):
        PLANIFICADO = "PLANIFICADO", "Planificado"
        EN_EJECUCION = "EN_EJECUCION", "En ejecución"
        FINALIZADO = "FINALIZADO", "Finalizado"
        CANCELADO = "CANCELADO", "Cancelado"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(null=True, blank=True)
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    duracion_min = models.IntegerField(null=True, blank=True)
    objetivo = models.TextField(null=True, blank=True)
    resultado_esperado = models.TextField(null=True, blank=True)
    resultado_obtenido = models.TextField(null=True, blank=True)
    capacidad = models.IntegerField(default=0)
    estado = models.CharField(
        max_length=50,
        choices=Estado.choices,
        default=Estado.PLANIFICADO,
    )
    coordinador = models.ForeignKey(
        Coordinador,
        on_delete=models.SET_NULL,
        null=True,
        related_name="eventos",
        db_column="coordinador_id",
    )
    # RF-EV-01: Ampliación de la jerarquía territorial completa para la creación de eventos
    barrio = models.ForeignKey(
        Barrio,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="eventos",
        db_column="barrio_id",
    )
    sector = models.ForeignKey(
        Sector,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="eventos",
        db_column="sector_id",
    )
    punto_interes = models.ForeignKey(
        PuntoInteres,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="eventos",
        db_column="punto_interes_id",
    )

    class Meta:
        managed = False
        db_table = 'evento'
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"
        ordering = ["-fecha", "hora_inicio"]

    def __str__(self):
        return f"{self.nombre} ({self.fecha})"


# =============================================================================
# EVENTO_TIPO
# =============================================================================
class EventoTipo(models.Model):

    class Tipo(models.TextChoices):
        RECOLECCION_DATOS = "RECOLECCION_DATOS", "Recolección de datos"
        ENCUESTAS = "ENCUESTAS", "Encuestas"
        MOVILIZACION = "MOVILIZACION", "Movilización"
        PUBLICIDAD = "PUBLICIDAD", "Publicidad"
        ACTIVIDAD_COMUNITARIA = "ACTIVIDAD_COMUNITARIA", "Actividad comunitaria"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name="tipos",
        db_column="evento_id",
    )
    tipo = models.CharField(max_length=100, choices=Tipo.choices)

    class Meta:
        managed = False
        db_table = 'evento_tipo'
        verbose_name = "Tipo de Evento"
        verbose_name_plural = "Tipos de Evento"

    def __str__(self):
        return f"{self.evento.nombre} — {self.tipo}"


# =============================================================================
# ASIGNACION
# =============================================================================
class Asignacion(models.Model):

    class Rol(models.TextChoices):
        LIDER = "LIDER", "Líder"
        STAFF = "STAFF", "Staff del partido"
        EXTERNO = "EXTERNO", "Participante externo"

    class Metodo(models.TextChoices):
        MANUAL = "MANUAL", "Manual"
        AUTOMATICO = "AUTOMATICO", "Automático"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name="asignaciones",
        db_column="evento_id",
    )
    simpatizante = models.ForeignKey(
        Simpatizante,
        on_delete=models.CASCADE,
        related_name="asignaciones",
        db_column="simpatizante_id",
    )
    rol = models.CharField(max_length=100, choices=Rol.choices, null=True, blank=True)
    metodo = models.CharField(max_length=100, choices=Metodo.choices, null=True, blank=True)
    asistio = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = 'asignacion'
        verbose_name = "Asignación"
        verbose_name_plural = "Asignaciones"
        unique_together = [("evento", "simpatizante")]

    def __str__(self):
        return f"{self.simpatizante.nombre} → {self.evento.nombre} [{self.rol}]"


# =============================================================================
# COBERTURA
# =============================================================================
class Cobertura(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name="coberturas",
        db_column="evento_id",
    )
    ocupacion = models.CharField(max_length=255)
    requeridos = models.IntegerField(default=0)
    asignados = models.IntegerField(default=0)

    class Meta:
        managed = False
        db_table = 'cobertura'
        verbose_name = "Cobertura"
        verbose_name_plural = "Coberturas"

    def __str__(self):
        return f"{self.evento.nombre} — {self.ocupacion}: {self.asignados}/{self.requeridos}"


# =============================================================================
# OBSERVACION
# =============================================================================
class Observacion(models.Model):

    class Momento(models.TextChoices):
        INICIAL = "INICIAL", "Inicial"
        FINAL = "FINAL", "Final"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name="observaciones",
        db_column="evento_id",
    )
    momento = models.CharField(max_length=50, choices=Momento.choices)
    contenido = models.TextField()
    # Se remueve auto_now_add para evitar colisiones con defaults de PostgreSQL en tablas no gestionadas
    registrado_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'observacion'
        verbose_name = "Observación"
        verbose_name_plural = "Observaciones"
        ordering = ["registrado_en"]

    def __str__(self):
        return f"{self.evento.nombre} [{self.momento}]"


# =============================================================================
# PARTICIPACION_EXTERNA
# =============================================================================
class ParticipacionExterna(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name="participaciones_externas",
        db_column="evento_id",
    )
    cantidad = models.IntegerField(default=0)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'participacion_externa'
        verbose_name = "Participación Externa"
        verbose_name_plural = "Participaciones Externas"

    def __str__(self):
        return f"{self.evento.nombre} — {self.cantidad} externos"


# =============================================================================
# MATERIAL_PUBLICITARIO
# =============================================================================
class MaterialPublicitario(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name="materiales",
        db_column="evento_id",
    )
    entregado = models.IntegerField(default=0)
    restante = models.IntegerField(default=0)

    class Meta:
        managed = False
        db_table = 'material_publicitario'
        verbose_name = "Material Publicitario"
        verbose_name_plural = "Materiales Publicitarios"

    def __str__(self):
        return f"{self.evento.nombre} — entregado: {self.entregado}, restante: {self.restante}"


# =============================================================================
# ESTADO_MATERIAL
# =============================================================================
class EstadoMaterial(models.Model):

    class Estado(models.TextChoices):
        CONSERVADO = "CONSERVADO", "Conservado"
        DETERIORADO = "DETERIORADO", "Deteriorado"
        RETIRADO = "RETIRADO", "Retirado"
        VANDALIZADO = "VANDALIZADO", "Vandalizado"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name="estados_material",
        db_column="evento_id",
    )
    estado = models.CharField(max_length=100, choices=Estado.choices)
    notas = models.TextField(null=True, blank=True)
    # Se remueve auto_now_add para delegar la marca temporal nativa al motor relacional
    registrado_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'estado_material'
        verbose_name = "Estado de Material"
        verbose_name_plural = "Estados de Material"
        ordering = ["-registrado_en"]

    def __str__(self):
        return f"{self.evento.nombre} — {self.estado}"


# =============================================================================
# AUDITORIA
# =============================================================================
class Auditoria(models.Model):

    class Accion(models.TextChoices):
        INSERT = "INSERT", "Insert"
        UPDATE = "UPDATE", "Update"
        DELETE = "DELETE", "Delete"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    coordinador = models.ForeignKey(
        Coordinador,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="auditorias",
        db_column="coordinador_id",
    )
    tabla = models.CharField(max_length=150)
    registro_id = models.UUIDField()
    accion = models.CharField(max_length=20, choices=Accion.choices)
    cambios = models.JSONField(null=True, blank=True)
    # Se remueve auto_now_add para sincronizar limpiamente con triggers nativos de PostgreSQL
    en = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'auditoria'
        verbose_name = "Auditoría"
        verbose_name_plural = "Auditorías"
        ordering = ["-en"]

    def __str__(self):
        return f"{self.accion} en {self.tabla}"