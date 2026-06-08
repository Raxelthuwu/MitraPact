import logging
from asgiref.sync import sync_to_async
from django.db import connection
from app import db

logger = logging.getLogger(__name__)


def _ejecutar(sql, params=None, fetchone=False, fetchall=False):
    with connection.cursor() as cursor:
        cursor.execute(sql, params or [])
        if fetchone:
            row = cursor.fetchone()
            if row is None:
                return None
            cols = [col.name for col in cursor.description]
            return dict(zip(cols, row))
        if fetchall:
            rows = cursor.fetchall()
            cols = [col.name for col in cursor.description]
            return [dict(zip(cols, row)) for row in rows]
        return None

_query = sync_to_async(_ejecutar, thread_sensitive=True)


class OpinionClasificada:

    # INSERT

    @staticmethod
    async def insertar(encuestaId: str, barrioId: str, tema: str) -> dict | None:
        logger.info(f"[OpinionClasificada] Insertando opinión | encuesta_id: '{encuestaId}' | tema: '{tema}'")
        sql = f"""
            INSERT INTO {db.opinion_clasificada} (encuesta_id, barrio_id, tema, clasificado_en)
            VALUES (%s, %s, %s, NOW())
            RETURNING id, encuesta_id, barrio_id, tema, clasificado_en
        """
        try:
            return await _query(sql, [encuestaId, barrioId, tema], fetchone=True)
        except Exception as e:
            logger.error(f"[OpinionClasificada] Error al insertar: {e}")
            raise

    @staticmethod
    async def insertarBatch(opiniones: list[dict]) -> list[dict]:
        logger.info(f"[OpinionClasificada] Insertando lote de {len(opiniones)} opiniones.")
        sql = f"""
            INSERT INTO {db.opinion_clasificada} (encuesta_id, barrio_id, tema, clasificado_en)
            VALUES (%s, %s, %s, NOW())
            RETURNING id, encuesta_id, barrio_id, tema, clasificado_en
        """
        def _batch():
            resultados = []
            with connection.cursor() as cursor:
                for o in opiniones:
                    cursor.execute(sql, [o['encuestaId'], o['barrioId'], o['tema']])
                    row = cursor.fetchone()
                    if row:
                        cols = [col.name for col in cursor.description]
                        resultados.append(dict(zip(cols, row)))
            return resultados
        try:
            return await sync_to_async(_batch, thread_sensitive=True)()
        except Exception as e:
            logger.error(f"[OpinionClasificada] Error en insertarBatch: {e}")
            raise

    # UPDATE

    @staticmethod
    async def actualizar(opinionId: str, tema: str) -> dict | None:
        logger.info(f"[OpinionClasificada] Actualizando opinión id: '{opinionId}' -> tema: '{tema}'")
        sql = f"""
            UPDATE {db.opinion_clasificada}
            SET tema = %s
            WHERE id = %s
            RETURNING id, encuesta_id, barrio_id, tema, clasificado_en
        """
        try:
            return await _query(sql, [tema, opinionId], fetchone=True)
        except Exception as e:
            logger.error(f"[OpinionClasificada] Error al actualizar: {e}")
            raise

    # GET — lógica interna

    @staticmethod
    async def obtenerPorId(opinionId: str) -> dict | None:
        logger.info(f"[OpinionClasificada] Buscando opinión por id: '{opinionId}'")
        sql = f"""
            SELECT id, encuesta_id, barrio_id, tema, clasificado_en
            FROM {db.opinion_clasificada}
            WHERE id = %s
        """
        try:
            return await _query(sql, [opinionId], fetchone=True)
        except Exception as e:
            logger.error(f"[OpinionClasificada] Error en obtenerPorId: {e}")
            raise

    @staticmethod
    async def obtenerPorEncuesta(encuestaId: str) -> list[dict]:
        logger.info(f"[OpinionClasificada] Obteniendo opiniones de encuesta_id: '{encuestaId}'")
        sql = f"""
            SELECT id, encuesta_id, barrio_id, tema, clasificado_en
            FROM {db.opinion_clasificada}
            WHERE encuesta_id = %s
            ORDER BY clasificado_en DESC
        """
        try:
            return await _query(sql, [encuestaId], fetchall=True)
        except Exception as e:
            logger.error(f"[OpinionClasificada] Error en obtenerPorEncuesta: {e}")
            raise

    @staticmethod
    async def obtenerPorBarrio(barrioId: str) -> list[dict]:
        logger.info(f"[OpinionClasificada] Obteniendo opiniones de barrio_id: '{barrioId}'")
        sql = f"""
            SELECT id, encuesta_id, barrio_id, tema, clasificado_en
            FROM {db.opinion_clasificada}
            WHERE barrio_id = %s
            ORDER BY clasificado_en DESC
        """
        try:
            return await _query(sql, [barrioId], fetchall=True)
        except Exception as e:
            logger.error(f"[OpinionClasificada] Error en obtenerPorBarrio: {e}")
            raise

    # GET — orientado a usuario

    @staticmethod
    async def buscarPorTema(tema: str) -> list[dict]:
        logger.info(f"[OpinionClasificada] Buscando opiniones por tema: '{tema}'")
        sql = f"""
            SELECT
                o.id,
                o.tema,
                o.clasificado_en,
                b.nombre    AS barrio_nombre
            FROM {db.opinion_clasificada} o
            JOIN {db.barrio} b ON b.id = o.barrio_id
            WHERE o.tema ILIKE %s
            ORDER BY o.clasificado_en DESC
        """
        try:
            return await _query(sql, [f"%{tema}%"], fetchall=True)
        except Exception as e:
            logger.error(f"[OpinionClasificada] Error en buscarPorTema: {e}")
            raise

    @staticmethod
    async def buscarPorBarrioYTema(barrioId: str, tema: str) -> list[dict]:
        logger.info(f"[OpinionClasificada] Buscando por barrio_id: '{barrioId}' y tema: '{tema}'")
        sql = f"""
            SELECT
                o.id,
                o.tema,
                o.clasificado_en,
                b.nombre    AS barrio_nombre
            FROM {db.opinion_clasificada} o
            JOIN {db.barrio} b ON b.id = o.barrio_id
            WHERE o.barrio_id = %s AND o.tema ILIKE %s
            ORDER BY o.clasificado_en DESC
        """
        try:
            return await _query(sql, [barrioId, f"%{tema}%"], fetchall=True)
        except Exception as e:
            logger.error(f"[OpinionClasificada] Error en buscarPorBarrioYTema: {e}")
            raise

    @staticmethod
    async def resumenPorBarrio(barrioId: str) -> list[dict]:
        logger.info(f"[OpinionClasificada] Resumen por tema para barrio_id: '{barrioId}'")
        sql = f"""
            SELECT
                o.tema,
                COUNT(*) AS total,
                b.nombre  AS barrio_nombre
            FROM {db.opinion_clasificada} o
            JOIN {db.barrio} b ON b.id = o.barrio_id
            WHERE o.barrio_id = %s
            GROUP BY o.tema, b.nombre
            ORDER BY total DESC
        """
        try:
            return await _query(sql, [barrioId], fetchall=True)
        except Exception as e:
            logger.error(f"[OpinionClasificada] Error en resumenPorBarrio: {e}")
            raise

    @staticmethod
    async def buscarParaSelector(texto: str) -> list[dict]:
        """
        Busca opiniones por texto de encuesta o tema para el selector del modal.
        Retorna id, resumen del texto de opinión, tema y barrio.
        """
        logger.info(f"[OpinionClasificada] Buscando para selector: '{texto}'")
        sql = f"""
            SELECT
                o.id,
                o.tema,
                b.nombre                    AS barrio_nombre,
                LEFT(e.opinion_politica, 80) AS opinion_texto
            FROM {db.opinion_clasificada} o
            JOIN {db.barrio} b   ON b.id = o.barrio_id
            JOIN {db.encuesta} e ON e.id = o.encuesta_id
            WHERE e.opinion_politica ILIKE %s
            OR o.tema ILIKE %s
            ORDER BY o.clasificado_en DESC
            LIMIT 20
        """
        try:
            return await _query(sql, [f"%{texto}%", f"%{texto}%"], fetchall=True)
        except Exception as e:
            logger.error(f"[OpinionClasificada] Error en buscarParaSelector: {e}")
            raise