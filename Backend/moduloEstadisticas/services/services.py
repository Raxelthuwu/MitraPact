import csv
import io
import json
import logging
import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from asgiref.sync import sync_to_async
from django.db import connection, transaction

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
from app import db

logger = logging.getLogger(__name__)


# =============================================================================
# HELPERS
# =============================================================================

def _fetchall(cursor) -> List[Dict[str, Any]]:
    cols = [c[0] for c in cursor.description]
    return [dict(zip(cols, row)) for row in cursor.fetchall()]


def _fetchone(cursor) -> Optional[Dict[str, Any]]:
    row = cursor.fetchone()
    return dict(zip([c[0] for c in cursor.description], row)) if row else None


def _str_fields(obj: Dict[str, Any]) -> Dict[str, Any]:
    import uuid
    result = {}
    for k, v in obj.items():
        if isinstance(v, uuid.UUID):
            result[k] = str(v)
        elif isinstance(v, (datetime.date, datetime.time, datetime.datetime)):
            result[k] = str(v)
        elif isinstance(v, Decimal):
            result[k] = float(v)
        else:
            result[k] = v
    return result


def _s(obj): return _str_fields(obj) if obj else None
def _sl(objs): return [_str_fields(o) for o in objs]


# =============================================================================
# REPOSITORIOS
# =============================================================================

# ── Catálogos (solo lectura) ──────────────────────────────────────────────────

class _RepoCatalogo:
    """Repositorio genérico para tablas de catálogo de solo lectura."""

    @staticmethod
    def get_all(tabla: str):
        with connection.cursor() as cur:
            cur.execute(f"SELECT codigo, descripcion FROM {tabla} ORDER BY codigo")
            return _fetchall(cur)

    @staticmethod
    def get_by_codigo(tabla: str, codigo: int):
        with connection.cursor() as cur:
            cur.execute(f"SELECT codigo, descripcion FROM {tabla} WHERE codigo = %s", [codigo])
            return _fetchone(cur)


# ── Rango de edad ─────────────────────────────────────────────────────────────

class _RepoRangoEdad:
    _T = db.rango_edad
    _F = "id, etiqueta, edad_min, edad_max"

    @classmethod
    def get_all(cls):
        with connection.cursor() as cur:
            cur.execute(f"SELECT {cls._F} FROM {cls._T} ORDER BY edad_min")
            return _fetchall(cur)

    @classmethod
    def get_by_id(cls, rango_id: str):
        with connection.cursor() as cur:
            cur.execute(f"SELECT {cls._F} FROM {cls._T} WHERE id = %s", [rango_id])
            return _fetchone(cur)

    @classmethod
    def create(cls, etiqueta, edad_min, edad_max) -> str:
        with connection.cursor() as cur:
            cur.execute(
                f"INSERT INTO {cls._T} (etiqueta, edad_min, edad_max) VALUES (%s,%s,%s) RETURNING id",
                [etiqueta, edad_min, edad_max],
            )
            return str(cur.fetchone()[0])

    @classmethod
    def update(cls, rango_id, etiqueta, edad_min, edad_max) -> bool:
        with connection.cursor() as cur:
            cur.execute(
                f"UPDATE {cls._T} SET etiqueta=%s, edad_min=%s, edad_max=%s WHERE id=%s",
                [etiqueta, edad_min, edad_max, rango_id],
            )
            return cur.rowcount > 0

    @classmethod
    def delete(cls, rango_id) -> bool:
        with connection.cursor() as cur:
            cur.execute(f"DELETE FROM {cls._T} WHERE id = %s", [rango_id])
            return cur.rowcount > 0


# ── Período estadístico ───────────────────────────────────────────────────────

class _RepoPeriodo:
    _T = db.periodo_estadistico
    _F = "id, etiqueta, fecha_inicio, fecha_fin"

    @classmethod
    def get_all(cls):
        with connection.cursor() as cur:
            cur.execute(f"SELECT {cls._F} FROM {cls._T} ORDER BY fecha_inicio DESC")
            return _fetchall(cur)

    @classmethod
    def get_by_id(cls, pid: str):
        with connection.cursor() as cur:
            cur.execute(f"SELECT {cls._F} FROM {cls._T} WHERE id = %s", [pid])
            return _fetchone(cur)

    @classmethod
    def create(cls, etiqueta, fecha_inicio, fecha_fin) -> str:
        with connection.cursor() as cur:
            cur.execute(
                f"INSERT INTO {cls._T} (etiqueta, fecha_inicio, fecha_fin) VALUES (%s,%s,%s) RETURNING id",
                [etiqueta, fecha_inicio, fecha_fin],
            )
            return str(cur.fetchone()[0])

    @classmethod
    def update(cls, pid, etiqueta, fecha_inicio, fecha_fin) -> bool:
        with connection.cursor() as cur:
            cur.execute(
                f"UPDATE {cls._T} SET etiqueta=%s, fecha_inicio=%s, fecha_fin=%s WHERE id=%s",
                [etiqueta, fecha_inicio, fecha_fin, pid],
            )
            return cur.rowcount > 0

    @classmethod
    def delete(cls, pid) -> bool:
        with connection.cursor() as cur:
            cur.execute(f"DELETE FROM {cls._T} WHERE id = %s", [pid])
            return cur.rowcount > 0


# ── Importación CSV ───────────────────────────────────────────────────────────

class _RepoImportacion:
    _T = db.importacion_csv
    _F = """id, nombre_archivo, fecha_importacion, procesado_en,
            estado, total_registros, registros_validos,
            registros_invalidos, errores_detalle"""

    @classmethod
    def get_all(cls):
        with connection.cursor() as cur:
            cur.execute(f"SELECT {cls._F} FROM {cls._T} ORDER BY fecha_importacion DESC")
            return _fetchall(cur)

    @classmethod
    def get_by_id(cls, iid: str):
        with connection.cursor() as cur:
            cur.execute(f"SELECT {cls._F} FROM {cls._T} WHERE id = %s", [iid])
            return _fetchone(cur)

    @classmethod
    def create(cls, nombre_archivo: str) -> str:
        with connection.cursor() as cur:
            cur.execute(
                f"INSERT INTO {cls._T} (nombre_archivo) VALUES (%s) RETURNING id",
                [nombre_archivo],
            )
            return str(cur.fetchone()[0])

    @classmethod
    def finalizar(cls, iid, total, validos, invalidos, errores):
        with connection.cursor() as cur:
            cur.execute(
                f"""UPDATE {cls._T}
                    SET estado='COMPLETADO', procesado_en=NOW(),
                        total_registros=%s, registros_validos=%s,
                        registros_invalidos=%s, errores_detalle=%s
                    WHERE id=%s""",
                [total, validos, invalidos, errores, iid],
            )


# ── Encuesta ──────────────────────────────────────────────────────────────────

class _RepoEncuesta:
    _T = db.encuesta
    _F = """id, importacion_id, fecha, edad, barrio, barrio_id,
            ocupacion_cod, inclinacion_voto_cod, intencion_participacion_cod,
            prob_1_cod, prob_2_cod, prob_otra, opinion_politica"""
    _CAMPOS_INSERT = [
        "importacion_id", "fecha", "edad", "barrio", "barrio_id",
        "ocupacion_cod", "inclinacion_voto_cod", "intencion_participacion_cod",
        "prob_1_cod", "prob_2_cod", "prob_otra", "opinion_politica",
    ]

    @classmethod
    def get_all(cls, importacion_id=None, barrio_id=None):
        conds, params = [], []
        if importacion_id:
            conds.append("importacion_id = %s"); params.append(importacion_id)
        if barrio_id:
            conds.append("barrio_id = %s"); params.append(barrio_id)
        where = ("WHERE " + " AND ".join(conds)) if conds else ""
        with connection.cursor() as cur:
            cur.execute(f"SELECT {cls._F} FROM {cls._T} {where} ORDER BY fecha DESC", params)
            return _fetchall(cur)

    @classmethod
    def get_by_periodo(cls, periodo_id: str):
        with connection.cursor() as cur:
            cur.execute(
                f"""SELECT e.id, e.importacion_id, e.fecha, e.edad, e.barrio, e.barrio_id,
                           e.ocupacion_cod, e.inclinacion_voto_cod, e.intencion_participacion_cod,
                           e.prob_1_cod, e.prob_2_cod, e.prob_otra, e.opinion_politica
                    FROM {cls._T} e
                    JOIN {db.periodo_estadistico} p ON e.fecha BETWEEN p.fecha_inicio AND p.fecha_fin
                    WHERE p.id = %s ORDER BY e.fecha DESC""",
                [periodo_id],
            )
            return _fetchall(cur)

    @classmethod
    def get_by_id(cls, eid: str):
        with connection.cursor() as cur:
            cur.execute(f"SELECT {cls._F} FROM {cls._T} WHERE id = %s", [eid])
            return _fetchone(cur)

    @classmethod
    def create(cls, payload: Dict) -> str:
        vals = [payload.get(c) for c in cls._CAMPOS_INSERT]
        ph = ", ".join(["%s"] * len(cls._CAMPOS_INSERT))
        with connection.cursor() as cur:
            cur.execute(
                f"INSERT INTO {cls._T} ({', '.join(cls._CAMPOS_INSERT)}) VALUES ({ph}) RETURNING id",
                vals,
            )
            return str(cur.fetchone()[0])

    @classmethod
    def update(cls, eid: str, payload: Dict) -> bool:
        allowed = set(cls._CAMPOS_INSERT) - {"importacion_id"}
        fields = {k: v for k, v in payload.items() if k in allowed}
        if not fields:
            return False
        set_clause = ", ".join(f"{k} = %s" for k in fields)
        with connection.cursor() as cur:
            cur.execute(f"UPDATE {cls._T} SET {set_clause} WHERE id = %s",
                        list(fields.values()) + [eid])
            return cur.rowcount > 0

    @classmethod
    def delete(cls, eid: str) -> bool:
        with connection.cursor() as cur:
            cur.execute(f"DELETE FROM {cls._T} WHERE id = %s", [eid])
            return cur.rowcount > 0

    @classmethod
    def bulk_insert(cls, rows: List[Dict]) -> int:
        ph = ", ".join(["%s"] * len(cls._CAMPOS_INSERT))
        inserted = 0
        with connection.cursor() as cur:
            for row in rows:
                cur.execute(
                    f"INSERT INTO {cls._T} ({', '.join(cls._CAMPOS_INSERT)}) VALUES ({ph})",
                    [row.get(c) for c in cls._CAMPOS_INSERT],
                )
                inserted += cur.rowcount
        return inserted

    @classmethod
    def agregar_por_barrio_y_periodo(cls, barrio_id: str, periodo_id: str) -> Dict:
        with connection.cursor() as cur:
            cur.execute(
                f"""SELECT
                        COUNT(*) FILTER (WHERE e.inclinacion_voto_cod = 1)       AS total_simpatizantes,
                        COUNT(*) FILTER (WHERE e.inclinacion_voto_cod = 2)       AS total_indecisos,
                        COUNT(*) FILTER (WHERE e.inclinacion_voto_cod = 3)       AS total_no_simpatizantes,
                        COUNT(*) FILTER (WHERE e.intencion_participacion_cod = 2) AS total_no_votantes,
                        COUNT(*) FILTER (WHERE e.intencion_participacion_cod = 1) AS total_intension_votar,
                        COUNT(*) FILTER (WHERE e.intencion_participacion_cod = 2) AS total_abstencion,
                        COUNT(*)                                                  AS total
                    FROM {cls._T} e
                    JOIN {db.periodo_estadistico} p ON e.fecha BETWEEN p.fecha_inicio AND p.fecha_fin
                    WHERE e.barrio_id = %s AND p.id = %s""",
                [barrio_id, periodo_id],
            )
            return _fetchone(cur)

    @classmethod
    def barrios_del_periodo(cls, periodo_id: str) -> List[str]:
        with connection.cursor() as cur:
            cur.execute(
                f"""SELECT DISTINCT e.barrio_id
                    FROM {cls._T} e
                    JOIN {db.periodo_estadistico} p ON e.fecha BETWEEN p.fecha_inicio AND p.fecha_fin
                    WHERE p.id = %s AND e.barrio_id IS NOT NULL""",
                [periodo_id],
            )
            return [str(r[0]) for r in cur.fetchall()]

    @classmethod
    def moda(cls, campo: str, barrio_id: str, periodo_id: str):
        """Retorna el valor más frecuente de un campo para barrio/período."""
        with connection.cursor() as cur:
            cur.execute(
                f"""SELECT e.{campo}
                    FROM {cls._T} e
                    JOIN {db.periodo_estadistico} p ON e.fecha BETWEEN p.fecha_inicio AND p.fecha_fin
                    WHERE e.barrio_id = %s AND p.id = %s AND e.{campo} IS NOT NULL
                    GROUP BY e.{campo} ORDER BY COUNT(*) DESC LIMIT 1""",
                [barrio_id, periodo_id],
            )
            row = cur.fetchone()
            return str(row[0]) if row else None


# ── Snapshot territorial ──────────────────────────────────────────────────────

class _RepoSnapshot:
    _T = db.snapshot_territorial
    _F = """id, barrio_id, periodo_id, total_simpatizantes, total_indecisos,
            total_no_simpatizantes, total_no_votantes, pct_simpatizantes,
            pct_indecisos, pct_no_simpatizantes, pct_no_votantes,
            total_intension_votar, total_abstencion, pct_participacion,
            indice_intervencion, generado_en"""

    @classmethod
    def get_all(cls, barrio_id=None, periodo_id=None):
        conds, params = [], []
        if barrio_id:
            conds.append("barrio_id = %s"); params.append(barrio_id)
        if periodo_id:
            conds.append("periodo_id = %s"); params.append(periodo_id)
        where = ("WHERE " + " AND ".join(conds)) if conds else ""
        with connection.cursor() as cur:
            cur.execute(f"SELECT {cls._F} FROM {cls._T} {where} ORDER BY generado_en DESC", params)
            return _fetchall(cur)

    @classmethod
    def get_by_id(cls, sid: str):
        with connection.cursor() as cur:
            cur.execute(f"SELECT {cls._F} FROM {cls._T} WHERE id = %s", [sid])
            return _fetchone(cur)

    @classmethod
    def get_pcts(cls, barrio_id: str, periodo_id: str):
        """Retorna solo los porcentajes necesarios para variación/caracterización."""
        with connection.cursor() as cur:
            cur.execute(
                f"""SELECT pct_simpatizantes, pct_indecisos, pct_no_simpatizantes,
                           pct_participacion, indice_intervencion
                    FROM {cls._T} WHERE barrio_id = %s AND periodo_id = %s""",
                [barrio_id, periodo_id],
            )
            return _fetchone(cur)

    @classmethod
    def upsert(cls, barrio_id: str, periodo_id: str, totales: Dict) -> str:
        total = totales["total"] or 0
        ts = totales["total_simpatizantes"] or 0
        ti = totales["total_indecisos"] or 0
        tns = totales["total_no_simpatizantes"] or 0
        tnv = totales["total_no_votantes"] or 0
        tiv = totales["total_intension_votar"] or 0
        tab = totales["total_abstencion"] or 0

        def pct(part, whole): return round(part / whole * 100, 2) if whole else None

        indice = round((ts / total - tns / total) * 100, 4) if total else None

        with connection.cursor() as cur:
            cur.execute(f"DELETE FROM {cls._T} WHERE barrio_id=%s AND periodo_id=%s",
                        [barrio_id, periodo_id])
            cur.execute(
                f"""INSERT INTO {cls._T}
                    (barrio_id, periodo_id, total_simpatizantes, total_indecisos,
                     total_no_simpatizantes, total_no_votantes, pct_simpatizantes,
                     pct_indecisos, pct_no_simpatizantes, pct_no_votantes,
                     total_intension_votar, total_abstencion, pct_participacion, indice_intervencion)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
                [barrio_id, periodo_id, ts, ti, tns, tnv,
                 pct(ts, total), pct(ti, total), pct(tns, total), pct(tnv, total),
                 tiv, tab, pct(tiv, total), indice],
            )
            return str(cur.fetchone()[0])

    @classmethod
    def delete(cls, sid: str) -> bool:
        with connection.cursor() as cur:
            cur.execute(f"DELETE FROM {cls._T} WHERE id = %s", [sid])
            return cur.rowcount > 0


# ── Variación temporal ────────────────────────────────────────────────────────

class _RepoVariacion:
    _T = db.variacion_temporal
    _F = """id, barrio_id, periodo_anterior_id, periodo_actual_id,
            variacion_simpatizantes, variacion_indecisos,
            variacion_no_simpatizantes, variacion_participacion, cambio_significativo"""

    @classmethod
    def get_all(cls, barrio_id=None, periodo_actual_id=None):
        conds, params = [], []
        if barrio_id:
            conds.append("barrio_id = %s"); params.append(barrio_id)
        if periodo_actual_id:
            conds.append("periodo_actual_id = %s"); params.append(periodo_actual_id)
        where = ("WHERE " + " AND ".join(conds)) if conds else ""
        with connection.cursor() as cur:
            cur.execute(f"SELECT {cls._F} FROM {cls._T} {where}", params)
            return _fetchall(cur)

    @classmethod
    def get_by_id(cls, vid: str):
        with connection.cursor() as cur:
            cur.execute(f"SELECT {cls._F} FROM {cls._T} WHERE id = %s", [vid])
            return _fetchone(cur)

    @classmethod
    def upsert(cls, barrio_id, periodo_ant, periodo_act,
               var_simp, var_ind, var_no_simp, var_part, cambio) -> str:
        with connection.cursor() as cur:
            cur.execute(
                f"DELETE FROM {cls._T} WHERE barrio_id=%s AND periodo_anterior_id=%s AND periodo_actual_id=%s",
                [barrio_id, periodo_ant, periodo_act],
            )
            cur.execute(
                f"""INSERT INTO {cls._T}
                    (barrio_id, periodo_anterior_id, periodo_actual_id,
                     variacion_simpatizantes, variacion_indecisos,
                     variacion_no_simpatizantes, variacion_participacion, cambio_significativo)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
                [barrio_id, periodo_ant, periodo_act, var_simp, var_ind, var_no_simp, var_part, cambio],
            )
            return str(cur.fetchone()[0])


# ── Ranking problemática ──────────────────────────────────────────────────────

class _RepoRanking:
    _T = db.ranking_problematica
    _F = "id, periodo_id, barrio_id, problematica_cod, frecuencia, pct_frecuencia, posicion_ranking"

    @classmethod
    def get_all(cls, periodo_id=None, barrio_id=None):
        conds, params = [], []
        if periodo_id:
            conds.append("periodo_id = %s"); params.append(periodo_id)
        if barrio_id:
            conds.append("barrio_id = %s"); params.append(barrio_id)
        where = ("WHERE " + " AND ".join(conds)) if conds else ""
        with connection.cursor() as cur:
            cur.execute(f"SELECT {cls._F} FROM {cls._T} {where} ORDER BY posicion_ranking", params)
            return _fetchall(cur)

    @classmethod
    def get_by_id(cls, rid: str):
        with connection.cursor() as cur:
            cur.execute(f"SELECT {cls._F} FROM {cls._T} WHERE id = %s", [rid])
            return _fetchone(cur)

    @classmethod
    def calcular_y_persistir(cls, barrio_id: str, periodo_id: str) -> List[Dict]:
        """Calcula frecuencias desde encuestas y reemplaza el ranking del barrio/período."""
        with connection.cursor() as cur:
            cur.execute(
                f"""WITH problemas AS (
                        SELECT prob_1_cod AS cod FROM {db.encuesta} e
                        JOIN {db.periodo_estadistico} p ON e.fecha BETWEEN p.fecha_inicio AND p.fecha_fin
                        WHERE e.barrio_id=%s AND p.id=%s AND prob_1_cod IS NOT NULL
                        UNION ALL
                        SELECT prob_2_cod FROM {db.encuesta} e
                        JOIN {db.periodo_estadistico} p ON e.fecha BETWEEN p.fecha_inicio AND p.fecha_fin
                        WHERE e.barrio_id=%s AND p.id=%s AND prob_2_cod IS NOT NULL
                    ),
                    conteo AS (SELECT cod, COUNT(*) AS frec FROM problemas GROUP BY cod),
                    total  AS (SELECT SUM(frec) AS t FROM conteo)
                    SELECT cod, frec, ROUND(frec::DECIMAL/t*100,2) AS pct,
                           ROW_NUMBER() OVER (ORDER BY frec DESC) AS pos
                    FROM conteo, total ORDER BY pos""",
                [barrio_id, periodo_id, barrio_id, periodo_id],
            )
            filas = _fetchall(cur)

            cur.execute(f"DELETE FROM {cls._T} WHERE barrio_id=%s AND periodo_id=%s",
                        [barrio_id, periodo_id])
            for f in filas:
                cur.execute(
                    f"""INSERT INTO {cls._T}
                        (barrio_id, periodo_id, problematica_cod, frecuencia, pct_frecuencia, posicion_ranking)
                        VALUES (%s,%s,%s,%s,%s,%s)""",
                    [barrio_id, periodo_id, f["cod"], f["frec"], f["pct"], f["pos"]],
                )
        return cls.get_all(periodo_id, barrio_id)

    @classmethod
    def top1_cod(cls, barrio_id: str, periodo_id: str) -> Optional[int]:
        with connection.cursor() as cur:
            cur.execute(
                f"SELECT problematica_cod FROM {cls._T} WHERE barrio_id=%s AND periodo_id=%s ORDER BY posicion_ranking LIMIT 1",
                [barrio_id, periodo_id],
            )
            row = cur.fetchone()
            return row[0] if row else None


# ── Resultado cruce ───────────────────────────────────────────────────────────

class _RepoCruce:
    _T = db.resultado_cruce
    _F = "id, periodo_id, dimension_a, valor_a, dimension_b, valor_b, cantidad, porcentaje, generado_en"
    _DIMS = {
        "ocupacion": "ocupacion_cod",
        "inclinacion_voto": "inclinacion_voto_cod",
        "intencion_participacion": "intencion_participacion_cod",
        "problematica_1": "prob_1_cod",
        "problematica_2": "prob_2_cod",
    }

    @classmethod
    def get_all(cls, periodo_id: str):
        with connection.cursor() as cur:
            cur.execute(
                f"SELECT {cls._F} FROM {cls._T} WHERE periodo_id=%s ORDER BY generado_en DESC",
                [periodo_id],
            )
            return _fetchall(cur)

    @classmethod
    def get_by_id(cls, cid: str):
        with connection.cursor() as cur:
            cur.execute(f"SELECT {cls._F} FROM {cls._T} WHERE id = %s", [cid])
            return _fetchone(cur)

    @classmethod
    def calcular_y_persistir(cls, periodo_id: str, dim_a: str, dim_b: str) -> List[Dict]:
        col_a = cls._DIMS.get(dim_a)
        col_b = cls._DIMS.get(dim_b)
        if not col_a or not col_b:
            raise ValueError(f"Dimensiones inválidas: {dim_a}, {dim_b}")
        with connection.cursor() as cur:
            cur.execute(
                f"""WITH base AS (
                        SELECT e.{col_a} AS va, e.{col_b} AS vb
                        FROM {db.encuesta} e
                        JOIN {db.periodo_estadistico} p ON e.fecha BETWEEN p.fecha_inicio AND p.fecha_fin
                        WHERE p.id=%s AND e.{col_a} IS NOT NULL AND e.{col_b} IS NOT NULL
                    ),
                    total AS (SELECT COUNT(*) AS t FROM base),
                    cruce AS (SELECT va, vb, COUNT(*) AS cantidad FROM base GROUP BY va, vb)
                    SELECT va, vb, cantidad, ROUND(cantidad::DECIMAL/t*100,2) AS porcentaje
                    FROM cruce, total ORDER BY cantidad DESC""",
                [periodo_id],
            )
            filas = _fetchall(cur)

            cur.execute(
                f"DELETE FROM {cls._T} WHERE periodo_id=%s AND dimension_a=%s AND dimension_b=%s",
                [periodo_id, dim_a, dim_b],
            )
            for f in filas:
                cur.execute(
                    f"""INSERT INTO {cls._T}
                        (periodo_id, dimension_a, valor_a, dimension_b, valor_b, cantidad, porcentaje)
                        VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                    [periodo_id, dim_a, str(f["va"]), dim_b, str(f["vb"]), f["cantidad"], f["porcentaje"]],
                )
        return cls.get_all(periodo_id)

    @classmethod
    def delete_by_periodo(cls, periodo_id: str) -> int:
        with connection.cursor() as cur:
            cur.execute(f"DELETE FROM {cls._T} WHERE periodo_id=%s", [periodo_id])
            return cur.rowcount


# ── Caracterización territorial ───────────────────────────────────────────────

class _RepoCaracterizacion:
    _T = db.caracterizacion_territorial
    _F = """id, barrio_id, periodo_id, afinidad_predominante, ocupacion_predominante,
            problematica_predominante_cod, participacion_predominante,
            pct_indecision, pct_apoyo, cantidad_eventos,
            frecuencia_problematicas, es_prioritario, alto_potencial_crecimiento, generado_en"""

    @classmethod
    def get_all(cls, barrio_id=None, periodo_id=None):
        conds, params = [], []
        if barrio_id:
            conds.append("barrio_id = %s"); params.append(barrio_id)
        if periodo_id:
            conds.append("periodo_id = %s"); params.append(periodo_id)
        where = ("WHERE " + " AND ".join(conds)) if conds else ""
        with connection.cursor() as cur:
            cur.execute(f"SELECT {cls._F} FROM {cls._T} {where} ORDER BY generado_en DESC", params)
            return _fetchall(cur)

    @classmethod
    def get_by_id(cls, cid: str):
        with connection.cursor() as cur:
            cur.execute(f"SELECT {cls._F} FROM {cls._T} WHERE id = %s", [cid])
            return _fetchone(cur)

    @classmethod
    def cantidad_eventos(cls, barrio_id: str) -> int:
        with connection.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) FROM {db.evento} WHERE barrio_id=%s", [barrio_id])
            return cur.fetchone()[0] or 0

    @classmethod
    def upsert(cls, barrio_id: str, periodo_id: str, datos: Dict) -> str:
        with connection.cursor() as cur:
            cur.execute(f"DELETE FROM {cls._T} WHERE barrio_id=%s AND periodo_id=%s",
                        [barrio_id, periodo_id])
            cur.execute(
                f"""INSERT INTO {cls._T}
                    (barrio_id, periodo_id, afinidad_predominante, ocupacion_predominante,
                     problematica_predominante_cod, participacion_predominante,
                     pct_indecision, pct_apoyo, cantidad_eventos,
                     frecuencia_problematicas, es_prioritario, alto_potencial_crecimiento)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
                [barrio_id, periodo_id,
                 datos.get("afinidad_predominante"), datos.get("ocupacion_predominante"),
                 datos.get("problematica_predominante_cod"), datos.get("participacion_predominante"),
                 datos.get("pct_indecision"), datos.get("pct_apoyo"),
                 datos.get("cantidad_eventos", 0), datos.get("frecuencia_problematicas"),
                 datos.get("es_prioritario", False), datos.get("alto_potencial_crecimiento", False)],
            )
            return str(cur.fetchone()[0])


# ── Exportación resultado ─────────────────────────────────────────────────────

class _RepoExportacion:
    _T = db.exportacion_resultado
    _F = "id, periodo_id, tipo_analisis, formato, ruta_archivo, generado_en, coordinador_id"

    @classmethod
    def get_all(cls, periodo_id=None):
        where = "WHERE periodo_id=%s" if periodo_id else ""
        params = [periodo_id] if periodo_id else []
        with connection.cursor() as cur:
            cur.execute(f"SELECT {cls._F} FROM {cls._T} {where} ORDER BY generado_en DESC", params)
            return _fetchall(cur)

    @classmethod
    def get_by_id(cls, eid: str):
        with connection.cursor() as cur:
            cur.execute(f"SELECT {cls._F} FROM {cls._T} WHERE id = %s", [eid])
            return _fetchone(cur)

    @classmethod
    def create(cls, periodo_id, tipo, formato, ruta, coordinador_id) -> str:
        with connection.cursor() as cur:
            cur.execute(
                f"INSERT INTO {cls._T} (periodo_id, tipo_analisis, formato, ruta_archivo, coordinador_id) VALUES (%s,%s,%s,%s,%s) RETURNING id",
                [periodo_id, tipo, formato, ruta, coordinador_id],
            )
            return str(cur.fetchone()[0])


# ── Resumen estadístico ───────────────────────────────────────────────────────

class _RepoResumen:
    _T = db.resumen_estadistico
    _F = "id, periodo_id, barrio_id, resumen_texto, generado_en"

    @classmethod
    def get_all(cls, barrio_id=None, periodo_id=None):
        conds, params = [], []
        if barrio_id:
            conds.append("barrio_id = %s"); params.append(barrio_id)
        if periodo_id:
            conds.append("periodo_id = %s"); params.append(periodo_id)
        where = ("WHERE " + " AND ".join(conds)) if conds else ""
        with connection.cursor() as cur:
            cur.execute(f"SELECT {cls._F} FROM {cls._T} {where} ORDER BY generado_en DESC", params)
            return _fetchall(cur)

    @classmethod
    def get_by_id(cls, rid: str):
        with connection.cursor() as cur:
            cur.execute(f"SELECT {cls._F} FROM {cls._T} WHERE id = %s", [rid])
            return _fetchone(cur)

    @classmethod
    def upsert(cls, barrio_id: str, periodo_id: str, texto: str) -> str:
        with connection.cursor() as cur:
            cur.execute(f"DELETE FROM {cls._T} WHERE barrio_id=%s AND periodo_id=%s",
                        [barrio_id, periodo_id])
            cur.execute(
                f"INSERT INTO {cls._T} (periodo_id, barrio_id, resumen_texto) VALUES (%s,%s,%s) RETURNING id",
                [periodo_id, barrio_id, texto],
            )
            return str(cur.fetchone()[0])


# =============================================================================
# HELPERS INTERNOS DE CÁLCULO
# =============================================================================

def _diff_pct(ant: Dict, act: Dict, key: str) -> Optional[float]:
    a, b = ant.get(key), act.get(key)
    return round(float(b) - float(a), 4) if (a is not None and b is not None) else None


def _calcular_variacion_barrio(barrio_id: str, periodo_ant: str, periodo_act: str) -> str:
    ant = _RepoSnapshot.get_pcts(barrio_id, periodo_ant) or {}
    act = _RepoSnapshot.get_pcts(barrio_id, periodo_act) or {}
    var_simp = _diff_pct(ant, act, "pct_simpatizantes")
    var_ind = _diff_pct(ant, act, "pct_indecisos")
    var_no_simp = _diff_pct(ant, act, "pct_no_simpatizantes")
    var_part = _diff_pct(ant, act, "pct_participacion")
    cambio = abs(var_simp) > 5.0 if var_simp is not None else False
    return _RepoVariacion.upsert(barrio_id, periodo_ant, periodo_act,
                                  var_simp, var_ind, var_no_simp, var_part, cambio)


def _calcular_caracterizacion_barrio(barrio_id: str, periodo_id: str) -> str:
    snap = _RepoSnapshot.get_pcts(barrio_id, periodo_id) or {}
    pct_simp = float(snap.get("pct_simpatizantes") or 0)
    pct_ind = float(snap.get("pct_indecisos") or 0)
    pct_no_simp = float(snap.get("pct_no_simpatizantes") or 0)
    indice = float(snap.get("indice_intervencion") or 0)
    afinidad = max(
        [("SIMPATIZANTE", pct_simp), ("INDECISO", pct_ind), ("NO_SIMPATIZANTE", pct_no_simp)],
        key=lambda x: x[1],
    )[0]
    datos = {
        "afinidad_predominante": afinidad,
        "ocupacion_predominante": _RepoEncuesta.moda("ocupacion_cod", barrio_id, periodo_id),
        "problematica_predominante_cod": _RepoRanking.top1_cod(barrio_id, periodo_id),
        "participacion_predominante": _RepoEncuesta.moda("intencion_participacion_cod", barrio_id, periodo_id),
        "pct_indecision": round(pct_ind, 2),
        "pct_apoyo": round(pct_simp, 2),
        "cantidad_eventos": _RepoCaracterizacion.cantidad_eventos(barrio_id),
        "frecuencia_problematicas": round(indice, 4) if indice else None,
        "es_prioritario": pct_no_simp > 40.0 or pct_ind > 35.0,
        "alto_potencial_crecimiento": pct_ind > 25.0 and indice > 0,
    }
    return _RepoCaracterizacion.upsert(barrio_id, periodo_id, datos)


# =============================================================================
# SERVICIOS
# =============================================================================

# ── Catálogos ─────────────────────────────────────────────────────────────────

class _CatalogoBaseService:
    _tabla: str = ""

    async def listar(self) -> List[Dict]:
        return _sl(await sync_to_async(_RepoCatalogo.get_all)(self._tabla))

    async def obtener(self, codigo: int) -> Optional[Dict]:
        return _s(await sync_to_async(_RepoCatalogo.get_by_codigo)(self._tabla, codigo))


class CatalogoOcupacionService(_CatalogoBaseService, ICatalogoOcupacionService):
    _tabla = db.catalogo_ocupacion


class CatalogoInclinacionVotoService(_CatalogoBaseService, ICatalogoInclinacionVotoService):
    _tabla = db.catalogo_inclinacion_voto


class CatalogoIntencionParticipacionService(_CatalogoBaseService, ICatalogoIntencionParticipacionService):
    _tabla = db.catalogo_intencion_participacion


class CatalogoProblematicaService(_CatalogoBaseService, ICatalogoProblematicaService):
    _tabla = db.catalogo_problematica


# ── Rango de edad ─────────────────────────────────────────────────────────────

class RangoEdadService(IRangoEdadService):

    async def listar(self) -> List[Dict]:
        return _sl(await sync_to_async(_RepoRangoEdad.get_all)())

    async def obtener(self, rango_id: str) -> Optional[Dict]:
        return _s(await sync_to_async(_RepoRangoEdad.get_by_id)(rango_id))

    async def crear(self, etiqueta, edad_min, edad_max) -> Dict:
        rid = await sync_to_async(_RepoRangoEdad.create)(etiqueta, edad_min, edad_max)
        return _s(await sync_to_async(_RepoRangoEdad.get_by_id)(rid))

    async def actualizar(self, rango_id, etiqueta, edad_min, edad_max) -> Optional[Dict]:
        await sync_to_async(_RepoRangoEdad.update)(rango_id, etiqueta, edad_min, edad_max)
        return _s(await sync_to_async(_RepoRangoEdad.get_by_id)(rango_id))

    async def eliminar(self, rango_id: str) -> bool:
        return await sync_to_async(_RepoRangoEdad.delete)(rango_id)


# ── Período estadístico ───────────────────────────────────────────────────────

class PeriodoEstadisticoService(IPeriodoEstadisticoService):

    async def listar(self) -> List[Dict]:
        return _sl(await sync_to_async(_RepoPeriodo.get_all)())

    async def obtener(self, periodo_id: str) -> Optional[Dict]:
        return _s(await sync_to_async(_RepoPeriodo.get_by_id)(periodo_id))

    async def crear(self, etiqueta, fecha_inicio, fecha_fin) -> Dict:
        pid = await sync_to_async(_RepoPeriodo.create)(etiqueta, fecha_inicio, fecha_fin)
        return _s(await sync_to_async(_RepoPeriodo.get_by_id)(pid))

    async def actualizar(self, periodo_id, etiqueta, fecha_inicio, fecha_fin) -> Optional[Dict]:
        await sync_to_async(_RepoPeriodo.update)(periodo_id, etiqueta, fecha_inicio, fecha_fin)
        return _s(await sync_to_async(_RepoPeriodo.get_by_id)(periodo_id))

    async def eliminar(self, periodo_id: str) -> bool:
        return await sync_to_async(_RepoPeriodo.delete)(periodo_id)


# ── Importación CSV ───────────────────────────────────────────────────────────

class ImportacionCsvService(IImportacionCsvService):

    _REQUERIDAS = {
        "fecha", "edad", "barrio_id", "ocupacion_cod",
        "inclinacion_voto_cod", "intencion_participacion_cod", "prob_1_cod",
    }

    async def listar(self) -> List[Dict]:
        return _sl(await sync_to_async(_RepoImportacion.get_all)())

    async def obtener(self, importacion_id: str) -> Optional[Dict]:
        return _s(await sync_to_async(_RepoImportacion.get_by_id)(importacion_id))

    async def importar(self, archivo_csv: Any) -> Dict:
        nombre = getattr(archivo_csv, "name", "sin_nombre.csv")

        def _procesar():
            iid = _RepoImportacion.create(nombre)
            validos, invalidos, errores = [], [], []

            contenido = archivo_csv.read()
            if isinstance(contenido, bytes):
                contenido = contenido.decode("utf-8", errors="replace")

            for i, fila in enumerate(csv.DictReader(io.StringIO(contenido)), start=2):
                faltantes = self._REQUERIDAS - set(fila.keys())
                if faltantes:
                    errores.append(f"Fila {i}: columnas faltantes {faltantes}")
                    invalidos.append(fila)
                    continue
                try:
                    def _int(v): return int(v) if v and v.strip() else None
                    validos.append({
                        "importacion_id": iid,
                        "fecha": fila["fecha"].strip(),
                        "edad": int(fila["edad"]),
                        "barrio": fila.get("barrio", "").strip() or None,
                        "barrio_id": fila.get("barrio_id", "").strip() or None,
                        "ocupacion_cod": _int(fila.get("ocupacion_cod")),
                        "inclinacion_voto_cod": _int(fila.get("inclinacion_voto_cod")),
                        "intencion_participacion_cod": _int(fila.get("intencion_participacion_cod")),
                        "prob_1_cod": _int(fila.get("prob_1_cod")),
                        "prob_2_cod": _int(fila.get("prob_2_cod")),
                        "prob_otra": fila.get("prob_otra", "").strip() or None,
                        "opinion_politica": fila.get("opinion_politica", "").strip() or None,
                    })
                except (ValueError, KeyError) as e:
                    errores.append(f"Fila {i}: {e}")
                    invalidos.append(fila)

            with transaction.atomic():
                if validos:
                    _RepoEncuesta.bulk_insert(validos)
                _RepoImportacion.finalizar(
                    iid, len(validos) + len(invalidos),
                    len(validos), len(invalidos),
                    "\n".join(errores) if errores else None,
                )
            return _RepoImportacion.get_by_id(iid)

        return _s(await sync_to_async(_procesar)())

    async def obtener_estado(self, importacion_id: str) -> Optional[Dict]:
        return await self.obtener(importacion_id)


# ── Encuesta ──────────────────────────────────────────────────────────────────

class EncuestaService(IEncuestaService):

    async def listar(self, importacion_id=None, barrio_id=None, periodo_id=None) -> List[Dict]:
        def _q():
            return (_RepoEncuesta.get_by_periodo(periodo_id) if periodo_id
                    else _RepoEncuesta.get_all(importacion_id, barrio_id))
        return _sl(await sync_to_async(_q)())

    async def obtener(self, encuesta_id: str) -> Optional[Dict]:
        return _s(await sync_to_async(_RepoEncuesta.get_by_id)(encuesta_id))

    async def crear(self, payload: Dict) -> Dict:
        eid = await sync_to_async(_RepoEncuesta.create)(payload)
        return _s(await sync_to_async(_RepoEncuesta.get_by_id)(eid))

    async def actualizar(self, encuesta_id: str, payload: Dict) -> Optional[Dict]:
        await sync_to_async(_RepoEncuesta.update)(encuesta_id, payload)
        return _s(await sync_to_async(_RepoEncuesta.get_by_id)(encuesta_id))

    async def eliminar(self, encuesta_id: str) -> bool:
        return await sync_to_async(_RepoEncuesta.delete)(encuesta_id)


# ── Snapshot territorial ──────────────────────────────────────────────────────

class SnapshotTerritorialService(ISnapshotTerritorialService):

    async def listar(self, barrio_id=None, periodo_id=None) -> List[Dict]:
        return _sl(await sync_to_async(_RepoSnapshot.get_all)(barrio_id, periodo_id))

    async def obtener(self, snapshot_id: str) -> Optional[Dict]:
        return _s(await sync_to_async(_RepoSnapshot.get_by_id)(snapshot_id))

    async def generar(self, barrio_id: str, periodo_id: str) -> Dict:
        def _gen():
            totales = _RepoEncuesta.agregar_por_barrio_y_periodo(barrio_id, periodo_id)
            sid = _RepoSnapshot.upsert(barrio_id, periodo_id, totales)
            return _RepoSnapshot.get_by_id(sid)
        return _s(await sync_to_async(_gen)())

    async def generar_todos(self, periodo_id: str) -> List[Dict]:
        def _gen_todos():
            return [
                _RepoSnapshot.get_by_id(
                    _RepoSnapshot.upsert(bid, periodo_id,
                                         _RepoEncuesta.agregar_por_barrio_y_periodo(bid, periodo_id))
                )
                for bid in _RepoEncuesta.barrios_del_periodo(periodo_id)
            ]
        return _sl(await sync_to_async(_gen_todos)())

    async def eliminar(self, snapshot_id: str) -> bool:
        return await sync_to_async(_RepoSnapshot.delete)(snapshot_id)


# ── Variación temporal ────────────────────────────────────────────────────────

class VariacionTemporalService(IVariacionTemporalService):

    async def listar(self, barrio_id=None, periodo_actual_id=None) -> List[Dict]:
        return _sl(await sync_to_async(_RepoVariacion.get_all)(barrio_id, periodo_actual_id))

    async def obtener(self, variacion_id: str) -> Optional[Dict]:
        return _s(await sync_to_async(_RepoVariacion.get_by_id)(variacion_id))

    async def calcular(self, barrio_id: str, periodo_anterior_id: str, periodo_actual_id: str) -> Dict:
        def _calc():
            vid = _calcular_variacion_barrio(barrio_id, periodo_anterior_id, periodo_actual_id)
            return _RepoVariacion.get_by_id(vid)
        return _s(await sync_to_async(_calc)())

    async def calcular_todos(self, periodo_anterior_id: str, periodo_actual_id: str) -> List[Dict]:
        def _todos():
            return [
                _RepoVariacion.get_by_id(
                    _calcular_variacion_barrio(bid, periodo_anterior_id, periodo_actual_id)
                )
                for bid in _RepoEncuesta.barrios_del_periodo(periodo_actual_id)
            ]
        return _sl(await sync_to_async(_todos)())


# ── Ranking problemática ──────────────────────────────────────────────────────

class RankingProblematicaService(IRankingProblematicaService):

    async def listar(self, periodo_id=None, barrio_id=None) -> List[Dict]:
        return _sl(await sync_to_async(_RepoRanking.get_all)(periodo_id, barrio_id))

    async def obtener(self, ranking_id: str) -> Optional[Dict]:
        return _s(await sync_to_async(_RepoRanking.get_by_id)(ranking_id))

    async def calcular(self, barrio_id: str, periodo_id: str) -> List[Dict]:
        return _sl(await sync_to_async(_RepoRanking.calcular_y_persistir)(barrio_id, periodo_id))

    async def calcular_todos(self, periodo_id: str) -> List[Dict]:
        def _todos():
            resultados = []
            for bid in _RepoEncuesta.barrios_del_periodo(periodo_id):
                resultados.extend(_RepoRanking.calcular_y_persistir(bid, periodo_id))
            return resultados
        return _sl(await sync_to_async(_todos)())


# ── Resultado cruce ───────────────────────────────────────────────────────────

class ResultadoCruceService(IResultadoCruceService):

    async def listar(self, periodo_id: str) -> List[Dict]:
        return _sl(await sync_to_async(_RepoCruce.get_all)(periodo_id))

    async def obtener(self, cruce_id: str) -> Optional[Dict]:
        return _s(await sync_to_async(_RepoCruce.get_by_id)(cruce_id))

    async def calcular(self, periodo_id: str, dimension_a: str, dimension_b: str) -> List[Dict]:
        return _sl(await sync_to_async(_RepoCruce.calcular_y_persistir)(periodo_id, dimension_a, dimension_b))

    async def calcular_multiples(self, periodo_id: str, cruces: List[Dict[str, str]]) -> List[Dict]:
        def _multi():
            for cruce in cruces:
                _RepoCruce.calcular_y_persistir(periodo_id, cruce["dimension_a"], cruce["dimension_b"])
            return _RepoCruce.get_all(periodo_id)
        return _sl(await sync_to_async(_multi)())

    async def eliminar_por_periodo(self, periodo_id: str) -> int:
        return await sync_to_async(_RepoCruce.delete_by_periodo)(periodo_id)


# ── Caracterización territorial ───────────────────────────────────────────────

class CaracterizacionTerritorialService(ICaracterizacionTerritorialService):

    async def listar(self, barrio_id=None, periodo_id=None) -> List[Dict]:
        return _sl(await sync_to_async(_RepoCaracterizacion.get_all)(barrio_id, periodo_id))

    async def obtener(self, caracterizacion_id: str) -> Optional[Dict]:
        return _s(await sync_to_async(_RepoCaracterizacion.get_by_id)(caracterizacion_id))

    async def generar(self, barrio_id: str, periodo_id: str) -> Dict:
        def _gen():
            cid = _calcular_caracterizacion_barrio(barrio_id, periodo_id)
            return _RepoCaracterizacion.get_by_id(cid)
        return _s(await sync_to_async(_gen)())

    async def generar_todos(self, periodo_id: str) -> List[Dict]:
        def _todos():
            return [
                _RepoCaracterizacion.get_by_id(
                    _calcular_caracterizacion_barrio(bid, periodo_id)
                )
                for bid in _RepoEncuesta.barrios_del_periodo(periodo_id)
            ]
        return _sl(await sync_to_async(_todos)())


# ── Exportación resultado ─────────────────────────────────────────────────────

class ExportacionResultadoService(IExportacionResultadoService):

    _FUENTES = {
        "snapshot": lambda pid: _RepoSnapshot.get_all(periodo_id=pid),
        "variacion": lambda pid: _RepoVariacion.get_all(periodo_actual_id=pid),
        "ranking": lambda pid: _RepoRanking.get_all(periodo_id=pid),
        "cruce": lambda pid: _RepoCruce.get_all(pid),
        "caracterizacion": lambda pid: _RepoCaracterizacion.get_all(periodo_id=pid),
    }

    async def listar(self, periodo_id=None) -> List[Dict]:
        return _sl(await sync_to_async(_RepoExportacion.get_all)(periodo_id))

    async def obtener(self, exportacion_id: str) -> Optional[Dict]:
        return _s(await sync_to_async(_RepoExportacion.get_by_id)(exportacion_id))

    async def exportar(self, periodo_id: str, tipo_analisis: str, formato: str,
                       coordinador_id: Optional[str] = None) -> Dict:
        def _exportar():
            fuente = self._FUENTES.get(tipo_analisis)
            if not fuente:
                raise ValueError(f"tipo_analisis inválido: '{tipo_analisis}'")

            datos = _sl(fuente(periodo_id))
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre = f"exportacion_{tipo_analisis}_{periodo_id[:8]}_{ts}"
            fmt = formato.upper()

            if fmt == "JSON":
                ruta = f"/tmp/{nombre}.json"
                with open(ruta, "w", encoding="utf-8") as f:
                    json.dump(datos, f, ensure_ascii=False, indent=2)
            elif fmt == "CSV":
                ruta = f"/tmp/{nombre}.csv"
                with open(ruta, "w", newline="", encoding="utf-8") as f:
                    if datos:
                        writer = csv.DictWriter(f, fieldnames=datos[0].keys())
                        writer.writeheader()
                        writer.writerows(datos)
            else:
                raise ValueError(f"formato inválido: '{formato}'. Use CSV o JSON.")

            eid = _RepoExportacion.create(periodo_id, tipo_analisis, fmt, ruta, coordinador_id)
            return _RepoExportacion.get_by_id(eid)

        return _s(await sync_to_async(_exportar)())


# ── Resumen estadístico ───────────────────────────────────────────────────────

class ResumenEstadisticoService(IResumenEstadisticoService):

    async def listar(self, barrio_id=None, periodo_id=None) -> List[Dict]:
        return _sl(await sync_to_async(_RepoResumen.get_all)(barrio_id, periodo_id))

    async def obtener(self, resumen_id: str) -> Optional[Dict]:
        return _s(await sync_to_async(_RepoResumen.get_by_id)(resumen_id))

    async def generar(self, barrio_id: str, periodo_id: str) -> Dict:
        def _gen():
            snap = next(iter(_RepoSnapshot.get_all(barrio_id, periodo_id)), None)
            caract = next(iter(_RepoCaracterizacion.get_all(barrio_id, periodo_id)), None)
            ranking = _RepoRanking.get_all(periodo_id, barrio_id)[:3]

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
                lineas.append("Top problemáticas: " + ", ".join(
                    f"#{r['posicion_ranking']} cod={r['problematica_cod']} ({r['pct_frecuencia']}%)"
                    for r in ranking
                ))

            rid = _RepoResumen.upsert(barrio_id, periodo_id, "\n".join(lineas))
            return _RepoResumen.get_by_id(rid)

        return _s(await sync_to_async(_gen)())

    async def generar_todos(self, periodo_id: str) -> List[Dict]:
        def _todos():
            return [
                _RepoResumen.get_by_id(
                    _RepoResumen.upsert(
                        bid, periodo_id,
                        # reutiliza la lógica inline ya que _gen es síncrona aquí
                        _construir_texto_resumen(bid, periodo_id)
                    )
                )
                for bid in _RepoEncuesta.barrios_del_periodo(periodo_id)
            ]
        return _sl(await sync_to_async(_todos)())


def _construir_texto_resumen(barrio_id: str, periodo_id: str) -> str:
    snap = next(iter(_RepoSnapshot.get_all(barrio_id, periodo_id)), None)
    caract = next(iter(_RepoCaracterizacion.get_all(barrio_id, periodo_id)), None)
    ranking = _RepoRanking.get_all(periodo_id, barrio_id)[:3]
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
        lineas.append("Top problemáticas: " + ", ".join(
            f"#{r['posicion_ranking']} cod={r['problematica_cod']} ({r['pct_frecuencia']}%)"
            for r in ranking
        ))
    return "\n".join(lineas)