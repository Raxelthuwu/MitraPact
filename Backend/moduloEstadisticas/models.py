import uuid
import datetime
import logging
from decimal import Decimal
from itertools import chain
from typing import Any, Dict, List, Optional

from django.db import connection, transaction

import app.db as db

# =============================================================================
# LOGGER
# =============================================================================

logger = logging.getLogger(__name__)

# =============================================================================
# HELPERS DE SERIALIZACIÓN Y CURSOR
# =============================================================================

def _fetchall(cursor) -> List[Dict[str, Any]]:
    cols = [c[0] for c in cursor.description]
    return [dict(zip(cols, row)) for row in cursor.fetchall()]


def _fetchone(cursor) -> Optional[Dict[str, Any]]:
    row = cursor.fetchone()
    return dict(zip([c[0] for c in cursor.description], row)) if row else None


def _str_fields(obj: Dict[str, Any]) -> Dict[str, Any]:
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


# =============================================================================
# CATÁLOGOS  (PK = integer codigo, sin UUID)
# =============================================================================

class CatalogoOcupacion:
    TABLE = db.catalogo_ocupacion

    @classmethod
    def listar(cls) -> List[Dict]:
        logger.info("[CatalogoOcupacion.listar] Consultando todos los registros.")
        with connection.cursor() as cur:
            cur.execute(f"SELECT codigo, descripcion FROM {cls.TABLE} ORDER BY codigo")
            result = _fetchall(cur)
        logger.info("[CatalogoOcupacion.listar] %d registros encontrados.", len(result))
        return result

    @classmethod
    def obtener(cls, codigo: int) -> Optional[Dict]:
        logger.info("[CatalogoOcupacion.obtener] Buscando codigo=%s.", codigo)
        with connection.cursor() as cur:
            cur.execute(
                f"SELECT codigo, descripcion FROM {cls.TABLE} WHERE codigo = %s",
                [codigo],
            )
            result = _fetchone(cur)
        if result:
            logger.info("[CatalogoOcupacion.obtener] Registro encontrado.")
        else:
            logger.warning("[CatalogoOcupacion.obtener] No se encontró codigo=%s.", codigo)
        return result

    @classmethod
    def crear(cls, codigo: int, descripcion: str) -> Dict:
        logger.info("[CatalogoOcupacion.crear] Creando codigo=%s descripcion='%s'.", codigo, descripcion)
        with connection.cursor() as cur:
            cur.execute(
                f"INSERT INTO {cls.TABLE} (codigo, descripcion) VALUES (%s, %s)",
                [codigo, descripcion],
            )
        logger.info("[CatalogoOcupacion.crear] Registro creado codigo=%s.", codigo)
        return {"codigo": codigo, "descripcion": descripcion}

    @classmethod
    def actualizar(cls, codigo: int, descripcion: str) -> bool:
        logger.info("[CatalogoOcupacion.actualizar] Actualizando codigo=%s.", codigo)
        with connection.cursor() as cur:
            cur.execute(
                f"UPDATE {cls.TABLE} SET descripcion = %s WHERE codigo = %s",
                [descripcion, codigo],
            )
            updated = cur.rowcount > 0
        if updated:
            logger.info("[CatalogoOcupacion.actualizar] Registro codigo=%s actualizado.", codigo)
        else:
            logger.warning("[CatalogoOcupacion.actualizar] No se encontró codigo=%s.", codigo)
        return updated

    @classmethod
    def eliminar(cls, codigo: int) -> bool:
        logger.info("[CatalogoOcupacion.eliminar] Eliminando codigo=%s.", codigo)
        with connection.cursor() as cur:
            cur.execute(f"DELETE FROM {cls.TABLE} WHERE codigo = %s", [codigo])
            deleted = cur.rowcount > 0
        if deleted:
            logger.info("[CatalogoOcupacion.eliminar] Registro codigo=%s eliminado.", codigo)
        else:
            logger.warning("[CatalogoOcupacion.eliminar] No se encontró codigo=%s.", codigo)
        return deleted


class CatalogoInclinacionVoto:
    TABLE = db.catalogo_inclinacion_voto

    @classmethod
    def listar(cls) -> List[Dict]:
        logger.info("[CatalogoInclinacionVoto.listar] Consultando todos los registros.")
        with connection.cursor() as cur:
            cur.execute(f"SELECT codigo, descripcion FROM {cls.TABLE} ORDER BY codigo")
            result = _fetchall(cur)
        logger.info("[CatalogoInclinacionVoto.listar] %d registros encontrados.", len(result))
        return result

    @classmethod
    def obtener(cls, codigo: int) -> Optional[Dict]:
        logger.info("[CatalogoInclinacionVoto.obtener] Buscando codigo=%s.", codigo)
        with connection.cursor() as cur:
            cur.execute(
                f"SELECT codigo, descripcion FROM {cls.TABLE} WHERE codigo = %s",
                [codigo],
            )
            result = _fetchone(cur)
        if result:
            logger.info("[CatalogoInclinacionVoto.obtener] Registro encontrado.")
        else:
            logger.warning("[CatalogoInclinacionVoto.obtener] No se encontró codigo=%s.", codigo)
        return result

    @classmethod
    def crear(cls, codigo: int, descripcion: str) -> Dict:
        logger.info("[CatalogoInclinacionVoto.crear] Creando codigo=%s descripcion='%s'.", codigo, descripcion)
        with connection.cursor() as cur:
            cur.execute(
                f"INSERT INTO {cls.TABLE} (codigo, descripcion) VALUES (%s, %s)",
                [codigo, descripcion],
            )
        logger.info("[CatalogoInclinacionVoto.crear] Registro creado codigo=%s.", codigo)
        return {"codigo": codigo, "descripcion": descripcion}

    @classmethod
    def actualizar(cls, codigo: int, descripcion: str) -> bool:
        logger.info("[CatalogoInclinacionVoto.actualizar] Actualizando codigo=%s.", codigo)
        with connection.cursor() as cur:
            cur.execute(
                f"UPDATE {cls.TABLE} SET descripcion = %s WHERE codigo = %s",
                [descripcion, codigo],
            )
            updated = cur.rowcount > 0
        if updated:
            logger.info("[CatalogoInclinacionVoto.actualizar] Registro codigo=%s actualizado.", codigo)
        else:
            logger.warning("[CatalogoInclinacionVoto.actualizar] No se encontró codigo=%s.", codigo)
        return updated

    @classmethod
    def eliminar(cls, codigo: int) -> bool:
        logger.info("[CatalogoInclinacionVoto.eliminar] Eliminando codigo=%s.", codigo)
        with connection.cursor() as cur:
            cur.execute(f"DELETE FROM {cls.TABLE} WHERE codigo = %s", [codigo])
            deleted = cur.rowcount > 0
        if deleted:
            logger.info("[CatalogoInclinacionVoto.eliminar] Registro codigo=%s eliminado.", codigo)
        else:
            logger.warning("[CatalogoInclinacionVoto.eliminar] No se encontró codigo=%s.", codigo)
        return deleted


class CatalogoIntencionParticipacion:
    TABLE = db.catalogo_intencion_participacion

    @classmethod
    def listar(cls) -> List[Dict]:
        logger.info("[CatalogoIntencionParticipacion.listar] Consultando todos los registros.")
        with connection.cursor() as cur:
            cur.execute(f"SELECT codigo, descripcion FROM {cls.TABLE} ORDER BY codigo")
            result = _fetchall(cur)
        logger.info("[CatalogoIntencionParticipacion.listar] %d registros encontrados.", len(result))
        return result

    @classmethod
    def obtener(cls, codigo: int) -> Optional[Dict]:
        logger.info("[CatalogoIntencionParticipacion.obtener] Buscando codigo=%s.", codigo)
        with connection.cursor() as cur:
            cur.execute(
                f"SELECT codigo, descripcion FROM {cls.TABLE} WHERE codigo = %s",
                [codigo],
            )
            result = _fetchone(cur)
        if result:
            logger.info("[CatalogoIntencionParticipacion.obtener] Registro encontrado.")
        else:
            logger.warning("[CatalogoIntencionParticipacion.obtener] No se encontró codigo=%s.", codigo)
        return result

    @classmethod
    def crear(cls, codigo: int, descripcion: str) -> Dict:
        logger.info("[CatalogoIntencionParticipacion.crear] Creando codigo=%s descripcion='%s'.", codigo, descripcion)
        with connection.cursor() as cur:
            cur.execute(
                f"INSERT INTO {cls.TABLE} (codigo, descripcion) VALUES (%s, %s)",
                [codigo, descripcion],
            )
        logger.info("[CatalogoIntencionParticipacion.crear] Registro creado codigo=%s.", codigo)
        return {"codigo": codigo, "descripcion": descripcion}

    @classmethod
    def actualizar(cls, codigo: int, descripcion: str) -> bool:
        logger.info("[CatalogoIntencionParticipacion.actualizar] Actualizando codigo=%s.", codigo)
        with connection.cursor() as cur:
            cur.execute(
                f"UPDATE {cls.TABLE} SET descripcion = %s WHERE codigo = %s",
                [descripcion, codigo],
            )
            updated = cur.rowcount > 0
        if updated:
            logger.info("[CatalogoIntencionParticipacion.actualizar] Registro codigo=%s actualizado.", codigo)
        else:
            logger.warning("[CatalogoIntencionParticipacion.actualizar] No se encontró codigo=%s.", codigo)
        return updated

    @classmethod
    def eliminar(cls, codigo: int) -> bool:
        logger.info("[CatalogoIntencionParticipacion.eliminar] Eliminando codigo=%s.", codigo)
        with connection.cursor() as cur:
            cur.execute(f"DELETE FROM {cls.TABLE} WHERE codigo = %s", [codigo])
            deleted = cur.rowcount > 0
        if deleted:
            logger.info("[CatalogoIntencionParticipacion.eliminar] Registro codigo=%s eliminado.", codigo)
        else:
            logger.warning("[CatalogoIntencionParticipacion.eliminar] No se encontró codigo=%s.", codigo)
        return deleted


class CatalogoProblematica:
    TABLE = db.catalogo_problematica

    @classmethod
    def listar(cls) -> List[Dict]:
        logger.info("[CatalogoProblematica.listar] Consultando todos los registros.")
        with connection.cursor() as cur:
            cur.execute(f"SELECT codigo, descripcion FROM {cls.TABLE} ORDER BY codigo")
            result = _fetchall(cur)
        logger.info("[CatalogoProblematica.listar] %d registros encontrados.", len(result))
        return result

    @classmethod
    def obtener(cls, codigo: int) -> Optional[Dict]:
        logger.info("[CatalogoProblematica.obtener] Buscando codigo=%s.", codigo)
        with connection.cursor() as cur:
            cur.execute(
                f"SELECT codigo, descripcion FROM {cls.TABLE} WHERE codigo = %s",
                [codigo],
            )
            result = _fetchone(cur)
        if result:
            logger.info("[CatalogoProblematica.obtener] Registro encontrado.")
        else:
            logger.warning("[CatalogoProblematica.obtener] No se encontró codigo=%s.", codigo)
        return result

    @classmethod
    def crear(cls, codigo: int, descripcion: str) -> Dict:
        logger.info("[CatalogoProblematica.crear] Creando codigo=%s descripcion='%s'.", codigo, descripcion)
        with connection.cursor() as cur:
            cur.execute(
                f"INSERT INTO {cls.TABLE} (codigo, descripcion) VALUES (%s, %s)",
                [codigo, descripcion],
            )
        logger.info("[CatalogoProblematica.crear] Registro creado codigo=%s.", codigo)
        return {"codigo": codigo, "descripcion": descripcion}

    @classmethod
    def actualizar(cls, codigo: int, descripcion: str) -> bool:
        logger.info("[CatalogoProblematica.actualizar] Actualizando codigo=%s.", codigo)
        with connection.cursor() as cur:
            cur.execute(
                f"UPDATE {cls.TABLE} SET descripcion = %s WHERE codigo = %s",
                [descripcion, codigo],
            )
            updated = cur.rowcount > 0
        if updated:
            logger.info("[CatalogoProblematica.actualizar] Registro codigo=%s actualizado.", codigo)
        else:
            logger.warning("[CatalogoProblematica.actualizar] No se encontró codigo=%s.", codigo)
        return updated

    @classmethod
    def eliminar(cls, codigo: int) -> bool:
        logger.info("[CatalogoProblematica.eliminar] Eliminando codigo=%s.", codigo)
        with connection.cursor() as cur:
            cur.execute(f"DELETE FROM {cls.TABLE} WHERE codigo = %s", [codigo])
            deleted = cur.rowcount > 0
        if deleted:
            logger.info("[CatalogoProblematica.eliminar] Registro codigo=%s eliminado.", codigo)
        else:
            logger.warning("[CatalogoProblematica.eliminar] No se encontró codigo=%s.", codigo)
        return deleted


# =============================================================================
# RANGO DE EDAD
# =============================================================================

class RangoEdad:
    TABLE = db.rango_edad

    @classmethod
    def listar(cls) -> List[Dict]:
        logger.info("[RangoEdad.listar] Consultando todos los rangos de edad.")
        with connection.cursor() as cur:
            cur.execute(
                f"SELECT id, etiqueta, edad_min, edad_max FROM {cls.TABLE} ORDER BY edad_min"
            )
            result = [_str_fields(r) for r in _fetchall(cur)]
        logger.info("[RangoEdad.listar] %d rangos encontrados.", len(result))
        return result

    @classmethod
    def obtener(cls, rango_id: str) -> Optional[Dict]:
        logger.info("[RangoEdad.obtener] Buscando id=%s.", rango_id)
        with connection.cursor() as cur:
            cur.execute(
                f"SELECT id, etiqueta, edad_min, edad_max FROM {cls.TABLE} WHERE id = %s",
                [rango_id],
            )
            row = _fetchone(cur)
        result = _str_fields(row) if row else None
        if result:
            logger.info("[RangoEdad.obtener] Registro encontrado.")
        else:
            logger.warning("[RangoEdad.obtener] No se encontró id=%s.", rango_id)
        return result

    @classmethod
    def crear(cls, etiqueta: str, edad_min: int, edad_max: int) -> Dict:
        new_id = str(uuid.uuid4())
        logger.info("[RangoEdad.crear] Creando rango etiqueta='%s' (%d-%d).", etiqueta, edad_min, edad_max)
        with connection.cursor() as cur:
            cur.execute(
                f"""
                INSERT INTO {cls.TABLE} (id, etiqueta, edad_min, edad_max)
                VALUES (%s, %s, %s, %s)
                """,
                [new_id, etiqueta, edad_min, edad_max],
            )
        logger.info("[RangoEdad.crear] Rango creado con id=%s.", new_id)
        return {"id": new_id, "etiqueta": etiqueta, "edad_min": edad_min, "edad_max": edad_max}

    @classmethod
    def actualizar(cls, rango_id: str, etiqueta: str, edad_min: int, edad_max: int) -> bool:
        logger.info("[RangoEdad.actualizar] Actualizando id=%s.", rango_id)
        with connection.cursor() as cur:
            cur.execute(
                f"""
                UPDATE {cls.TABLE}
                SET etiqueta = %s, edad_min = %s, edad_max = %s
                WHERE id = %s
                """,
                [etiqueta, edad_min, edad_max, rango_id],
            )
            updated = cur.rowcount > 0
        if updated:
            logger.info("[RangoEdad.actualizar] Rango id=%s actualizado.", rango_id)
        else:
            logger.warning("[RangoEdad.actualizar] No se encontró id=%s para actualizar.", rango_id)
        return updated

    @classmethod
    def eliminar(cls, rango_id: str) -> bool:
        logger.info("[RangoEdad.eliminar] Eliminando id=%s.", rango_id)
        with connection.cursor() as cur:
            cur.execute(f"DELETE FROM {cls.TABLE} WHERE id = %s", [rango_id])
            deleted = cur.rowcount > 0
        if deleted:
            logger.info("[RangoEdad.eliminar] Rango id=%s eliminado.", rango_id)
        else:
            logger.warning("[RangoEdad.eliminar] No se encontró id=%s para eliminar.", rango_id)
        return deleted


# =============================================================================
# PERÍODO ESTADÍSTICO
# =============================================================================

class PeriodoEstadistico:
    TABLE = db.periodo_estadistico

    @classmethod
    def listar(cls) -> List[Dict]:
        logger.info("[PeriodoEstadistico.listar] Consultando todos los períodos.")
        with connection.cursor() as cur:
            cur.execute(
                f"""
                SELECT id, etiqueta, fecha_inicio, fecha_fin
                FROM {cls.TABLE}
                ORDER BY fecha_inicio DESC
                """
            )
            result = [_str_fields(r) for r in _fetchall(cur)]
        logger.info("[PeriodoEstadistico.listar] %d períodos encontrados.", len(result))
        return result

    @classmethod
    def obtener(cls, periodo_id: str) -> Optional[Dict]:
        logger.info("[PeriodoEstadistico.obtener] Buscando id=%s.", periodo_id)
        with connection.cursor() as cur:
            cur.execute(
                f"""
                SELECT id, etiqueta, fecha_inicio, fecha_fin
                FROM {cls.TABLE}
                WHERE id = %s
                """,
                [periodo_id],
            )
            row = _fetchone(cur)
        result = _str_fields(row) if row else None
        if result:
            logger.info("[PeriodoEstadistico.obtener] Período encontrado.")
        else:
            logger.warning("[PeriodoEstadistico.obtener] No se encontró id=%s.", periodo_id)
        return result

    @classmethod
    def crear(cls, etiqueta: str, fecha_inicio, fecha_fin) -> Dict:
        new_id = str(uuid.uuid4())
        logger.info("[PeriodoEstadistico.crear] Creando período '%s' (%s → %s).", etiqueta, fecha_inicio, fecha_fin)
        with connection.cursor() as cur:
            cur.execute(
                f"""
                INSERT INTO {cls.TABLE} (id, etiqueta, fecha_inicio, fecha_fin)
                VALUES (%s, %s, %s, %s)
                """,
                [new_id, etiqueta, fecha_inicio, fecha_fin],
            )
        logger.info("[PeriodoEstadistico.crear] Período creado con id=%s.", new_id)
        return {"id": new_id, "etiqueta": etiqueta, "fecha_inicio": str(fecha_inicio), "fecha_fin": str(fecha_fin)}

    @classmethod
    def actualizar(cls, periodo_id: str, etiqueta: str, fecha_inicio, fecha_fin) -> bool:
        logger.info("[PeriodoEstadistico.actualizar] Actualizando id=%s.", periodo_id)
        with connection.cursor() as cur:
            cur.execute(
                f"""
                UPDATE {cls.TABLE}
                SET etiqueta = %s, fecha_inicio = %s, fecha_fin = %s
                WHERE id = %s
                """,
                [etiqueta, fecha_inicio, fecha_fin, periodo_id],
            )
            updated = cur.rowcount > 0
        if updated:
            logger.info("[PeriodoEstadistico.actualizar] Período id=%s actualizado.", periodo_id)
        else:
            logger.warning("[PeriodoEstadistico.actualizar] No se encontró id=%s.", periodo_id)
        return updated

    @classmethod
    def eliminar(cls, periodo_id: str) -> bool:
        """
        Elimina el período y todos los datos asociados a él en cascada:
        snapshots, rankings, caracterizaciones, resúmenes, variaciones,
        cruces, exportaciones e importaciones del período.
        Las encuestas se eliminan por rango de fecha del período.
        """
        logger.info("[PeriodoEstadistico.eliminar] Eliminando id=%s con cascada.", periodo_id)

        periodo = cls.obtener(periodo_id)
        if not periodo:
            logger.warning("[PeriodoEstadistico.eliminar] No se encontró id=%s.", periodo_id)
            return False

        fecha_inicio = periodo["fecha_inicio"]
        fecha_fin    = periodo["fecha_fin"]

        with transaction.atomic():
            with connection.cursor() as cur:
                # 1. Resúmenes estadísticos
                cur.execute(f"DELETE FROM {db.resumen_estadistico} WHERE periodo_id = %s", [periodo_id])
                logger.info("[PeriodoEstadistico.eliminar] Resúmenes eliminados.")

                # 2. Caracterizaciones territoriales
                cur.execute(f"DELETE FROM {db.caracterizacion_territorial} WHERE periodo_id = %s", [periodo_id])
                logger.info("[PeriodoEstadistico.eliminar] Caracterizaciones eliminadas.")

                # 3. Rankings de problemáticas
                cur.execute(f"DELETE FROM {db.ranking_problematica} WHERE periodo_id = %s", [periodo_id])
                logger.info("[PeriodoEstadistico.eliminar] Rankings eliminados.")

                # 4. Resultados de cruces
                cur.execute(
                    f"DELETE FROM {db.resultado_cruce} WHERE periodo_id = %s",
                    [periodo_id],
                )
                logger.info("[PeriodoEstadistico.eliminar] Cruces eliminados.")

                # 5. Variaciones temporales (como período anterior o actual)
                cur.execute(
                    f"DELETE FROM {db.variacion_temporal} WHERE periodo_anterior_id = %s OR periodo_actual_id = %s",
                    [periodo_id, periodo_id],
                )
                logger.info("[PeriodoEstadistico.eliminar] Variaciones eliminadas.")

                # 6. Exportaciones del período
                cur.execute(f"DELETE FROM {db.exportacion_resultado} WHERE periodo_id = %s", [periodo_id])
                logger.info("[PeriodoEstadistico.eliminar] Exportaciones eliminadas.")

                # 7. Snapshots territoriales
                cur.execute(f"DELETE FROM {db.snapshot_territorial} WHERE periodo_id = %s", [periodo_id])
                logger.info("[PeriodoEstadistico.eliminar] Snapshots eliminados.")

                # 8. Encuestas del rango de fechas del período
                cur.execute(
                    f"DELETE FROM {db.encuesta} WHERE fecha >= %s AND fecha <= %s",
                    [fecha_inicio, fecha_fin],
                )
                logger.info("[PeriodoEstadistico.eliminar] Encuestas eliminadas.")

                # 9. Importaciones asociadas al período
                cur.execute(f"DELETE FROM {db.importacion_csv} WHERE periodo_id = %s", [periodo_id])
                logger.info("[PeriodoEstadistico.eliminar] Importaciones eliminadas.")

                # 10. El período en sí
                cur.execute(f"DELETE FROM {cls.TABLE} WHERE id = %s", [periodo_id])
                deleted = cur.rowcount > 0

        if deleted:
            logger.info("[PeriodoEstadistico.eliminar] Período id=%s eliminado con todos sus datos.", periodo_id)
        else:
            logger.warning("[PeriodoEstadistico.eliminar] No se pudo eliminar el período id=%s.", periodo_id)
        return deleted


# =============================================================================
# IMPORTACIÓN CSV
# =============================================================================

class ImportacionCsv:
    TABLE = db.importacion_csv

    _COLS = (
        "id, nombre_archivo, fecha_importacion, procesado_en, "
        "estado, total_registros, registros_validos, "
        "registros_invalidos, errores_detalle, periodo_id"
    )

    @classmethod
    def listar(cls) -> List[Dict]:
        logger.info("[ImportacionCsv.listar] Consultando importaciones.")
        with connection.cursor() as cur:
            cur.execute(
                f"SELECT {cls._COLS} FROM {cls.TABLE} ORDER BY fecha_importacion DESC"
            )
            result = [_str_fields(r) for r in _fetchall(cur)]
        logger.info("[ImportacionCsv.listar] %d importaciones encontradas.", len(result))
        return result

    @classmethod
    def obtener(cls, importacion_id: str) -> Optional[Dict]:
        logger.info("[ImportacionCsv.obtener] Buscando id=%s.", importacion_id)
        with connection.cursor() as cur:
            cur.execute(
                f"SELECT {cls._COLS} FROM {cls.TABLE} WHERE id = %s",
                [importacion_id],
            )
            row = _fetchone(cur)
        result = _str_fields(row) if row else None
        if result:
            logger.info("[ImportacionCsv.obtener] Importación encontrada.")
        else:
            logger.warning("[ImportacionCsv.obtener] No se encontró id=%s.", importacion_id)
        return result

    @classmethod
    def crear(cls, nombre_archivo: str, periodo_id: Optional[str] = None) -> Dict:
        new_id = str(uuid.uuid4())
        fecha_hoy = datetime.date.today()
        logger.info("[ImportacionCsv.crear] Creando importación '%s'.", nombre_archivo)
        with connection.cursor() as cur:
            cur.execute(
                f"""
                INSERT INTO {cls.TABLE}
                    (id, nombre_archivo, fecha_importacion, estado,
                     total_registros, registros_validos, registros_invalidos, periodo_id)
                VALUES (%s, %s, %s, 'PENDIENTE', 0, 0, 0, %s)
                """,
                [new_id, nombre_archivo, fecha_hoy, periodo_id],
            )
        logger.info("[ImportacionCsv.crear] Importación creada con id=%s.", new_id)
        return {"id": new_id, "nombre_archivo": nombre_archivo, "estado": "PENDIENTE", "periodo_id": periodo_id}

    @classmethod
    def finalizar(
        cls,
        importacion_id: str,
        total: int,
        validos: int,
        invalidos: int,
        errores: Optional[str],
    ) -> bool:
        """Marca la importación como COMPLETADO con los totales calculados."""
        logger.info(
            "[ImportacionCsv.finalizar] Finalizando id=%s — total=%d, validos=%d, invalidos=%d.",
            importacion_id, total, validos, invalidos,
        )
        ahora = datetime.datetime.now()
        with connection.cursor() as cur:
            cur.execute(
                f"""
                UPDATE {cls.TABLE}
                SET estado              = 'COMPLETADO',
                    procesado_en        = %s,
                    total_registros     = %s,
                    registros_validos   = %s,
                    registros_invalidos = %s,
                    errores_detalle     = %s
                WHERE id = %s
                """,
                [ahora, total, validos, invalidos, errores, importacion_id],
            )
            updated = cur.rowcount > 0
        if updated:
            logger.info("[ImportacionCsv.finalizar] Importación id=%s marcada como COMPLETADO.", importacion_id)
        else:
            logger.warning("[ImportacionCsv.finalizar] No se encontró id=%s.", importacion_id)
        return updated


# =============================================================================
# ENCUESTA
# =============================================================================

class Encuesta:
    TABLE = db.encuesta

    # Columnas base para SELECT
    _COLS = """
        e.id, e.importacion_id, e.fecha, e.edad, e.barrio, e.barrio_id,
        e.ocupacion_cod, e.inclinacion_voto_cod, e.intencion_participacion_cod,
        e.prob_1_cod, e.prob_2_cod, e.prob_otra, e.opinion_politica,
        oc.descripcion  AS ocupacion_desc,
        iv.descripcion  AS inclinacion_voto_desc,
        ip.descripcion  AS intencion_participacion_desc,
        p1.descripcion  AS problematica_1_desc,
        p2.descripcion  AS problematica_2_desc
    """

    # JOINs hacia catálogos
    _JOINS = f"""
        LEFT JOIN {db.catalogo_ocupacion}               oc ON oc.codigo = e.ocupacion_cod
        LEFT JOIN {db.catalogo_inclinacion_voto}        iv ON iv.codigo = e.inclinacion_voto_cod
        LEFT JOIN {db.catalogo_intencion_participacion} ip ON ip.codigo = e.intencion_participacion_cod
        LEFT JOIN {db.catalogo_problematica}            p1 ON p1.codigo = e.prob_1_cod
        LEFT JOIN {db.catalogo_problematica}            p2 ON p2.codigo = e.prob_2_cod
    """

    @classmethod
    def _base_select(cls) -> str:
        return f"SELECT {cls._COLS} FROM {cls.TABLE} e {cls._JOINS}"

    # ------------------------------------------------------------------
    # Listar
    # ------------------------------------------------------------------
    @classmethod
    def listar(cls, importacion_id=None, barrio_id=None) -> List[Dict]:
        logger.info(
            "[Encuesta.listar] importacion_id=%s barrio_id=%s.",
            importacion_id, barrio_id,
        )
        sql    = cls._base_select()
        params = []
        wheres = []
        if importacion_id:
            wheres.append("e.importacion_id = %s")
            params.append(importacion_id)
        if barrio_id:
            wheres.append("e.barrio_id = %s")
            params.append(barrio_id)
        if wheres:
            sql += " WHERE " + " AND ".join(wheres)
        sql += " ORDER BY e.fecha DESC"

        with connection.cursor() as cur:
            cur.execute(sql, params)
            result = [_str_fields(r) for r in _fetchall(cur)]
        logger.info("[Encuesta.listar] %d encuestas encontradas.", len(result))
        return result

    @classmethod
    def listar_por_periodo(cls, periodo_id: str) -> List[Dict]:
        logger.info("[Encuesta.listar_por_periodo] periodo_id=%s.", periodo_id)
        periodo = PeriodoEstadistico.obtener(periodo_id)
        if not periodo:
            logger.warning("[Encuesta.listar_por_periodo] Período %s no encontrado.", periodo_id)
            return []
        
        # CORRECCIÓN: Filtramos directamente por el UUID del periodo_id 
        # para garantizar un aislamiento absoluto entre periodos.
        sql = (
            cls._base_select()
            + " WHERE e.periodo_id = %s ORDER BY e.fecha DESC"
        )
        
        with connection.cursor() as cur:
            # Pasamos el periodo_id como argumento seguro
            cur.execute(sql, [periodo_id])
            result = [_str_fields(r) for r in _fetchall(cur)]
            
        logger.info("[Encuesta.listar_por_periodo] %d encuestas encontradas.", len(result))
        return result

    # ------------------------------------------------------------------
    # Obtener
    # ------------------------------------------------------------------
    @classmethod
    def obtener(cls, encuesta_id: str) -> Optional[Dict]:
        logger.info("[Encuesta.obtener] Buscando id=%s.", encuesta_id)
        with connection.cursor() as cur:
            cur.execute(cls._base_select() + " WHERE e.id = %s", [encuesta_id])
            row = _fetchone(cur)
        result = _str_fields(row) if row else None
        if result:
            logger.info("[Encuesta.obtener] Encuesta encontrada.")
        else:
            logger.warning("[Encuesta.obtener] No se encontró id=%s.", encuesta_id)
        return result

    # ------------------------------------------------------------------
    # Crear
    # ------------------------------------------------------------------
    @classmethod
    def crear(cls, payload: Dict) -> Dict:
        new_id = str(uuid.uuid4())
        logger.info("[Encuesta.crear] Creando encuesta con payload keys=%s.", list(payload.keys()))
        campos = {
            "importacion_id", "fecha", "edad", "barrio", "barrio_id",
            "ocupacion_cod", "inclinacion_voto_cod",
            "intencion_participacion_cod", "prob_1_cod",
            "prob_2_cod", "prob_otra", "opinion_politica",
        }
        datos = {k: v for k, v in payload.items() if k in campos}
        datos["id"] = new_id

        cols   = ", ".join(datos.keys())
        places = ", ".join(["%s"] * len(datos))
        with connection.cursor() as cur:
            cur.execute(
                f"INSERT INTO {cls.TABLE} ({cols}) VALUES ({places})",
                list(datos.values()),
            )
        logger.info("[Encuesta.crear] Encuesta creada con id=%s.", new_id)
        return {"id": new_id, **datos}

    # ------------------------------------------------------------------
    # Actualizar
    # ------------------------------------------------------------------
    @classmethod
    def actualizar(cls, encuesta_id: str, payload: Dict) -> bool:
        logger.info("[Encuesta.actualizar] Actualizando id=%s.", encuesta_id)
        campos_permitidos = {
            "fecha", "edad", "barrio", "barrio_id",
            "ocupacion_cod", "inclinacion_voto_cod",
            "intencion_participacion_cod", "prob_1_cod",
            "prob_2_cod", "prob_otra", "opinion_politica",
        }
        datos = {k: v for k, v in payload.items() if k in campos_permitidos}
        if not datos:
            logger.warning("[Encuesta.actualizar] No hay campos válidos para actualizar id=%s.", encuesta_id)
            return False

        set_clause = ", ".join(f"{k} = %s" for k in datos)
        with connection.cursor() as cur:
            cur.execute(
                f"UPDATE {cls.TABLE} SET {set_clause} WHERE id = %s",
                [*datos.values(), encuesta_id],
            )
            updated = cur.rowcount > 0
        if updated:
            logger.info("[Encuesta.actualizar] Encuesta id=%s actualizada.", encuesta_id)
        else:
            logger.warning("[Encuesta.actualizar] No se encontró id=%s.", encuesta_id)
        return updated

    # ------------------------------------------------------------------
    # Eliminar
    # ------------------------------------------------------------------
    @classmethod
    def eliminar(cls, encuesta_id: str) -> bool:
        logger.info("[Encuesta.eliminar] Eliminando id=%s.", encuesta_id)
        with connection.cursor() as cur:
            cur.execute(f"DELETE FROM {cls.TABLE} WHERE id = %s", [encuesta_id])
            deleted = cur.rowcount > 0
        if deleted:
            logger.info("[Encuesta.eliminar] Encuesta id=%s eliminada.", encuesta_id)
        else:
            logger.warning("[Encuesta.eliminar] No se encontró id=%s.", encuesta_id)
        return deleted

    # ------------------------------------------------------------------
    # Inserción masiva
    # ------------------------------------------------------------------
    @classmethod
    def insercion_masiva(cls, rows: List[Dict]) -> int:
        """Inserta en bloque filas ya validadas provenientes del CSV."""
        logger.info("[Encuesta.insercion_masiva] Insertando %d filas.", len(rows))
        if not rows:
            return 0

        campos = [
            "id", "importacion_id", "fecha", "edad", "barrio", "barrio_id",
            "ocupacion_cod", "inclinacion_voto_cod",
            "intencion_participacion_cod", "prob_1_cod",
            "prob_2_cod", "prob_otra", "opinion_politica",
        ]
        cols   = ", ".join(campos)
        places = ", ".join(["%s"] * len(campos))
        valores = []
        for r in rows:
            r.setdefault("id", str(uuid.uuid4()))
            valores.append([r.get(c) for c in campos])

        with connection.cursor() as cur:
            cur.executemany(
                f"INSERT INTO {cls.TABLE} ({cols}) VALUES ({places})",
                valores,
            )
        logger.info("[Encuesta.insercion_masiva] %d filas insertadas.", len(rows))
        return len(rows)

    # ------------------------------------------------------------------
    # Barrios del período
    # ------------------------------------------------------------------
    @classmethod
    def barrios_del_periodo(cls, periodo_id: str) -> List[str]:
        logger.info("[Encuesta.barrios_del_periodo] periodo_id=%s.", periodo_id)
        periodo = PeriodoEstadistico.obtener(periodo_id)
        if not periodo:
            logger.warning("[Encuesta.barrios_del_periodo] Período %s no encontrado.", periodo_id)
            return []
        with connection.cursor() as cur:
            cur.execute(
                f"""
                SELECT DISTINCT barrio_id
                FROM {cls.TABLE}
                WHERE barrio_id IS NOT NULL
                  AND fecha >= %s AND fecha <= %s
                """,
                [periodo["fecha_inicio"], periodo["fecha_fin"]],
            )
            result = [str(row[0]) for row in cur.fetchall()]
        logger.info("[Encuesta.barrios_del_periodo] %d barrios encontrados.", len(result))
        return result

    # ------------------------------------------------------------------
    # Agregar por barrio y período
    # ------------------------------------------------------------------
    @classmethod
    def agregar_por_barrio_y_periodo(cls, barrio_id: str, periodo_id: str) -> Dict:
        logger.info(
            "[Encuesta.agregar_por_barrio_y_periodo] barrio_id=%s periodo_id=%s.",
            barrio_id, periodo_id,
        )
        periodo = PeriodoEstadistico.obtener(periodo_id)
        if not periodo:
            logger.warning("[Encuesta.agregar_por_barrio_y_periodo] Período %s no encontrado.", periodo_id)
            return {k: 0 for k in (
                "total", "total_simpatizantes", "total_indecisos",
                "total_no_simpatizantes", "total_no_votantes",
                "total_intension_votar", "total_abstencion",
            )}
        with connection.cursor() as cur:
            cur.execute(
                f"""
                SELECT
                    COUNT(*) AS total,
                    COUNT(*) FILTER (WHERE inclinacion_voto_cod = 1) AS total_simpatizantes,
                    COUNT(*) FILTER (WHERE inclinacion_voto_cod = 3) AS total_indecisos,
                    COUNT(*) FILTER (WHERE inclinacion_voto_cod = 2) AS total_no_simpatizantes,
                    COUNT(*) FILTER (WHERE inclinacion_voto_cod = 4) AS total_no_votantes,
                    COUNT(*) FILTER (WHERE intencion_participacion_cod IN (1,2)) AS total_intension_votar,
                    COUNT(*) FILTER (WHERE intencion_participacion_cod IN (4,5)) AS total_abstencion
                FROM {cls.TABLE}
                WHERE barrio_id = %s
                AND fecha >= %s
                AND fecha <= %s
                """,
                [barrio_id, periodo["fecha_inicio"], periodo["fecha_fin"]],
            )

            result = _fetchone(cur)

        logger.info("[Encuesta.agregar_por_barrio_y_periodo] Resultado: %s.", result)
        return result or {k: 0 for k in (
            "total", "total_simpatizantes", "total_indecisos",
            "total_no_simpatizantes", "total_no_votantes",
            "total_intension_votar", "total_abstencion",
        )}

    # ------------------------------------------------------------------
    # Moda de un campo
    # ------------------------------------------------------------------
    @classmethod
    def moda(cls, campo: str, barrio_id: str, periodo_id: str) -> Optional[str]:
        CAMPOS_PERMITIDOS = {
            "ocupacion_cod", "inclinacion_voto_cod",
            "intencion_participacion_cod", "prob_1_cod", "prob_2_cod",
        }
        if campo not in CAMPOS_PERMITIDOS:
            logger.warning("[Encuesta.moda] Campo '%s' no permitido.", campo)
            return None

        logger.info(
            "[Encuesta.moda] campo=%s barrio_id=%s periodo_id=%s.",
            campo, barrio_id, periodo_id,
        )
        periodo = PeriodoEstadistico.obtener(periodo_id)
        if not periodo:
            logger.warning("[Encuesta.moda] Período %s no encontrado.", periodo_id)
            return None

        with connection.cursor() as cur:
            cur.execute(
                f"""
                SELECT {campo}, COUNT(*) AS frecuencia
                FROM {cls.TABLE}
                WHERE barrio_id = %s
                  AND fecha >= %s AND fecha <= %s
                  AND {campo} IS NOT NULL
                GROUP BY {campo}
                ORDER BY frecuencia DESC
                LIMIT 1
                """,
                [barrio_id, periodo["fecha_inicio"], periodo["fecha_fin"]],
            )
            row = cur.fetchone()
        result = str(row[0]) if row else None
        logger.info("[Encuesta.moda] Moda de '%s' = %s.", campo, result)
        return result


# =============================================================================
# SNAPSHOT TERRITORIAL
# =============================================================================

class SnapshotTerritorial:
    TABLE = db.snapshot_territorial

    _COLS = """
        s.id, s.barrio_id, s.periodo_id,
        s.total_simpatizantes, s.total_indecisos, s.total_no_simpatizantes,
        s.total_no_votantes, s.pct_simpatizantes, s.pct_indecisos,
        s.pct_no_simpatizantes, s.pct_no_votantes,
        s.total_intension_votar, s.total_abstencion, s.pct_participacion,
        s.indice_intervencion, s.generado_en,
        p.etiqueta AS periodo_etiqueta
    """

    @classmethod
    def _base_select(cls) -> str:
        return (
            f"SELECT {cls._COLS} "
            f"FROM {cls.TABLE} s "
            f"LEFT JOIN {db.periodo_estadistico} p ON p.id = s.periodo_id"
        )

    @classmethod
    def listar(cls, barrio_id=None, periodo_id=None) -> List[Dict]:
        logger.info("[SnapshotTerritorial.listar] barrio_id=%s periodo_id=%s.", barrio_id, periodo_id)
        sql    = cls._base_select()
        params = []
        wheres = []
        if barrio_id:
            wheres.append("s.barrio_id = %s")
            params.append(barrio_id)
        if periodo_id:
            wheres.append("s.periodo_id = %s")
            params.append(periodo_id)
        if wheres:
            sql += " WHERE " + " AND ".join(wheres)
        sql += " ORDER BY s.generado_en DESC"

        with connection.cursor() as cur:
            cur.execute(sql, params)
            result = [_str_fields(r) for r in _fetchall(cur)]
        logger.info("[SnapshotTerritorial.listar] %d snapshots encontrados.", len(result))
        return result

    @classmethod
    def obtener(cls, snapshot_id: str) -> Optional[Dict]:
        logger.info("[SnapshotTerritorial.obtener] Buscando id=%s.", snapshot_id)
        with connection.cursor() as cur:
            cur.execute(cls._base_select() + " WHERE s.id = %s", [snapshot_id])
            row = _fetchone(cur)
        result = _str_fields(row) if row else None
        if result:
            logger.info("[SnapshotTerritorial.obtener] Snapshot encontrado.")
        else:
            logger.warning("[SnapshotTerritorial.obtener] No se encontró id=%s.", snapshot_id)
        return result

    @classmethod
    def obtener_porcentajes(cls, barrio_id: str, periodo_id: str) -> Optional[Dict]:
        logger.info(
            "[SnapshotTerritorial.obtener_porcentajes] barrio_id=%s periodo_id=%s.",
            barrio_id, periodo_id,
        )
        with connection.cursor() as cur:
            cur.execute(
                f"""
                SELECT pct_simpatizantes, pct_indecisos, pct_no_simpatizantes,
                       pct_participacion, indice_intervencion
                FROM {cls.TABLE}
                WHERE barrio_id = %s AND periodo_id = %s
                """,
                [barrio_id, periodo_id],
            )
            row = _fetchone(cur)
        result = _str_fields(row) if row else None
        if result:
            logger.info("[SnapshotTerritorial.obtener_porcentajes] Porcentajes encontrados.")
        else:
            logger.warning(
                "[SnapshotTerritorial.obtener_porcentajes] Sin datos para barrio=%s periodo=%s.",
                barrio_id, periodo_id,
            )
        return result

    @classmethod
    def crear_o_reemplazar(cls, barrio_id: str, periodo_id: str, totales: Dict) -> Dict:
        logger.info(
            "[SnapshotTerritorial.crear_o_reemplazar] barrio_id=%s periodo_id=%s.",
            barrio_id, periodo_id,
        )
        total = totales.get("total") or 0
        ts    = totales.get("total_simpatizantes") or 0
        ti    = totales.get("total_indecisos") or 0
        tns   = totales.get("total_no_simpatizantes") or 0
        tnv   = totales.get("total_no_votantes") or 0
        tiv   = totales.get("total_intension_votar") or 0
        tab   = totales.get("total_abstencion") or 0

        def pct(part, whole):
            return round(part / whole * 100, 2) if whole else None

        indice = round((ts - tns) / total * 100, 4) if total else None
        new_id = str(uuid.uuid4())

        with transaction.atomic():
            with connection.cursor() as cur:
                cur.execute(
                    f"DELETE FROM {cls.TABLE} WHERE barrio_id = %s AND periodo_id = %s",
                    [barrio_id, periodo_id],
                )
                logger.info("[SnapshotTerritorial.crear_o_reemplazar] Snapshot anterior eliminado.")
                cur.execute(
                    f"""
                    INSERT INTO {cls.TABLE} (
                        id, barrio_id, periodo_id,
                        total_simpatizantes, total_indecisos, total_no_simpatizantes, total_no_votantes,
                        pct_simpatizantes, pct_indecisos, pct_no_simpatizantes, pct_no_votantes,
                        total_intension_votar, total_abstencion, pct_participacion, indice_intervencion
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    [
                        new_id, barrio_id, periodo_id,
                        ts, ti, tns, tnv,
                        pct(ts, total), pct(ti, total), pct(tns, total), pct(tnv, total),
                        tiv, tab, pct(tiv, total), indice,
                    ],
                )
        logger.info("[SnapshotTerritorial.crear_o_reemplazar] Nuevo snapshot id=%s creado.", new_id)
        return {"id": new_id, "barrio_id": barrio_id, "periodo_id": periodo_id}

    @classmethod
    def eliminar(cls, snapshot_id: str) -> bool:
        logger.info("[SnapshotTerritorial.eliminar] Eliminando id=%s.", snapshot_id)
        with connection.cursor() as cur:
            cur.execute(f"DELETE FROM {cls.TABLE} WHERE id = %s", [snapshot_id])
            deleted = cur.rowcount > 0
        if deleted:
            logger.info("[SnapshotTerritorial.eliminar] Snapshot id=%s eliminado.", snapshot_id)
        else:
            logger.warning("[SnapshotTerritorial.eliminar] No se encontró id=%s.", snapshot_id)
        return deleted


# =============================================================================
# VARIACIÓN TEMPORAL
# =============================================================================

class VariacionTemporal:
    TABLE = db.variacion_temporal

    _COLS = """
        v.id, v.barrio_id, v.periodo_anterior_id, v.periodo_actual_id,
        v.variacion_simpatizantes, v.variacion_indecisos,
        v.variacion_no_simpatizantes, v.variacion_participacion,
        v.cambio_significativo,
        pa.etiqueta AS periodo_anterior_etiqueta,
        pac.etiqueta AS periodo_actual_etiqueta
    """

    @classmethod
    def _base_select(cls) -> str:
        return (
            f"SELECT {cls._COLS} "
            f"FROM {cls.TABLE} v "
            f"LEFT JOIN {db.periodo_estadistico} pa  ON pa.id  = v.periodo_anterior_id "
            f"LEFT JOIN {db.periodo_estadistico} pac ON pac.id = v.periodo_actual_id"
        )

    @classmethod
    def listar(cls, barrio_id=None, periodo_actual_id=None) -> List[Dict]:
        logger.info(
            "[VariacionTemporal.listar] barrio_id=%s periodo_actual_id=%s.",
            barrio_id, periodo_actual_id,
        )
        sql    = cls._base_select()
        params = []
        wheres = []
        if barrio_id:
            wheres.append("v.barrio_id = %s")
            params.append(barrio_id)
        if periodo_actual_id:
            wheres.append("v.periodo_actual_id = %s")
            params.append(periodo_actual_id)
        if wheres:
            sql += " WHERE " + " AND ".join(wheres)

        with connection.cursor() as cur:
            cur.execute(sql, params)
            result = [_str_fields(r) for r in _fetchall(cur)]
        logger.info("[VariacionTemporal.listar] %d variaciones encontradas.", len(result))
        return result

    @classmethod
    def obtener(cls, variacion_id: str) -> Optional[Dict]:
        logger.info("[VariacionTemporal.obtener] Buscando id=%s.", variacion_id)
        with connection.cursor() as cur:
            cur.execute(cls._base_select() + " WHERE v.id = %s", [variacion_id])
            row = _fetchone(cur)
        result = _str_fields(row) if row else None
        if result:
            logger.info("[VariacionTemporal.obtener] Variación encontrada.")
        else:
            logger.warning("[VariacionTemporal.obtener] No se encontró id=%s.", variacion_id)
        return result

    @classmethod
    def crear_o_reemplazar(
        cls,
        barrio_id: str,
        periodo_anterior_id: str,
        periodo_actual_id: str,
        var_simp, var_ind, var_no_simp, var_part,
        cambio: bool,
    ) -> Dict:
        logger.info(
            "[VariacionTemporal.crear_o_reemplazar] barrio_id=%s %s→%s.",
            barrio_id, periodo_anterior_id, periodo_actual_id,
        )
        new_id = str(uuid.uuid4())
        with transaction.atomic():
            with connection.cursor() as cur:
                cur.execute(
                    f"""
                    DELETE FROM {cls.TABLE}
                    WHERE barrio_id = %s
                      AND periodo_anterior_id = %s
                      AND periodo_actual_id   = %s
                    """,
                    [barrio_id, periodo_anterior_id, periodo_actual_id],
                )
                cur.execute(
                    f"""
                    INSERT INTO {cls.TABLE} (
                        id, barrio_id, periodo_anterior_id, periodo_actual_id,
                        variacion_simpatizantes, variacion_indecisos,
                        variacion_no_simpatizantes, variacion_participacion,
                        cambio_significativo
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    [
                        new_id, barrio_id, periodo_anterior_id, periodo_actual_id,
                        var_simp, var_ind, var_no_simp, var_part, cambio,
                    ],
                )
        logger.info("[VariacionTemporal.crear_o_reemplazar] Variación id=%s creada.", new_id)
        return {"id": new_id, "barrio_id": barrio_id}


# =============================================================================
# RANKING PROBLEMÁTICA
# =============================================================================

class RankingProblematica:
    TABLE = db.ranking_problematica

    _COLS = """
        r.id, r.barrio_id, r.periodo_id,
        r.problematica_cod, r.frecuencia, r.pct_frecuencia, r.posicion_ranking,
        p.etiqueta   AS periodo_etiqueta,
        pr.descripcion AS problematica_desc
    """

    @classmethod
    def _base_select(cls) -> str:
        return (
            f"SELECT {cls._COLS} "
            f"FROM {cls.TABLE} r "
            f"LEFT JOIN {db.periodo_estadistico} p  ON p.id     = r.periodo_id "
            f"LEFT JOIN {db.catalogo_problematica} pr ON pr.codigo = r.problematica_cod"
        )

    @classmethod
    def listar(cls, periodo_id=None, barrio_id=None) -> List[Dict]:
        logger.info("[RankingProblematica.listar] periodo_id=%s barrio_id=%s.", periodo_id, barrio_id)
        sql    = cls._base_select()
        params = []
        wheres = []
        if periodo_id:
            wheres.append("r.periodo_id = %s")
            params.append(periodo_id)
        if barrio_id:
            wheres.append("r.barrio_id = %s")
            params.append(barrio_id)
        if wheres:
            sql += " WHERE " + " AND ".join(wheres)
        sql += " ORDER BY r.posicion_ranking"

        with connection.cursor() as cur:
            cur.execute(sql, params)
            result = [_str_fields(r) for r in _fetchall(cur)]
        logger.info("[RankingProblematica.listar] %d entradas encontradas.", len(result))
        return result

    @classmethod
    def obtener(cls, ranking_id: str) -> Optional[Dict]:
        logger.info("[RankingProblematica.obtener] Buscando id=%s.", ranking_id)
        with connection.cursor() as cur:
            cur.execute(cls._base_select() + " WHERE r.id = %s", [ranking_id])
            row = _fetchone(cur)
        result = _str_fields(row) if row else None
        if result:
            logger.info("[RankingProblematica.obtener] Ranking encontrado.")
        else:
            logger.warning("[RankingProblematica.obtener] No se encontró id=%s.", ranking_id)
        return result

    @classmethod
    def top1_cod(cls, barrio_id: str, periodo_id: str) -> Optional[int]:
        logger.info("[RankingProblematica.top1_cod] barrio_id=%s periodo_id=%s.", barrio_id, periodo_id)
        with connection.cursor() as cur:
            cur.execute(
                f"""
                SELECT problematica_cod FROM {cls.TABLE}
                WHERE barrio_id = %s AND periodo_id = %s
                ORDER BY posicion_ranking
                LIMIT 1
                """,
                [barrio_id, periodo_id],
            )
            row = cur.fetchone()
        result = row[0] if row else None
        logger.info("[RankingProblematica.top1_cod] Top 1 = %s.", result)
        return result

    @classmethod
    def calcular_y_persistir(cls, barrio_id: str, periodo_id: str) -> List[Dict]:
        """
        Calcula la frecuencia de cada problemática para el barrio+período
        con SQL puro, elimina el ranking anterior y persiste el nuevo.
        """
        logger.info(
            "[RankingProblematica.calcular_y_persistir] barrio_id=%s periodo_id=%s.",
            barrio_id, periodo_id,
        )
        periodo = PeriodoEstadistico.obtener(periodo_id)
        if not periodo:
            logger.warning("[RankingProblematica.calcular_y_persistir] Período %s no encontrado.", periodo_id)
            return []

        with connection.cursor() as cur:
            # Conteo unificado de prob_1_cod y prob_2_cod
            cur.execute(
                f"""
                SELECT cod, SUM(frec) AS frecuencia
                FROM (
                    SELECT prob_1_cod AS cod, COUNT(*) AS frec
                    FROM {db.encuesta}
                    WHERE barrio_id = %s AND fecha >= %s AND fecha <= %s
                      AND prob_1_cod IS NOT NULL
                    GROUP BY prob_1_cod

                    UNION ALL

                    SELECT prob_2_cod AS cod, COUNT(*) AS frec
                    FROM {db.encuesta}
                    WHERE barrio_id = %s AND fecha >= %s AND fecha <= %s
                      AND prob_2_cod IS NOT NULL
                    GROUP BY prob_2_cod
                ) sub
                GROUP BY cod
                ORDER BY frecuencia DESC
                """,
                [
                    barrio_id, periodo["fecha_inicio"], periodo["fecha_fin"],
                    barrio_id, periodo["fecha_inicio"], periodo["fecha_fin"],
                ],
            )
            filas = cur.fetchall()  # [(cod, frecuencia), ...]

        if not filas:
            logger.info("[RankingProblematica.calcular_y_persistir] Sin datos de problemáticas.")
            return []

        total_global = sum(f[1] for f in filas) or 1

        with transaction.atomic():
            with connection.cursor() as cur:
                cur.execute(
                    f"DELETE FROM {cls.TABLE} WHERE barrio_id = %s AND periodo_id = %s",
                    [barrio_id, periodo_id],
                )
                nuevos = [
                    (
                        str(uuid.uuid4()), barrio_id, periodo_id, cod,
                        frec, round(frec / total_global * 100, 2), pos,
                    )
                    for pos, (cod, frec) in enumerate(filas, start=1)
                ]
                cur.executemany(
                    f"""
                    INSERT INTO {cls.TABLE}
                        (id, barrio_id, periodo_id, problematica_cod,
                         frecuencia, pct_frecuencia, posicion_ranking)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    nuevos,
                )
        logger.info(
            "[RankingProblematica.calcular_y_persistir] %d problemáticas persistidas.",
            len(nuevos),
        )
        return cls.listar(periodo_id, barrio_id)


# =============================================================================
# RESULTADO CRUCE
# =============================================================================

class ResultadoCruce:
    TABLE = db.resultado_cruce

    # Mapeo nombre dimensión → columna en la tabla encuesta
    _DIMS: Dict[str, str] = {
        "ocupacion":               "ocupacion_cod",
        "inclinacion_voto":        "inclinacion_voto_cod",
        "intencion_participacion": "intencion_participacion_cod",
        "problematica_1":          "prob_1_cod",
        "problematica_2":          "prob_2_cod",
    }

    @classmethod
    def listar(cls, periodo_id: str) -> List[Dict]:
        logger.info("[ResultadoCruce.listar] periodo_id=%s.", periodo_id)
        with connection.cursor() as cur:
            cur.execute(
                f"""
                SELECT rc.id, rc.periodo_id, rc.dimension_a, rc.valor_a,
                       rc.dimension_b, rc.valor_b, rc.cantidad, rc.porcentaje,
                       rc.generado_en, p.etiqueta AS periodo_etiqueta
                FROM {cls.TABLE} rc
                LEFT JOIN {db.periodo_estadistico} p ON p.id = rc.periodo_id
                WHERE rc.periodo_id = %s
                ORDER BY rc.generado_en DESC
                """,
                [periodo_id],
            )
            result = [_str_fields(r) for r in _fetchall(cur)]
        logger.info("[ResultadoCruce.listar] %d cruces encontrados.", len(result))
        return result

    @classmethod
    def obtener(cls, cruce_id: str) -> Optional[Dict]:
        logger.info("[ResultadoCruce.obtener] Buscando id=%s.", cruce_id)
        with connection.cursor() as cur:
            cur.execute(
                f"""
                SELECT rc.*, p.etiqueta AS periodo_etiqueta
                FROM {cls.TABLE} rc
                LEFT JOIN {db.periodo_estadistico} p ON p.id = rc.periodo_id
                WHERE rc.id = %s
                """,
                [cruce_id],
            )
            row = _fetchone(cur)
        result = _str_fields(row) if row else None
        if result:
            logger.info("[ResultadoCruce.obtener] Cruce encontrado.")
        else:
            logger.warning("[ResultadoCruce.obtener] No se encontró id=%s.", cruce_id)
        return result

    @classmethod
    def calcular_y_persistir(cls, periodo_id: str, dim_a: str, dim_b: str) -> List[Dict]:
        """
        Calcula el cruce dim_a × dim_b para el período con SQL puro,
        elimina resultados previos y persiste los nuevos.
        """
        logger.info(
            "[ResultadoCruce.calcular_y_persistir] periodo_id=%s dim_a=%s dim_b=%s.",
            periodo_id, dim_a, dim_b,
        )
        col_a = cls._DIMS.get(dim_a)
        col_b = cls._DIMS.get(dim_b)
        if not col_a or not col_b:
            logger.error(
                "[ResultadoCruce.calcular_y_persistir] Dimensiones inválidas: %s, %s.", dim_a, dim_b
            )
            raise ValueError(f"Dimensiones inválidas: {dim_a}, {dim_b}")

        periodo = PeriodoEstadistico.obtener(periodo_id)
        if not periodo:
            logger.warning("[ResultadoCruce.calcular_y_persistir] Período %s no encontrado.", periodo_id)
            return []

        with connection.cursor() as cur:
            cur.execute(
                f"""
                SELECT {col_a} AS va, {col_b} AS vb, COUNT(*) AS cantidad
                FROM {db.encuesta}
                WHERE fecha >= %s AND fecha <= %s
                  AND {col_a} IS NOT NULL
                  AND {col_b} IS NOT NULL
                GROUP BY {col_a}, {col_b}
                ORDER BY cantidad DESC
                """,
                [periodo["fecha_inicio"], periodo["fecha_fin"]],
            )
            filas = cur.fetchall()  # [(va, vb, cantidad), ...]

        total = sum(f[2] for f in filas) or 1

        with transaction.atomic():
            with connection.cursor() as cur:
                cur.execute(
                    f"""
                    DELETE FROM {cls.TABLE}
                    WHERE periodo_id = %s AND dimension_a = %s AND dimension_b = %s
                    """,
                    [periodo_id, dim_a, dim_b],
                )
                nuevos = [
                    (
                        str(uuid.uuid4()), periodo_id,
                        dim_a, str(va), dim_b, str(vb),
                        cantidad, round(cantidad / total * 100, 2),
                    )
                    for va, vb, cantidad in filas
                ]
                cur.executemany(
                    f"""
                    INSERT INTO {cls.TABLE}
                        (id, periodo_id, dimension_a, valor_a, dimension_b, valor_b,
                         cantidad, porcentaje)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    nuevos,
                )
        logger.info(
            "[ResultadoCruce.calcular_y_persistir] %d combinaciones persistidas.", len(nuevos)
        )
        return cls.listar(periodo_id)

    @classmethod
    def eliminar_por_periodo(cls, periodo_id: str) -> int:
        logger.info("[ResultadoCruce.eliminar_por_periodo] periodo_id=%s.", periodo_id)
        with connection.cursor() as cur:
            cur.execute(f"DELETE FROM {cls.TABLE} WHERE periodo_id = %s", [periodo_id])
            deleted = cur.rowcount
        logger.info("[ResultadoCruce.eliminar_por_periodo] %d registros eliminados.", deleted)
        return deleted


# =============================================================================
# CARACTERIZACIÓN TERRITORIAL
# =============================================================================

class CaracterizacionTerritorial:
    TABLE = db.caracterizacion_territorial

    _COLS = """
        c.id, c.barrio_id, c.periodo_id,
        c.afinidad_predominante, c.ocupacion_predominante,
        c.problematica_predominante_cod, c.participacion_predominante,
        c.pct_indecision, c.pct_apoyo, c.cantidad_eventos,
        c.frecuencia_problematicas, c.es_prioritario,
        c.alto_potencial_crecimiento, c.generado_en,
        p.etiqueta   AS periodo_etiqueta,
        pr.descripcion AS problematica_predominante_desc
    """

    @classmethod
    def _base_select(cls) -> str:
        return (
            f"SELECT {cls._COLS} "
            f"FROM {cls.TABLE} c "
            f"LEFT JOIN {db.periodo_estadistico} p  ON p.id     = c.periodo_id "
            f"LEFT JOIN {db.catalogo_problematica} pr ON pr.codigo = c.problematica_predominante_cod"
        )

    @classmethod
    def listar(cls, barrio_id=None, periodo_id=None) -> List[Dict]:
        logger.info(
            "[CaracterizacionTerritorial.listar] barrio_id=%s periodo_id=%s.", barrio_id, periodo_id
        )
        sql    = cls._base_select()
        params = []
        wheres = []
        if barrio_id:
            wheres.append("c.barrio_id = %s")
            params.append(barrio_id)
        if periodo_id:
            wheres.append("c.periodo_id = %s")
            params.append(periodo_id)
        if wheres:
            sql += " WHERE " + " AND ".join(wheres)
        sql += " ORDER BY c.generado_en DESC"

        with connection.cursor() as cur:
            cur.execute(sql, params)
            result = [_str_fields(r) for r in _fetchall(cur)]
        logger.info("[CaracterizacionTerritorial.listar] %d caracterizaciones encontradas.", len(result))
        return result

    @classmethod
    def obtener(cls, caracterizacion_id: str) -> Optional[Dict]:
        logger.info("[CaracterizacionTerritorial.obtener] Buscando id=%s.", caracterizacion_id)
        with connection.cursor() as cur:
            cur.execute(cls._base_select() + " WHERE c.id = %s", [caracterizacion_id])
            row = _fetchone(cur)
        result = _str_fields(row) if row else None
        if result:
            logger.info("[CaracterizacionTerritorial.obtener] Caracterización encontrada.")
        else:
            logger.warning("[CaracterizacionTerritorial.obtener] No se encontró id=%s.", caracterizacion_id)
        return result

    @classmethod
    def contar_eventos(cls, barrio_id: str) -> int:
        """Cuenta eventos del módulo externo gestion_eventos."""
        logger.info("[CaracterizacionTerritorial.contar_eventos] barrio_id=%s.", barrio_id)
        with connection.cursor() as cur:
            cur.execute(
                f"SELECT COUNT(*) FROM {db.evento} WHERE barrio_id = %s",
                [barrio_id],
            )
            count = cur.fetchone()[0]
        logger.info("[CaracterizacionTerritorial.contar_eventos] %d eventos encontrados.", count)
        return count

    @classmethod
    def crear_o_reemplazar(cls, barrio_id: str, periodo_id: str, datos: Dict) -> Dict:
        logger.info(
            "[CaracterizacionTerritorial.crear_o_reemplazar] barrio_id=%s periodo_id=%s.",
            barrio_id, periodo_id,
        )
        new_id = str(uuid.uuid4())
        with transaction.atomic():
            with connection.cursor() as cur:
                cur.execute(
                    f"DELETE FROM {cls.TABLE} WHERE barrio_id = %s AND periodo_id = %s",
                    [barrio_id, periodo_id],
                )
                cur.execute(
                    f"""
                    INSERT INTO {cls.TABLE} (
                        id, barrio_id, periodo_id,
                        afinidad_predominante, ocupacion_predominante,
                        problematica_predominante_cod, participacion_predominante,
                        pct_indecision, pct_apoyo, cantidad_eventos,
                        frecuencia_problematicas, es_prioritario,
                        alto_potencial_crecimiento
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    [
                        new_id, barrio_id, periodo_id,
                        datos.get("afinidad_predominante"),
                        datos.get("ocupacion_predominante"),
                        datos.get("problematica_predominante_cod"),
                        datos.get("participacion_predominante"),
                        datos.get("pct_indecision"),
                        datos.get("pct_apoyo"),
                        datos.get("cantidad_eventos", 0),
                        datos.get("frecuencia_problematicas"),
                        datos.get("es_prioritario", False),
                        datos.get("alto_potencial_crecimiento", False),
                    ],
                )
        logger.info(
            "[CaracterizacionTerritorial.crear_o_reemplazar] Caracterización id=%s creada.", new_id
        )
        return {"id": new_id, "barrio_id": barrio_id, "periodo_id": periodo_id}


# =============================================================================
# EXPORTACIÓN RESULTADO
# =============================================================================

class ExportacionResultado:
    TABLE = db.exportacion_resultado

    @classmethod
    def listar(cls, periodo_id=None) -> List[Dict]:
        logger.info("[ExportacionResultado.listar] periodo_id=%s.", periodo_id)
        sql    = f"""
            SELECT er.id, er.periodo_id, er.tipo_analisis, er.formato,
                   er.ruta_archivo, er.generado_en, er.coordinador_id,
                   p.etiqueta AS periodo_etiqueta
            FROM {cls.TABLE} er
            LEFT JOIN {db.periodo_estadistico} p ON p.id = er.periodo_id
        """
        params = []
        if periodo_id:
            sql += " WHERE er.periodo_id = %s"
            params.append(periodo_id)
        sql += " ORDER BY er.generado_en DESC"

        with connection.cursor() as cur:
            cur.execute(sql, params)
            result = [_str_fields(r) for r in _fetchall(cur)]
        logger.info("[ExportacionResultado.listar] %d exportaciones encontradas.", len(result))
        return result

    @classmethod
    def obtener(cls, exportacion_id: str) -> Optional[Dict]:
        logger.info("[ExportacionResultado.obtener] Buscando id=%s.", exportacion_id)
        with connection.cursor() as cur:
            cur.execute(
                f"""
                SELECT er.*, p.etiqueta AS periodo_etiqueta
                FROM {cls.TABLE} er
                LEFT JOIN {db.periodo_estadistico} p ON p.id = er.periodo_id
                WHERE er.id = %s
                """,
                [exportacion_id],
            )
            row = _fetchone(cur)
        result = _str_fields(row) if row else None
        if result:
            logger.info("[ExportacionResultado.obtener] Exportación encontrada.")
        else:
            logger.warning("[ExportacionResultado.obtener] No se encontró id=%s.", exportacion_id)
        return result

    @classmethod
    def crear(
        cls, periodo_id: str, tipo: str, formato: str,
        ruta: str, coordinador_id=None,
    ) -> Dict:
        new_id = str(uuid.uuid4())
        logger.info(
            "[ExportacionResultado.crear] Creando exportación tipo='%s' formato='%s'.", tipo, formato
        )
        with connection.cursor() as cur:
            cur.execute(
                f"""
                INSERT INTO {cls.TABLE}
                    (id, periodo_id, tipo_analisis, formato, ruta_archivo, coordinador_id)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                [new_id, periodo_id, tipo, formato, ruta, coordinador_id],
            )
        logger.info("[ExportacionResultado.crear] Exportación creada con id=%s.", new_id)
        return {"id": new_id, "periodo_id": periodo_id, "tipo_analisis": tipo}


# =============================================================================
# RESUMEN ESTADÍSTICO
# =============================================================================

class ResumenEstadistico:
    TABLE = db.resumen_estadistico

    @classmethod
    def listar(cls, barrio_id=None, periodo_id=None) -> List[Dict]:
        logger.info("[ResumenEstadistico.listar] barrio_id=%s periodo_id=%s.", barrio_id, periodo_id)
        sql    = f"""
            SELECT rs.id, rs.periodo_id, rs.barrio_id, rs.resumen_texto,
                   rs.generado_en, p.etiqueta AS periodo_etiqueta
            FROM {cls.TABLE} rs
            LEFT JOIN {db.periodo_estadistico} p ON p.id = rs.periodo_id
        """
        params = []
        wheres = []
        if barrio_id:
            wheres.append("rs.barrio_id = %s")
            params.append(barrio_id)
        if periodo_id:
            wheres.append("rs.periodo_id = %s")
            params.append(periodo_id)
        if wheres:
            sql += " WHERE " + " AND ".join(wheres)
        sql += " ORDER BY rs.generado_en DESC"

        with connection.cursor() as cur:
            cur.execute(sql, params)
            result = [_str_fields(r) for r in _fetchall(cur)]
        logger.info("[ResumenEstadistico.listar] %d resúmenes encontrados.", len(result))
        return result

    @classmethod
    def obtener(cls, resumen_id: str) -> Optional[Dict]:
        logger.info("[ResumenEstadistico.obtener] Buscando id=%s.", resumen_id)
        with connection.cursor() as cur:
            cur.execute(
                f"""
                SELECT rs.*, p.etiqueta AS periodo_etiqueta
                FROM {cls.TABLE} rs
                LEFT JOIN {db.periodo_estadistico} p ON p.id = rs.periodo_id
                WHERE rs.id = %s
                """,
                [resumen_id],
            )
            row = _fetchone(cur)
        result = _str_fields(row) if row else None
        if result:
            logger.info("[ResumenEstadistico.obtener] Resumen encontrado.")
        else:
            logger.warning("[ResumenEstadistico.obtener] No se encontró id=%s.", resumen_id)
        return result

    @classmethod
    def crear_o_reemplazar(cls, barrio_id: str, periodo_id: str, texto: str) -> Dict:
        logger.info(
            "[ResumenEstadistico.crear_o_reemplazar] barrio_id=%s periodo_id=%s.", barrio_id, periodo_id
        )
        new_id = str(uuid.uuid4())
        with transaction.atomic():
            with connection.cursor() as cur:
                cur.execute(
                    f"DELETE FROM {cls.TABLE} WHERE barrio_id = %s AND periodo_id = %s",
                    [barrio_id, periodo_id],
                )
                cur.execute(
                    f"""
                    INSERT INTO {cls.TABLE} (id, periodo_id, barrio_id, resumen_texto)
                    VALUES (%s, %s, %s, %s)
                    """,
                    [new_id, periodo_id, barrio_id, texto],
                )
        logger.info("[ResumenEstadistico.crear_o_reemplazar] Resumen id=%s creado.", new_id)
        return {"id": new_id, "barrio_id": barrio_id, "periodo_id": periodo_id}