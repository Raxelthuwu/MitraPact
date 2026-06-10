import logging
from asgiref.sync import sync_to_async
from django.db import connection
from app import db

logger = logging.getLogger(__name__)


def _ejecutar(sql, params=None, fetchone=False, fetchall=False, rowcount=False):
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
        if rowcount:
            return cursor.rowcount
        return None


_query = sync_to_async(_ejecutar, thread_sensitive=True)


class Argumento:

    # -------------------------------------------------------------------------
    # INSERT
    # -------------------------------------------------------------------------

    @staticmethod
    async def insertar(
        opinionId: str,
        texto: str,
        tema: str,
        problematicaCod: int,
        frecuencia: int,
    ) -> dict | None:
        logger.info(f"[Argumento] Insertando argumento | opinion_id: '{opinionId}' | tema: '{tema}'")
        sql = f"""
            INSERT INTO {db.argumento}
                (opinion_id, texto, tema, problematica_cod, frecuencia, identificado_en)
            VALUES (%s, %s, %s, %s, %s, NOW())
            RETURNING id, opinion_id, texto, tema, problematica_cod, frecuencia, identificado_en
        """
        try:
            return await _query(sql, [opinionId, texto, tema, problematicaCod, frecuencia], fetchone=True)
        except Exception as e:
            logger.error(f"[Argumento] Error al insertar: {e}")
            raise

    @staticmethod
    async def insertarBatch(argumentos: list[dict]) -> list[dict]:
        logger.info(f"[Argumento] Insertando lote de {len(argumentos)} argumentos.")
        sql = f"""
            INSERT INTO {db.argumento}
                (opinion_id, texto, tema, problematica_cod, frecuencia, identificado_en)
            VALUES (%s, %s, %s, %s, %s, NOW())
            RETURNING id, opinion_id, texto, tema, problematica_cod, frecuencia, identificado_en
        """

        def _batch():
            resultados = []
            with connection.cursor() as cursor:
                for a in argumentos:
                    cursor.execute(sql, [
                        a['opinionId'], a['texto'], a['tema'],
                        a['problematicaCod'], a['frecuencia'],
                    ])
                    row = cursor.fetchone()
                    if row:
                        cols = [col.name for col in cursor.description]
                        resultados.append(dict(zip(cols, row)))
            return resultados

        try:
            return await sync_to_async(_batch, thread_sensitive=True)()
        except Exception as e:
            logger.error(f"[Argumento] Error en insertarBatch: {e}")
            raise

    # -------------------------------------------------------------------------
    # UPDATE
    # -------------------------------------------------------------------------

    @staticmethod
    async def actualizar(
        argumentoId: str,
        texto: str = None,
        frecuencia: int = None,
        tema: str = None,
        problematicaCod: int = None,
    ) -> dict | None:
        logger.info(f"[Argumento] Actualizando argumento id: '{argumentoId}'")
        campos, valores = [], []

        if texto is not None:
            campos.append("texto = %s"); valores.append(texto)
        if frecuencia is not None:
            campos.append("frecuencia = %s"); valores.append(frecuencia)
        if tema is not None:
            campos.append("tema = %s"); valores.append(tema)
        if problematicaCod is not None:
            campos.append("problematica_cod = %s"); valores.append(problematicaCod)

        if not campos:
            logger.warning("[Argumento] No se proporcionaron campos para actualizar.")
            return None

        valores.append(argumentoId)
        sql = f"""
            UPDATE {db.argumento}
            SET {', '.join(campos)}
            WHERE id = %s
            RETURNING id, opinion_id, texto, tema, problematica_cod, frecuencia, identificado_en
        """
        try:
            return await _query(sql, valores, fetchone=True)
        except Exception as e:
            logger.error(f"[Argumento] Error al actualizar: {e}")
            raise

    @staticmethod
    async def incrementarFrecuencia(argumentoId: str) -> dict | None:
        """Suma 1 a la frecuencia del argumento indicado."""
        logger.info(f"[Argumento] Incrementando frecuencia del argumento id: '{argumentoId}'")
        sql = f"""
            UPDATE {db.argumento}
            SET frecuencia = frecuencia + 1
            WHERE id = %s
            RETURNING id, opinion_id, texto, tema, problematica_cod, frecuencia, identificado_en
        """
        try:
            return await _query(sql, [argumentoId], fetchone=True)
        except Exception as e:
            logger.error(f"[Argumento] Error en incrementarFrecuencia: {e}")
            raise

    # -------------------------------------------------------------------------
    # DELETE
    # -------------------------------------------------------------------------

    @staticmethod
    async def eliminar(argumentoId: str) -> bool:
        logger.info(f"[Argumento] Eliminando argumento id: '{argumentoId}'")
        sql = f"DELETE FROM {db.argumento} WHERE id = %s"
        try:
            filas = await _query(sql, [argumentoId], rowcount=True)
            return (filas or 0) > 0
        except Exception as e:
            logger.error(f"[Argumento] Error al eliminar: {e}")
            raise

    # -------------------------------------------------------------------------
    # GET — lógica interna
    # -------------------------------------------------------------------------

    @staticmethod
    async def obtenerPorId(argumentoId: str) -> dict | None:
        logger.info(f"[Argumento] Buscando argumento por id: '{argumentoId}'")
        sql = f"""
            SELECT id, opinion_id, texto, tema, problematica_cod, frecuencia, identificado_en
            FROM {db.argumento}
            WHERE id = %s
        """
        try:
            return await _query(sql, [argumentoId], fetchone=True)
        except Exception as e:
            logger.error(f"[Argumento] Error en obtenerPorId: {e}")
            raise

    @staticmethod
    async def obtenerPorOpinion(opinionId: str) -> list[dict]:
        logger.info(f"[Argumento] Obteniendo argumentos de opinion_id: '{opinionId}'")
        sql = f"""
            SELECT id, opinion_id, texto, tema, problematica_cod, frecuencia, identificado_en
            FROM {db.argumento}
            WHERE opinion_id = %s
            ORDER BY frecuencia DESC
        """
        try:
            return await _query(sql, [opinionId], fetchall=True)
        except Exception as e:
            logger.error(f"[Argumento] Error en obtenerPorOpinion: {e}")
            raise

    @staticmethod
    async def obtenerPorProblematica(problematicaCod: int) -> list[dict]:
        logger.info(f"[Argumento] Obteniendo argumentos de problematica_cod: {problematicaCod}")
        sql = f"""
            SELECT id, opinion_id, texto, tema, problematica_cod, frecuencia, identificado_en
            FROM {db.argumento}
            WHERE problematica_cod = %s
            ORDER BY frecuencia DESC
        """
        try:
            return await _query(sql, [problematicaCod], fetchall=True)
        except Exception as e:
            logger.error(f"[Argumento] Error en obtenerPorProblematica: {e}")
            raise

    # -------------------------------------------------------------------------
    # GET — orientado a usuario
    # -------------------------------------------------------------------------

    @staticmethod
    async def buscarPorTema(tema: str) -> list[dict]:
        logger.info(f"[Argumento] Buscando argumentos por tema: '{tema}'")
        sql = f"""
            SELECT
                a.id, a.texto, a.tema, a.frecuencia, a.identificado_en,
                cp.descripcion AS problematica_descripcion
            FROM {db.argumento} a
            JOIN {db.catalogo_problematica} cp ON cp.codigo = a.problematica_cod
            WHERE a.tema ILIKE %s
            ORDER BY a.frecuencia DESC
        """
        try:
            return await _query(sql, [f"%{tema}%"], fetchall=True)
        except Exception as e:
            logger.error(f"[Argumento] Error en buscarPorTema: {e}")
            raise

    @staticmethod
    async def buscarPorProblematicaConDescripcion(problematicaCod: int) -> list[dict]:
        logger.info(f"[Argumento] Buscando argumentos por problematica_cod: {problematicaCod}")
        sql = f"""
            SELECT
                a.id, a.texto, a.tema, a.frecuencia, a.identificado_en,
                cp.descripcion AS problematica_descripcion
            FROM {db.argumento} a
            JOIN {db.catalogo_problematica} cp ON cp.codigo = a.problematica_cod
            WHERE a.problematica_cod = %s
            ORDER BY a.frecuencia DESC
        """
        try:
            return await _query(sql, [problematicaCod], fetchall=True)
        except Exception as e:
            logger.error(f"[Argumento] Error en buscarPorProblematicaConDescripcion: {e}")
            raise

    @staticmethod
    async def listarMasFrecuentesPorTema(tema: str, limite: int = 10) -> list[dict]:
        logger.info(f"[Argumento] Top {limite} argumentos más frecuentes para tema: '{tema}'")
        sql = f"""
            SELECT
                a.id, a.texto, a.tema, a.frecuencia, a.identificado_en,
                cp.descripcion AS problematica_descripcion
            FROM {db.argumento} a
            JOIN {db.catalogo_problematica} cp ON cp.codigo = a.problematica_cod
            WHERE a.tema ILIKE %s
            ORDER BY a.frecuencia DESC
            LIMIT %s
        """
        try:
            return await _query(sql, [f"%{tema}%", limite], fetchall=True)
        except Exception as e:
            logger.error(f"[Argumento] Error en listarMasFrecuentesPorTema: {e}")
            raise

    @staticmethod
    async def topPorBarrio(barrioId: str, limite: int = 20) -> list[dict]:
        """
        Devuelve los argumentos más frecuentes de un barrio, enriquecidos con:
        - opinión de la encuesta original
        - documento relacionado (si existe vía argumento_documento)
        - barrio
        Ordenados por frecuencia descendente.
        """
        logger.info(f"[Argumento] Top {limite} argumentos para barrio_id: '{barrioId}'")
        sql = f"""
            SELECT
                a.id,
                a.texto,
                a.tema,
                a.frecuencia,
                a.problematica_cod,
                cp.descripcion                  AS problematica_descripcion,
                a.identificado_en,
                -- opinión original
                oc.id                           AS opinion_id,
                e.opinion_politica              AS opinion_texto,
                -- barrio
                b.nombre                        AS barrio_nombre,
                -- documento vinculado (el más reciente si hay varios)
                d.id                            AS documento_id,
                d.nombre                        AS documento_nombre,
                d.nombre_archivo                AS documento_archivo
            FROM {db.argumento} a
            JOIN {db.opinion_clasificada}   oc ON oc.id      = a.opinion_id
            JOIN {db.encuesta}              e  ON e.id       = oc.encuesta_id
            JOIN {db.barrio}                b  ON b.id       = oc.barrio_id
            JOIN {db.catalogo_problematica} cp ON cp.codigo  = a.problematica_cod
            -- documento: LEFT JOIN porque puede no haber ninguno vinculado
            LEFT JOIN LATERAL (
                SELECT ad.documento_id
                FROM {db.argumento_documento} ad
                WHERE ad.argumento_id = a.id
                ORDER BY ad.id DESC
                LIMIT 1
            ) ad ON true
            LEFT JOIN {db.documento} d ON d.id = ad.documento_id
            WHERE oc.barrio_id = %s
            ORDER BY a.frecuencia DESC
            LIMIT %s
        """
        try:
            return await _query(sql, [barrioId, limite], fetchall=True)
        except Exception as e:
            logger.error(f"[Argumento] Error en topPorBarrio: {e}")
            raise

    @staticmethod
    async def topGlobal(limite: int = 50) -> list[dict]:
        """
        Igual que topPorBarrio pero sin filtro de barrio.
        Útil para el dashboard general de búsqueda semántica.
        """
        logger.info(f"[Argumento] Top {limite} argumentos globales.")
        sql = f"""
            SELECT
                a.id,
                a.texto,
                a.tema,
                a.frecuencia,
                a.problematica_cod,
                cp.descripcion                  AS problematica_descripcion,
                a.identificado_en,
                oc.id                           AS opinion_id,
                e.opinion_politica              AS opinion_texto,
                b.nombre                        AS barrio_nombre,
                d.id                            AS documento_id,
                d.nombre                        AS documento_nombre,
                d.nombre_archivo                AS documento_archivo
            FROM {db.argumento} a
            JOIN {db.opinion_clasificada}   oc ON oc.id      = a.opinion_id
            JOIN {db.encuesta}              e  ON e.id       = oc.encuesta_id
            JOIN {db.barrio}                b  ON b.id       = oc.barrio_id
            JOIN {db.catalogo_problematica} cp ON cp.codigo  = a.problematica_cod
            LEFT JOIN LATERAL (
                SELECT ad.documento_id
                FROM {db.argumento_documento} ad
                WHERE ad.argumento_id = a.id
                ORDER BY ad.id DESC
                LIMIT 1
            ) ad ON true
            LEFT JOIN {db.documento} d ON d.id = ad.documento_id
            ORDER BY a.frecuencia DESC
            LIMIT %s
        """
        try:
            return await _query(sql, [limite], fetchall=True)
        except Exception as e:
            logger.error(f"[Argumento] Error en topGlobal: {e}")
            raise