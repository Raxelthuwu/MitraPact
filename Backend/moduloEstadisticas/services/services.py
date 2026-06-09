import csv
import io
import json
import logging
import datetime
from typing import Any, Dict, List, Optional
import uuid

from asgiref.sync import sync_to_async
from django.db import transaction

from Backend.moduloEstadisticas.interfaces import (
    ICatalogoOcupacionService,
    ICatalogoInclinacionVotoService,
    ICatalogoIntencionParticipacionService,
    ICatalogoProblematicaService,
    IRangoEdadService,
    IPeriodoEstadisticoService,
    IImportacionCsvService,
    IEncuestaService,
    ISnapshotTerritorialService,
    IVariacionTemporalService,
    IRankingProblematicaService,
    IResultadoCruceService,
    ICaracterizacionTerritorialService,
    IExportacionResultadoService,
    IResumenEstadisticoService,
)

# Toda la persistencia viene del models — este archivo NO importa connection ni db
from Backend.moduloEstadisticas.models import (
    CatalogoOcupacion,
    CatalogoInclinacionVoto,
    CatalogoIntencionParticipacion,
    CatalogoProblematica,
    RangoEdad,
    PeriodoEstadistico,
    ImportacionCsv,
    Encuesta,
    SnapshotTerritorial,
    VariacionTemporal,
    RankingProblematica,
    ResultadoCruce,
    CaracterizacionTerritorial,
    ExportacionResultado,
    ResumenEstadistico,
)

logger = logging.getLogger(__name__)


# =============================================================================
# HELPERS INTERNOS DE CÁLCULO  (lógica pura — sin tocar la BD directamente)
# =============================================================================

def _diff_pct(ant: Dict, act: Dict, key: str) -> Optional[float]:
    """Diferencia de porcentaje entre dos snapshots para una clave dada."""
    a, b = ant.get(key), act.get(key)
    return round(float(b) - float(a), 4) if (a is not None and b is not None) else None


def _calcular_variacion_barrio(
    barrio_id: str, periodo_anterior_id: str, periodo_actual_id: str
) -> Optional[Dict]:
    """
    Obtiene los porcentajes de ambos períodos desde el modelo y calcula
    la variación. Devuelve el registro persistido o None si no hay datos.
    """
    logger.info(
        "[_calcular_variacion_barrio] barrio=%s  %s → %s",
        barrio_id, periodo_anterior_id, periodo_actual_id,
    )
    ant = SnapshotTerritorial.obtener_porcentajes(barrio_id, periodo_anterior_id) or {}
    act = SnapshotTerritorial.obtener_porcentajes(barrio_id, periodo_actual_id)   or {}

    var_simp    = _diff_pct(ant, act, "pct_simpatizantes")
    var_ind     = _diff_pct(ant, act, "pct_indecisos")
    var_no_simp = _diff_pct(ant, act, "pct_no_simpatizantes")
    var_part    = _diff_pct(ant, act, "pct_participacion")
    cambio      = abs(var_simp) > 5.0 if var_simp is not None else False

    logger.info(
        "[_calcular_variacion_barrio] var_simp=%.4f  var_ind=%.4f  cambio=%s",
        var_simp or 0, var_ind or 0, cambio,
    )
    return VariacionTemporal.crear_o_reemplazar(
        barrio_id=barrio_id,
        periodo_anterior_id=periodo_anterior_id,
        periodo_actual_id=periodo_actual_id,
        var_simp=var_simp,
        var_ind=var_ind,
        var_no_simp=var_no_simp,
        var_part=var_part,
        cambio=cambio,
    )


def _calcular_caracterizacion_barrio(barrio_id: str, periodo_id: str) -> Optional[Dict]:
    """
    Extrae métricas del snapshot y de los rankings ya persistidos para
    determinar la caracterización del barrio. Sin queries propias.
    """
    logger.info(
        "[_calcular_caracterizacion_barrio] barrio=%s periodo=%s", barrio_id, periodo_id
    )
    snap = SnapshotTerritorial.obtener_porcentajes(barrio_id, periodo_id) or {}

    pct_simp    = float(snap.get("pct_simpatizantes")    or 0)
    pct_ind     = float(snap.get("pct_indecisos")        or 0)
    pct_no_simp = float(snap.get("pct_no_simpatizantes") or 0)
    indice      = float(snap.get("indice_intervencion")  or 0)

    # Afinidad predominante: la categoría con mayor porcentaje
    afinidad = max(
        [("SIMPATIZANTE", pct_simp), ("INDECISO", pct_ind), ("NO_SIMPATIZANTE", pct_no_simp)],
        key=lambda x: x[1],
    )[0]
    logger.info("[_calcular_caracterizacion_barrio] afinidad_predominante=%s", afinidad)

    datos = {
        "afinidad_predominante":         afinidad,
        "ocupacion_predominante":        Encuesta.moda("ocupacion_cod",              barrio_id, periodo_id),
        "problematica_predominante_cod": RankingProblematica.top1_cod(               barrio_id, periodo_id),
        "participacion_predominante":    Encuesta.moda("intencion_participacion_cod", barrio_id, periodo_id),
        "pct_indecision":                round(pct_ind,   2),
        "pct_apoyo":                     round(pct_simp,  2),
        "cantidad_eventos":              CaracterizacionTerritorial.contar_eventos(  barrio_id),
        "frecuencia_problematicas":      round(indice, 4) if indice else None,
        "es_prioritario":                pct_no_simp > 40.0 or pct_ind > 35.0,
        "alto_potencial_crecimiento":    pct_ind > 25.0 and indice > 0,
    }
    return CaracterizacionTerritorial.crear_o_reemplazar(barrio_id, periodo_id, datos)


def _construir_texto_resumen(barrio_id: str, periodo_id: str) -> str:
    """
    Construye el texto narrativo del resumen a partir de los datos ya
    persistidos en snapshot, caracterización y ranking. Sin queries propias.
    """
    logger.info(
        "[_construir_texto_resumen] barrio=%s periodo=%s", barrio_id, periodo_id
    )
    snapshots = SnapshotTerritorial.listar(barrio_id=barrio_id, periodo_id=periodo_id)
    snap      = snapshots[0] if snapshots else None

    caracterizaciones = CaracterizacionTerritorial.listar(barrio_id=barrio_id, periodo_id=periodo_id)
    caract            = caracterizaciones[0] if caracterizaciones else None

    # Toma solo el top-3 del ranking ya calculado
    ranking = RankingProblematica.listar(periodo_id=periodo_id, barrio_id=barrio_id)[:3]

    lineas = [f"Resumen estadístico — Barrio: {barrio_id} | Período: {periodo_id}"]

    if snap:
        lineas.append(
            f"Distribución: Simpatizantes {snap.get('pct_simpatizantes')}% | "
            f"Indecisos {snap.get('pct_indecisos')}% | "
            f"No simpatizantes {snap.get('pct_no_simpatizantes')}% | "
            f"Participación {snap.get('pct_participacion')}%"
        )
    if caract:
        lineas.append(
            f"Afinidad: {caract.get('afinidad_predominante')} | "
            f"Ocupación: {caract.get('ocupacion_predominante')} | "
            f"Prioritario: {'Sí' if caract.get('es_prioritario') else 'No'} | "
            f"Alto potencial: {'Sí' if caract.get('alto_potencial_crecimiento') else 'No'}"
        )
    if ranking:
        lineas.append(
            "Top problemáticas: " + ", ".join(
                f"#{r['posicion_ranking']} {r.get('problematica_desc', r.get('problematica_cod'))} "
                f"({r['pct_frecuencia']}%)"
                for r in ranking
            )
        )
    texto = "\n".join(lineas)
    logger.info("[_construir_texto_resumen] Texto construido (%d líneas).", len(lineas))
    return texto


# =============================================================================
# HELPERS DE VALIDACIÓN CSV
# =============================================================================

_COLUMNAS_REQUERIDAS = {
    "fecha", "edad", "barrio_id", "ocupacion_cod",
    "inclinacion_voto_cod", "intencion_participacion_cod", "prob_1_cod",
}


def _parsear_fila_csv(i: int, fila: Dict) -> tuple[Optional[Dict], Optional[str]]:
    """
    Valida y normaliza una fila de CSV.
    Devuelve (fila_normalizada, None) si es válida o (None, mensaje_error).
    """
    faltantes = _COLUMNAS_REQUERIDAS - set(fila.keys())
    if faltantes:
        return None, f"Fila {i}: columnas faltantes {faltantes}"

    def _int(v: Any) -> Optional[int]:
        return int(v) if v and str(v).strip() else None

    try:
        return {
            "fecha":          fila["fecha"].strip(),
            "edad":           int(fila["edad"]),
            "barrio":         fila.get("barrio", "").strip()    or None,
            "barrio_id":      fila.get("barrio_id", "").strip() or None,
            "ocupacion_cod":               _int(fila.get("ocupacion_cod")),
            "inclinacion_voto_cod":        _int(fila.get("inclinacion_voto_cod")),
            "intencion_participacion_cod": _int(fila.get("intencion_participacion_cod")),
            "prob_1_cod":  _int(fila.get("prob_1_cod")),
            "prob_2_cod":  _int(fila.get("prob_2_cod")),
            "prob_otra":   fila.get("prob_otra", "").strip()         or None,
            "opinion_politica": fila.get("opinion_politica", "").strip() or None,
        }, None
    except (ValueError, KeyError) as e:
        return None, f"Fila {i}: {e}"


# =============================================================================
# SERVICIOS
# =============================================================================

# ── Catálogos (solo lectura) ──────────────────────────────────────────────────

class _CatalogoBaseService:
    """Base para los cuatro catálogos de solo lectura."""
    _modelo = None  # subclases asignan el modelo concreto

    async def listar(self) -> List[Dict]:
        logger.info("[%s.listar] Listando catálogo.", self.__class__.__name__)
        result = await sync_to_async(self._modelo.listar)()
        logger.info("[%s.listar] %d registros.", self.__class__.__name__, len(result))
        return result

    async def obtener(self, codigo: int) -> Optional[Dict]:
        logger.info("[%s.obtener] codigo=%s.", self.__class__.__name__, codigo)
        result = await sync_to_async(self._modelo.obtener)(codigo)
        if not result:
            logger.warning("[%s.obtener] No encontrado: codigo=%s.", self.__class__.__name__, codigo)
        return result


class CatalogoOcupacionService(_CatalogoBaseService, ICatalogoOcupacionService):
    _modelo = CatalogoOcupacion

class CatalogoInclinacionVotoService(_CatalogoBaseService, ICatalogoInclinacionVotoService):
    _modelo = CatalogoInclinacionVoto

class CatalogoIntencionParticipacionService(_CatalogoBaseService, ICatalogoIntencionParticipacionService):
    _modelo = CatalogoIntencionParticipacion

class CatalogoProblematicaService(_CatalogoBaseService, ICatalogoProblematicaService):
    _modelo = CatalogoProblematica


# ── Rango de edad ─────────────────────────────────────────────────────────────

class RangoEdadService(IRangoEdadService):

    async def listar(self) -> List[Dict]:
        logger.info("[RangoEdadService.listar] Listando rangos.")
        result = await sync_to_async(RangoEdad.listar)()
        logger.info("[RangoEdadService.listar] %d rangos.", len(result))
        return result

    async def obtener(self, rango_id: str) -> Optional[Dict]:
        logger.info("[RangoEdadService.obtener] id=%s.", rango_id)
        result = await sync_to_async(RangoEdad.obtener)(rango_id)
        if not result:
            logger.warning("[RangoEdadService.obtener] No encontrado: id=%s.", rango_id)
        return result

    async def crear(self, etiqueta: str, edad_min: int, edad_max: int) -> Dict:
        logger.info("[RangoEdadService.crear] etiqueta='%s' %d-%d.", etiqueta, edad_min, edad_max)
        result = await sync_to_async(RangoEdad.crear)(etiqueta, edad_min, edad_max)
        logger.info("[RangoEdadService.crear] Creado: %s.", result)
        return result

    async def actualizar(self, rango_id: str, etiqueta: str, edad_min: int, edad_max: int) -> Optional[Dict]:
        logger.info("[RangoEdadService.actualizar] id=%s.", rango_id)
        updated = await sync_to_async(RangoEdad.actualizar)(rango_id, etiqueta, edad_min, edad_max)
        if not updated:
            logger.warning("[RangoEdadService.actualizar] No encontrado: id=%s.", rango_id)
            return None
        return await self.obtener(rango_id)

    async def eliminar(self, rango_id: str) -> bool:
        logger.info("[RangoEdadService.eliminar] id=%s.", rango_id)
        result = await sync_to_async(RangoEdad.eliminar)(rango_id)
        if not result:
            logger.warning("[RangoEdadService.eliminar] No encontrado: id=%s.", rango_id)
        return result


# ── Período estadístico ───────────────────────────────────────────────────────

class PeriodoEstadisticoService(IPeriodoEstadisticoService):

    async def listar(self) -> List[Dict]:
        logger.info("[PeriodoEstadisticoService.listar] Listando períodos.")
        result = await sync_to_async(PeriodoEstadistico.listar)()
        logger.info("[PeriodoEstadisticoService.listar] %d períodos.", len(result))
        return result

    async def obtener(self, periodo_id: str) -> Optional[Dict]:
        logger.info("[PeriodoEstadisticoService.obtener] id=%s.", periodo_id)
        result = await sync_to_async(PeriodoEstadistico.obtener)(periodo_id)
        if not result:
            logger.warning("[PeriodoEstadisticoService.obtener] No encontrado: id=%s.", periodo_id)
        return result

    async def crear(self, etiqueta: str, fecha_inicio, fecha_fin) -> Dict:
        logger.info("[PeriodoEstadisticoService.crear] '%s' %s→%s.", etiqueta, fecha_inicio, fecha_fin)
        result = await sync_to_async(PeriodoEstadistico.crear)(etiqueta, fecha_inicio, fecha_fin)
        logger.info("[PeriodoEstadisticoService.crear] Creado: %s.", result)
        return result

    async def actualizar(self, periodo_id: str, etiqueta: str, fecha_inicio, fecha_fin) -> Optional[Dict]:
        logger.info("[PeriodoEstadisticoService.actualizar] id=%s.", periodo_id)
        updated = await sync_to_async(PeriodoEstadistico.actualizar)(periodo_id, etiqueta, fecha_inicio, fecha_fin)
        if not updated:
            logger.warning("[PeriodoEstadisticoService.actualizar] No encontrado: id=%s.", periodo_id)
            return None
        return await self.obtener(periodo_id)

    async def eliminar(self, periodo_id: str) -> bool:
        logger.info("[PeriodoEstadisticoService.eliminar] id=%s.", periodo_id)
        result = await sync_to_async(PeriodoEstadistico.eliminar)(periodo_id)
        if not result:
            logger.warning("[PeriodoEstadisticoService.eliminar] No encontrado: id=%s.", periodo_id)
        return result


# ── Importación CSV ───────────────────────────────────────────────────────────

class ImportacionCsvService(IImportacionCsvService):

    async def listar(self) -> List[Dict]:
        logger.info("[ImportacionCsvService.listar] Listando importaciones.")
        result = await sync_to_async(ImportacionCsv.listar)()
        logger.info("[ImportacionCsvService.listar] %d importaciones.", len(result))
        return result

    async def obtener(self, importacion_id: str) -> Optional[Dict]:
        logger.info("[ImportacionCsvService.obtener] id=%s.", importacion_id)
        result = await sync_to_async(ImportacionCsv.obtener)(importacion_id)
        if not result:
            logger.warning("[ImportacionCsvService.obtener] No encontrado: id=%s.", importacion_id)
        return result

    async def obtener_estado(self, importacion_id: str) -> Optional[Dict]:
        """Alias semántico de obtener — expone el estado de procesamiento."""
        return await self.obtener(importacion_id)

    async def importar(self, archivo: Any) -> Dict:
        """
        Versión adaptada para recibir directamente el objeto 'archivo' desde la vista,
        extrayendo de forma interna el ID de importación y los bytes del contenido.
        """
        # Intentamos obtener el ID desde los atributos del archivo o generamos uno si no viene
        importacion_id = getattr(archivo, "importacion_id", None) or getattr(archivo, "id", None)
        if not importacion_id:
            importacion_id = str(uuid.uuid4())

        logger.info(
            "[ImportacionCsvService.importar] Iniciando procesamiento id=%s.", importacion_id
        )

        # Leer los bytes del archivo cargado
        try:
            if hasattr(archivo, "read"):
                contenido_bytes = archivo.read()
                if hasattr(archivo, "seek"):
                    archivo.seek(0)
            else:
                contenido_bytes = bytes(archivo)
        except Exception as e:
            logger.error("No se pudieron extraer los bytes del archivo: %s", str(e))
            return {"error": f"Archivo ilegible: {str(e)}"}

        def _procesar():
            logger.info("[ImportacionCsvService.importar] Leyendo contenido del CSV...")
            errores = []
            validos = []
            invalidos = 0

            try:
                content = contenido_bytes.decode("utf-8")
                delimiter = "\t" if "\t" in content else ","
                reader = csv.reader(io.StringIO(content), delimiter=delimiter)
            except Exception as e:
                logger.error("Error al decodificar archivo CSV: %s", str(e))
                ImportacionCsv.finalizar(importacion_id, 0, 0, 0, f"Error de lectura: {str(e)}")
                return

            for i, row in enumerate(reader, start=1):
                if not row or len(row) < 10:
                    if row and len(row) > 0:
                        errores.append(f"Fila {i}: Columnas insuficientes (mínimo 10).")
                        invalidos += 1
                    continue

                try:
                    # ─── LIMPIEZA ABSOLUTA DE ENTRADAS (.strip().lower()) ───
                    id_encuesta  = row[0].strip().lower()
                    periodo_id   = row[1].strip().lower()
                    fecha        = row[2].strip()
                    edad         = int(row[3].strip())
                    barrio       = row[4].strip()
                    barrio_id    = row[5].strip().lower()
                    ocupacion_id = row[6].strip().lower()
                    voto_id      = row[7].strip().lower()
                    part_id      = row[8].strip().lower()
                    prob_id      = row[9].strip().lower()

                    intensidad = None
                    if len(row) > 10 and row[10].strip().isdigit():
                        intensidad = int(row[10].strip())

                    texto_libre = row[-1].strip() if len(row) > 10 else ""

                    encuesta_dict = {
                        "id": id_encuesta,
                        "periodo_id": periodo_id,
                        "fecha": fecha,
                        "edad": edad,
                        "barrio_nombre_csv": barrio,
                        "barrio_id": barrio_id,
                        "catalogo_ocupacion_id": ocupacion_id,
                        "catalogo_inclinacion_voto_id": voto_id,
                        "catalogo_intencion_participacion_id": part_id,
                        "catalogo_problematica_id": prob_id,
                        "intensidad_problematica": intensidad,
                        "texto_libre_problematica": texto_libre
                    }
                    validos.append(encuesta_dict)

                except Exception as e:
                    errores.append(f"Fila {i}: Error en formato de datos -> {str(e)}")
                    invalidos += 1

            # Inserción y guardado transaccional atómico
            with transaction.atomic():
                if validos:
                    Encuesta.insercion_masiva(validos)
                ImportacionCsv.finalizar(
                    importacion_id=importacion_id,
                    total=len(validos) + invalidos,
                    validos=len(validos),
                    invalidos=invalidos,
                    errores="\n".join(errores) if errores else None,
                )

            # ─── AUTO-CALCULAR TODO EL PERIODO DE FORMA SECUENCIAL SEGURO ───
            if validos:
                periodos_afectados = list({f["periodo_id"] for f in validos if f.get("periodo_id")})
                
                for p_id in periodos_afectados:
                    logger.info(f"[Auto-Calculo] Iniciando secuencia completa para periodo: {p_id}")
                    try:
                        # 1. Regenerar Snapshots Territoriales
                        SnapshotTerritorial.generar_todos(p_id)
                        
                        # 2. Calcular los rankings globales del periodo (Le pasamos el diccionario de restricciones)
                        RankingProblematica.calcular_todos(p_id)
                        
                        # 3. Generar las Caracterizaciones del territorio
                        CaracterizacionTerritorial.generar_todos(p_id)
                        
                        # 4. Construir y actualizar resúmenes estadísticos textuales por barrio
                        barrios = Encuesta.barrios_del_periodo(p_id)
                        for b_id in barrios:
                            texto_resumen = _construir_texto_resumen(b_id, p_id)
                            ResumenEstadistico.crear_o_reemplazar(b_id, p_id, texto_resumen)
                            
                        logger.info(f"[Auto-Calculo] Procesamiento de reportes exitoso para periodo {p_id}.")
                    except Exception as calc_err:
                        logger.error(f"Fallo crítico en auto-calculo automático del periodo {p_id}: {str(calc_err)}")

        # Forzar la ejecución síncrona en el hilo seguro de Django
        await sync_to_async(_procesar)()

        logger.info(
            "[ImportacionCsvService.importar] Importación id=%s finalizada exitosamente.", importacion_id
        )
        return await sync_to_async(ImportacionCsv.obtener)(importacion_id)


# ── Encuesta ──────────────────────────────────────────────────────────────────

class EncuestaService(IEncuestaService):

    async def listar(
        self,
        importacion_id: Optional[str] = None,
        barrio_id:      Optional[str] = None,
        periodo_id:     Optional[str] = None,
    ) -> List[Dict]:
        logger.info(
            "[EncuestaService.listar] importacion_id=%s  barrio_id=%s  periodo_id=%s.",
            importacion_id, barrio_id, periodo_id,
        )
        def _query():
            if periodo_id:
                return Encuesta.listar_por_periodo(periodo_id)
            return Encuesta.listar(importacion_id=importacion_id, barrio_id=barrio_id)

        result = await sync_to_async(_query)()
        logger.info("[EncuestaService.listar] %d encuestas.", len(result))
        return result

    async def obtener(self, encuesta_id: str) -> Optional[Dict]:
        logger.info("[EncuestaService.obtener] id=%s.", encuesta_id)
        result = await sync_to_async(Encuesta.obtener)(encuesta_id)
        if not result:
            logger.warning("[EncuestaService.obtener] No encontrada: id=%s.", encuesta_id)
        return result

    async def crear(self, payload: Dict) -> Dict:
        logger.info("[EncuestaService.crear] Creando encuesta.")
        result = await sync_to_async(Encuesta.crear)(payload)
        logger.info("[EncuestaService.crear] Creada: %s.", result)
        return result

    async def actualizar(self, encuesta_id: str, payload: Dict) -> Optional[Dict]:
        logger.info("[EncuestaService.actualizar] id=%s.", encuesta_id)
        updated = await sync_to_async(Encuesta.actualizar)(encuesta_id, payload)
        if not updated:
            logger.warning("[EncuestaService.actualizar] No encontrada o sin cambios: id=%s.", encuesta_id)
            return None
        return await self.obtener(encuesta_id)

    async def eliminar(self, encuesta_id: str) -> bool:
        logger.info("[EncuestaService.eliminar] id=%s.", encuesta_id)
        result = await sync_to_async(Encuesta.eliminar)(encuesta_id)
        if not result:
            logger.warning("[EncuestaService.eliminar] No encontrada: id=%s.", encuesta_id)
        return result


# ── Snapshot territorial ──────────────────────────────────────────────────────

class SnapshotTerritorialService(ISnapshotTerritorialService):

    async def listar(self, barrio_id=None, periodo_id=None) -> List[Dict]:
        logger.info(
            "[SnapshotTerritorialService.listar] barrio_id=%s  periodo_id=%s.", barrio_id, periodo_id
        )
        result = await sync_to_async(SnapshotTerritorial.listar)(
            barrio_id=barrio_id, periodo_id=periodo_id
        )
        logger.info("[SnapshotTerritorialService.listar] %d snapshots.", len(result))
        return result

    async def obtener(self, snapshot_id: str) -> Optional[Dict]:
        logger.info("[SnapshotTerritorialService.obtener] id=%s.", snapshot_id)
        result = await sync_to_async(SnapshotTerritorial.obtener)(snapshot_id)
        if not result:
            logger.warning("[SnapshotTerritorialService.obtener] No encontrado: id=%s.", snapshot_id)
        return result

    async def generar(self, barrio_id: str, periodo_id: str) -> Dict:
        """
        Obtiene los totales agregados de encuestas (modelo) y genera el snapshot.
        """
        logger.info(
            "[SnapshotTerritorialService.generar] barrio_id=%s  periodo_id=%s.", barrio_id, periodo_id
        )
        def _gen():
            # Lógica de negocio: obtener totales y delegar creación al modelo
            totales = Encuesta.agregar_por_barrio_y_periodo(barrio_id, periodo_id)
            logger.info(
                "[SnapshotTerritorialService.generar] Totales obtenidos: %s.", totales
            )
            return SnapshotTerritorial.crear_o_reemplazar(barrio_id, periodo_id, totales)

        result = await sync_to_async(_gen)()
        logger.info("[SnapshotTerritorialService.generar] Snapshot generado: %s.", result)
        return result

    async def generar_todos(self, periodo_id: str) -> List[Dict]:
        """Genera un snapshot por cada barrio con encuestas en el período."""
        logger.info(
            "[SnapshotTerritorialService.generar_todos] periodo_id=%s.", periodo_id
        )
        def _gen_todos():
            barrios = Encuesta.barrios_del_periodo(periodo_id)
            logger.info(
                "[SnapshotTerritorialService.generar_todos] %d barrios encontrados.", len(barrios)
            )
            snapshots = []
            for barrio_id in barrios:
                totales = Encuesta.agregar_por_barrio_y_periodo(barrio_id, periodo_id)
                snap    = SnapshotTerritorial.crear_o_reemplazar(barrio_id, periodo_id, totales)
                snapshots.append(snap)
                logger.info(
                    "[SnapshotTerritorialService.generar_todos] Snapshot generado para barrio=%s.", barrio_id
                )
            return snapshots

        result = await sync_to_async(_gen_todos)()
        logger.info(
            "[SnapshotTerritorialService.generar_todos] %d snapshots generados.", len(result)
        )
        return result

    async def eliminar(self, snapshot_id: str) -> bool:
        logger.info("[SnapshotTerritorialService.eliminar] id=%s.", snapshot_id)
        result = await sync_to_async(SnapshotTerritorial.eliminar)(snapshot_id)
        if not result:
            logger.warning("[SnapshotTerritorialService.eliminar] No encontrado: id=%s.", snapshot_id)
        return result


# ── Variación temporal ────────────────────────────────────────────────────────

class VariacionTemporalService(IVariacionTemporalService):

    async def listar(self, barrio_id=None, periodo_actual_id=None) -> List[Dict]:
        logger.info(
            "[VariacionTemporalService.listar] barrio_id=%s  periodo_actual_id=%s.",
            barrio_id, periodo_actual_id,
        )
        result = await sync_to_async(VariacionTemporal.listar)(
            barrio_id=barrio_id, periodo_actual_id=periodo_actual_id
        )
        logger.info("[VariacionTemporalService.listar] %d variaciones.", len(result))
        return result

    async def obtener(self, variacion_id: str) -> Optional[Dict]:
        logger.info("[VariacionTemporalService.obtener] id=%s.", variacion_id)
        result = await sync_to_async(VariacionTemporal.obtener)(variacion_id)
        if not result:
            logger.warning("[VariacionTemporalService.obtener] No encontrada: id=%s.", variacion_id)
        return result

    async def calcular(
        self, barrio_id: str, periodo_anterior_id: str, periodo_actual_id: str
    ) -> Optional[Dict]:
        """
        Lógica de negocio: compara porcentajes entre dos snapshots
        y persiste la variación vía el helper interno.
        """
        logger.info(
            "[VariacionTemporalService.calcular] barrio=%s  %s→%s.",
            barrio_id, periodo_anterior_id, periodo_actual_id,
        )
        result = await sync_to_async(_calcular_variacion_barrio)(
            barrio_id, periodo_anterior_id, periodo_actual_id
        )
        logger.info("[VariacionTemporalService.calcular] Variación calculada: %s.", result)
        return result

    async def calcular_todos(
        self, periodo_anterior_id: str, periodo_actual_id: str
    ) -> List[Dict]:
        """Calcula variación para todos los barrios con encuestas en el período actual."""
        logger.info(
            "[VariacionTemporalService.calcular_todos] %s→%s.",
            periodo_anterior_id, periodo_actual_id,
        )
        def _todos():
            barrios = Encuesta.barrios_del_periodo(periodo_actual_id)
            logger.info(
                "[VariacionTemporalService.calcular_todos] %d barrios.", len(barrios)
            )
            resultados = []
            for barrio_id in barrios:
                v = _calcular_variacion_barrio(barrio_id, periodo_anterior_id, periodo_actual_id)
                if v:
                    resultados.append(v)
            return resultados

        result = await sync_to_async(_todos)()
        logger.info(
            "[VariacionTemporalService.calcular_todos] %d variaciones calculadas.", len(result)
        )
        return result


# ── Ranking problemática ──────────────────────────────────────────────────────

class RankingProblematicaService(IRankingProblematicaService):

    async def listar(self, periodo_id=None, barrio_id=None) -> List[Dict]:
        logger.info(
            "[RankingProblematicaService.listar] periodo_id=%s  barrio_id=%s.", periodo_id, barrio_id
        )
        result = await sync_to_async(RankingProblematica.listar)(
            periodo_id=periodo_id, barrio_id=barrio_id
        )
        logger.info("[RankingProblematicaService.listar] %d entradas.", len(result))
        return result

    async def obtener(self, ranking_id: str) -> Optional[Dict]:
        logger.info("[RankingProblematicaService.obtener] id=%s.", ranking_id)
        result = await sync_to_async(RankingProblematica.obtener)(ranking_id)
        if not result:
            logger.warning("[RankingProblematicaService.obtener] No encontrado: id=%s.", ranking_id)
        return result

    async def calcular(self, barrio_id: str, periodo_id: str) -> List[Dict]:
        """Delega el cálculo completo al modelo — ya incluye DELETE + INSERT."""
        logger.info(
            "[RankingProblematicaService.calcular] barrio=%s  periodo=%s.", barrio_id, periodo_id
        )
        result = await sync_to_async(RankingProblematica.calcular_y_persistir)(
            barrio_id, periodo_id
        )
        logger.info(
            "[RankingProblematicaService.calcular] %d problemáticas persistidas.", len(result)
        )
        return result

    async def calcular_todos(self, periodo_id: str) -> List[Dict]:
        """Calcula el ranking de problemáticas para todos los barrios del período."""
        logger.info(
            "[RankingProblematicaService.calcular_todos] periodo_id=%s.", periodo_id
        )
        def _todos():
            barrios = Encuesta.barrios_del_periodo(periodo_id)
            logger.info(
                "[RankingProblematicaService.calcular_todos] %d barrios.", len(barrios)
            )
            resultados = []
            for barrio_id in barrios:
                resultados.extend(
                    RankingProblematica.calcular_y_persistir(barrio_id, periodo_id)
                )
            return resultados

        result = await sync_to_async(_todos)()
        logger.info(
            "[RankingProblematicaService.calcular_todos] %d registros totales.", len(result)
        )
        return result


# ── Resultado cruce ───────────────────────────────────────────────────────────

class ResultadoCruceService(IResultadoCruceService):

    async def listar(self, periodo_id: str) -> List[Dict]:
        logger.info("[ResultadoCruceService.listar] periodo_id=%s.", periodo_id)
        result = await sync_to_async(ResultadoCruce.listar)(periodo_id)
        logger.info("[ResultadoCruceService.listar] %d cruces.", len(result))
        return result

    async def obtener(self, cruce_id: str) -> Optional[Dict]:
        logger.info("[ResultadoCruceService.obtener] id=%s.", cruce_id)
        result = await sync_to_async(ResultadoCruce.obtener)(cruce_id)
        if not result:
            logger.warning("[ResultadoCruceService.obtener] No encontrado: id=%s.", cruce_id)
        return result

    async def calcular(self, periodo_id: str, dimension_a: str, dimension_b: str) -> List[Dict]:
        """Delega el cálculo completo al modelo — ya incluye DELETE + INSERT."""
        logger.info(
            "[ResultadoCruceService.calcular] periodo=%s  %s×%s.",
            periodo_id, dimension_a, dimension_b,
        )
        result = await sync_to_async(ResultadoCruce.calcular_y_persistir)(
            periodo_id, dimension_a, dimension_b
        )
        logger.info("[ResultadoCruceService.calcular] %d combinaciones.", len(result))
        return result

    async def calcular_multiples(
        self, periodo_id: str, cruces: List[Dict[str, str]]
    ) -> List[Dict]:
        """
        Lógica de negocio: itera sobre la lista de pares de dimensiones
        y delega cada cálculo al modelo.
        """
        logger.info(
            "[ResultadoCruceService.calcular_multiples] periodo=%s  %d cruces.",
            periodo_id, len(cruces),
        )
        def _multi():
            for cruce in cruces:
                dim_a = cruce.get("dimension_a", "")
                dim_b = cruce.get("dimension_b", "")
                logger.info(
                    "[ResultadoCruceService.calcular_multiples] Calculando %s×%s.", dim_a, dim_b
                )
                ResultadoCruce.calcular_y_persistir(periodo_id, dim_a, dim_b)
            return ResultadoCruce.listar(periodo_id)

        result = await sync_to_async(_multi)()
        logger.info(
            "[ResultadoCruceService.calcular_multiples] %d resultados totales.", len(result)
        )
        return result

    async def eliminar_por_periodo(self, periodo_id: str) -> int:
        logger.info("[ResultadoCruceService.eliminar_por_periodo] periodo_id=%s.", periodo_id)
        deleted = await sync_to_async(ResultadoCruce.eliminar_por_periodo)(periodo_id)
        logger.info("[ResultadoCruceService.eliminar_por_periodo] %d eliminados.", deleted)
        return deleted


# ── Caracterización territorial ───────────────────────────────────────────────

class CaracterizacionTerritorialService(ICaracterizacionTerritorialService):

    async def listar(self, barrio_id=None, periodo_id=None) -> List[Dict]:
        logger.info(
            "[CaracterizacionTerritorialService.listar] barrio_id=%s  periodo_id=%s.",
            barrio_id, periodo_id,
        )
        result = await sync_to_async(CaracterizacionTerritorial.listar)(
            barrio_id=barrio_id, periodo_id=periodo_id
        )
        logger.info("[CaracterizacionTerritorialService.listar] %d caracterizaciones.", len(result))
        return result

    async def obtener(self, caracterizacion_id: str) -> Optional[Dict]:
        logger.info("[CaracterizacionTerritorialService.obtener] id=%s.", caracterizacion_id)
        result = await sync_to_async(CaracterizacionTerritorial.obtener)(caracterizacion_id)
        if not result:
            logger.warning(
                "[CaracterizacionTerritorialService.obtener] No encontrada: id=%s.", caracterizacion_id
            )
        return result

    async def generar(self, barrio_id: str, periodo_id: str) -> Optional[Dict]:
        """
        Lógica de negocio: combina datos del snapshot y del ranking
        para determinar la caracterización — vía helper interno.
        """
        logger.info(
            "[CaracterizacionTerritorialService.generar] barrio=%s  periodo=%s.",
            barrio_id, periodo_id,
        )
        result = await sync_to_async(_calcular_caracterizacion_barrio)(barrio_id, periodo_id)
        logger.info("[CaracterizacionTerritorialService.generar] Caracterización generada: %s.", result)
        return result

    async def generar_todos(self, periodo_id: str) -> List[Dict]:
        """Genera la caracterización para cada barrio con encuestas en el período."""
        logger.info(
            "[CaracterizacionTerritorialService.generar_todos] periodo_id=%s.", periodo_id
        )
        def _todos():
            barrios = Encuesta.barrios_del_periodo(periodo_id)
            logger.info(
                "[CaracterizacionTerritorialService.generar_todos] %d barrios.", len(barrios)
            )
            resultados = []
            for barrio_id in barrios:
                c = _calcular_caracterizacion_barrio(barrio_id, periodo_id)
                if c:
                    resultados.append(c)
                    logger.info(
                        "[CaracterizacionTerritorialService.generar_todos] barrio=%s listo.", barrio_id
                    )
            return resultados

        result = await sync_to_async(_todos)()
        logger.info(
            "[CaracterizacionTerritorialService.generar_todos] %d caracterizaciones.", len(result)
        )
        return result


# ── Exportación resultado ─────────────────────────────────────────────────────

class ExportacionResultadoService(IExportacionResultadoService):

    # Fuentes de datos por tipo de análisis — solo llaman al modelo, sin SQL propio
    _FUENTES = {
        "snapshot":        lambda pid: SnapshotTerritorial.listar(periodo_id=pid),
        "variacion":       lambda pid: VariacionTemporal.listar(periodo_actual_id=pid),
        "ranking":         lambda pid: RankingProblematica.listar(periodo_id=pid),
        "cruce":           lambda pid: ResultadoCruce.listar(pid),
        "caracterizacion": lambda pid: CaracterizacionTerritorial.listar(periodo_id=pid),
    }

    async def listar(self, periodo_id=None) -> List[Dict]:
        logger.info("[ExportacionResultadoService.listar] periodo_id=%s.", periodo_id)
        result = await sync_to_async(ExportacionResultado.listar)(periodo_id=periodo_id)
        logger.info("[ExportacionResultadoService.listar] %d exportaciones.", len(result))
        return result

    async def obtener(self, exportacion_id: str) -> Optional[Dict]:
        logger.info("[ExportacionResultadoService.obtener] id=%s.", exportacion_id)
        result = await sync_to_async(ExportacionResultado.obtener)(exportacion_id)
        if not result:
            logger.warning(
                "[ExportacionResultadoService.obtener] No encontrada: id=%s.", exportacion_id
            )
        return result

    async def exportar(
        self,
        periodo_id:     str,
        tipo_analisis:  str,
        formato:        str,
        coordinador_id: Optional[str] = None,
    ) -> Dict:
        """
        Lógica de negocio completa:
          1. Valida tipo y formato.
          2. Obtiene datos del modelo según tipo_analisis.
          3. Escribe el archivo físico (CSV o JSON).
          4. Registra la exportación vía el modelo.
        """
        logger.info(
            "[ExportacionResultadoService.exportar] periodo=%s  tipo=%s  formato=%s.",
            periodo_id, tipo_analisis, formato,
        )

        def _exportar():
            fuente = self._FUENTES.get(tipo_analisis)
            if not fuente:
                logger.error(
                    "[ExportacionResultadoService.exportar] tipo_analisis inválido: '%s'.", tipo_analisis
                )
                raise ValueError(f"tipo_analisis inválido: '{tipo_analisis}'")

            fmt = formato.upper()
            if fmt not in {"CSV", "JSON"}:
                logger.error(
                    "[ExportacionResultadoService.exportar] formato inválido: '%s'.", formato
                )
                raise ValueError(f"formato inválido: '{formato}'. Use CSV o JSON.")

            # Obtener datos vía el modelo (sin queries directas)
            datos = fuente(periodo_id)
            logger.info(
                "[ExportacionResultadoService.exportar] %d registros obtenidos para '%s'.",
                len(datos), tipo_analisis,
            )

            # Construir archivo físico (lógica de negocio de serialización)
            ts     = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre = f"exportacion_{tipo_analisis}_{periodo_id[:8]}_{ts}"

            if fmt == "JSON":
                ruta = f"/tmp/{nombre}.json"
                with open(ruta, "w", encoding="utf-8") as f:
                    json.dump(datos, f, ensure_ascii=False, indent=2)
            else:  # CSV
                ruta = f"/tmp/{nombre}.csv"
                with open(ruta, "w", newline="", encoding="utf-8") as f:
                    if datos:
                        writer = csv.DictWriter(f, fieldnames=datos[0].keys())
                        writer.writeheader()
                        writer.writerows(datos)

            logger.info(
                "[ExportacionResultadoService.exportar] Archivo escrito en '%s'.", ruta
            )

            # Registrar en BD vía el modelo
            result = ExportacionResultado.crear(
                periodo_id=periodo_id,
                tipo=tipo_analisis,
                formato=fmt,
                ruta=ruta,
                coordinador_id=coordinador_id,
            )
            logger.info(
                "[ExportacionResultadoService.exportar] Exportación registrada: %s.", result
            )
            return result

        return await sync_to_async(_exportar)()


# ── Resumen estadístico ───────────────────────────────────────────────────────

class ResumenEstadisticoService(IResumenEstadisticoService):

    async def listar(self, barrio_id=None, periodo_id=None) -> List[Dict]:
        logger.info(
            "[ResumenEstadisticoService.listar] barrio_id=%s  periodo_id=%s.", barrio_id, periodo_id
        )
        result = await sync_to_async(ResumenEstadistico.listar)(
            barrio_id=barrio_id, periodo_id=periodo_id
        )
        logger.info("[ResumenEstadisticoService.listar] %d resúmenes.", len(result))
        return result

    async def obtener(self, resumen_id: str) -> Optional[Dict]:
        logger.info("[ResumenEstadisticoService.obtener] id=%s.", resumen_id)
        result = await sync_to_async(ResumenEstadistico.obtener)(resumen_id)
        if not result:
            logger.warning("[ResumenEstadisticoService.obtener] No encontrado: id=%s.", resumen_id)
        return result

    async def generar(self, barrio_id: str, periodo_id: str) -> Dict:
        """
        Lógica de negocio: construye el texto narrativo a partir de datos
        ya persistidos y lo guarda vía el modelo.
        """
        logger.info(
            "[ResumenEstadisticoService.generar] barrio=%s  periodo=%s.", barrio_id, periodo_id
        )
        def _gen():
            texto = _construir_texto_resumen(barrio_id, periodo_id)
            result = ResumenEstadistico.crear_o_reemplazar(barrio_id, periodo_id, texto)
            logger.info("[ResumenEstadisticoService.generar] Resumen creado: %s.", result)
            return result

        return await sync_to_async(_gen)()

    async def generar_todos(self, periodo_id: str) -> List[Dict]:
        """Genera el resumen textual para cada barrio con encuestas en el período."""
        logger.info(
            "[ResumenEstadisticoService.generar_todos] periodo_id=%s.", periodo_id
        )
        def _todos():
            barrios = Encuesta.barrios_del_periodo(periodo_id)
            logger.info(
                "[ResumenEstadisticoService.generar_todos] %d barrios.", len(barrios)
            )
            resultados = []
            for barrio_id in barrios:
                texto = _construir_texto_resumen(barrio_id, periodo_id)
                r     = ResumenEstadistico.crear_o_reemplazar(barrio_id, periodo_id, texto)
                resultados.append(r)
                logger.info(
                    "[ResumenEstadisticoService.generar_todos] Resumen barrio=%s generado.", barrio_id
                )
            return resultados

        result = await sync_to_async(_todos)()
        logger.info(
            "[ResumenEstadisticoService.generar_todos] %d resúmenes generados.", len(result)
        )
        return result