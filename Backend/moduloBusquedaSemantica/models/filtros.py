import logging
from asgiref.sync import sync_to_async
from django.db import connection
from app import db

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helper compartido
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# FiltroSemantico
# ---------------------------------------------------------------------------

class FiltroSemantico:

    # -------------------------------------------------------------------------
    # ARGUMENTOS
    # -------------------------------------------------------------------------

    @staticmethod
    async def argumentosMasFrecuentesPorProblematica(problematicaCod: int, limite: int = 10) -> list[dict]:
        logger.info(f"[FiltroSemantico] Top {limite} argumentos para problematica_cod: {problematicaCod}")
        sql = f"""
            SELECT
                a.id,
                a.texto,
                a.tema,
                a.frecuencia,
                a.identificado_en,
                cp.descripcion AS problematica_descripcion
            FROM {db.argumento} a
            JOIN {db.catalogo_problematica} cp ON cp.codigo = a.problematica_cod
            WHERE a.problematica_cod = %s
            ORDER BY a.frecuencia DESC
            LIMIT %s
        """
        try:
            return await _query(sql, [problematicaCod, limite], fetchall=True)
        except Exception as e:
            logger.error(f"[FiltroSemantico] Error en argumentosMasFrecuentesPorProblematica: {e}")
            raise

    @staticmethod
    async def distribucionArgumentosPorProblematica() -> list[dict]:
        logger.info("[FiltroSemantico] Distribución de argumentos por problemática.")
        sql = f"""
            SELECT
                cp.codigo,
                cp.descripcion,
                COUNT(a.id)        AS total_argumentos,
                SUM(a.frecuencia)  AS frecuencia_acumulada
            FROM {db.argumento} a
            JOIN {db.catalogo_problematica} cp ON cp.codigo = a.problematica_cod
            GROUP BY cp.codigo, cp.descripcion
            ORDER BY frecuencia_acumulada DESC
        """
        try:
            return await _query(sql, fetchall=True)
        except Exception as e:
            logger.error(f"[FiltroSemantico] Error en distribucionArgumentosPorProblematica: {e}")
            raise

    @staticmethod
    async def argumentosPorBarrio(barrioId: str, limite: int = 10) -> list[dict]:
        logger.info(f"[FiltroSemantico] Argumentos por barrio_id: '{barrioId}'")
        sql = f"""
            SELECT
                a.id,
                a.texto,
                a.tema,
                a.frecuencia,
                cp.descripcion  AS problematica_descripcion,
                b.nombre        AS barrio_nombre
            FROM {db.argumento} a
            JOIN {db.opinion_clasificada} o    ON o.id = a.opinion_id
            JOIN {db.barrio} b                 ON b.id = o.barrio_id
            JOIN {db.catalogo_problematica} cp ON cp.codigo = a.problematica_cod
            WHERE o.barrio_id = %s
            ORDER BY a.frecuencia DESC
            LIMIT %s
        """
        try:
            return await _query(sql, [barrioId, limite], fetchall=True)
        except Exception as e:
            logger.error(f"[FiltroSemantico] Error en argumentosPorBarrio: {e}")
            raise

    @staticmethod
    async def evolucionFrecuenciaArgumento(argumentoId: str) -> dict | None:
        logger.info(f"[FiltroSemantico] Evolución de frecuencia para argumento_id: '{argumentoId}'")
        sql = f"""
            SELECT
                a.id,
                a.texto,
                a.tema,
                a.frecuencia,
                a.identificado_en,
                cp.descripcion  AS problematica_descripcion,
                NOW() - a.identificado_en AS tiempo_activo
            FROM {db.argumento} a
            JOIN {db.catalogo_problematica} cp ON cp.codigo = a.problematica_cod
            WHERE a.id = %s
        """
        try:
            return await _query(sql, [argumentoId], fetchone=True)
        except Exception as e:
            logger.error(f"[FiltroSemantico] Error en evolucionFrecuenciaArgumento: {e}")
            raise

    @staticmethod
    async def argumentosSinDocumentoVinculado() -> list[dict]:
        logger.info("[FiltroSemantico] Buscando argumentos sin documento vinculado.")
        sql = f"""
            SELECT
                a.id,
                a.texto,
                a.tema,
                a.frecuencia,
                a.identificado_en,
                cp.descripcion  AS problematica_descripcion
            FROM {db.argumento} a
            JOIN {db.catalogo_problematica} cp ON cp.codigo = a.problematica_cod
            WHERE NOT EXISTS (
                SELECT 1
                FROM {db.argumento_documento} ad
                WHERE ad.argumento_id = a.id
            )
            ORDER BY a.frecuencia DESC
        """
        try:
            return await _query(sql, fetchall=True)
        except Exception as e:
            logger.error(f"[FiltroSemantico] Error en argumentosSinDocumentoVinculado: {e}")
            raise

    # -------------------------------------------------------------------------
    # OPINIONES
    # -------------------------------------------------------------------------

    @staticmethod
    async def distribucionOpinionesPorBarrio() -> list[dict]:
        logger.info("[FiltroSemantico] Distribución de opiniones por barrio.")
        sql = f"""
            SELECT
                b.id            AS barrio_id,
                b.nombre        AS barrio_nombre,
                o.tema,
                COUNT(o.id)     AS total_opiniones
            FROM {db.opinion_clasificada} o
            JOIN {db.barrio} b ON b.id = o.barrio_id
            GROUP BY b.id, b.nombre, o.tema
            ORDER BY b.nombre ASC, total_opiniones DESC
        """
        try:
            return await _query(sql, fetchall=True)
        except Exception as e:
            logger.error(f"[FiltroSemantico] Error en distribucionOpinionesPorBarrio: {e}")
            raise

    @staticmethod
    async def temasMasRecurrentesPorBarrio(barrioId: str) -> list[dict]:
        logger.info(f"[FiltroSemantico] Temas recurrentes para barrio_id: '{barrioId}'")
        sql = f"""
            SELECT
                o.tema,
                COUNT(o.id)  AS total,
                b.nombre     AS barrio_nombre
            FROM {db.opinion_clasificada} o
            JOIN {db.barrio} b ON b.id = o.barrio_id
            WHERE o.barrio_id = %s
            GROUP BY o.tema, b.nombre
            ORDER BY total DESC
        """
        try:
            return await _query(sql, [barrioId], fetchall=True)
        except Exception as e:
            logger.error(f"[FiltroSemantico] Error en temasMasRecurrentesPorBarrio: {e}")
            raise

    @staticmethod
    async def opinionesPorRangoFecha(fechaInicio: str, fechaFin: str) -> list[dict]:
        logger.info(f"[FiltroSemantico] Opiniones entre {fechaInicio} y {fechaFin}")
        sql = f"""
            SELECT
                o.id,
                o.tema,
                o.clasificado_en,
                b.nombre    AS barrio_nombre
            FROM {db.opinion_clasificada} o
            JOIN {db.barrio} b ON b.id = o.barrio_id
            WHERE o.clasificado_en BETWEEN %s AND %s
            ORDER BY o.clasificado_en DESC
        """
        try:
            return await _query(sql, [fechaInicio, fechaFin], fetchall=True)
        except Exception as e:
            logger.error(f"[FiltroSemantico] Error en opinionesPorRangoFecha: {e}")
            raise

    @staticmethod
    async def distribucionOpinionesPorTema() -> list[dict]:
        logger.info("[FiltroSemantico] Distribución global de opiniones por tema.")
        sql = f"""
            SELECT
                o.tema,
                COUNT(o.id)  AS total_opiniones
            FROM {db.opinion_clasificada} o
            GROUP BY o.tema
            ORDER BY total_opiniones DESC
        """
        try:
            return await _query(sql, fetchall=True)
        except Exception as e:
            logger.error(f"[FiltroSemantico] Error en distribucionOpinionesPorTema: {e}")
            raise

    # -------------------------------------------------------------------------
    # DOCUMENTOS
    # -------------------------------------------------------------------------

    @staticmethod
    async def documentosConMasArgumentos(limite: int = 10) -> list[dict]:
        logger.info(f"[FiltroSemantico] Top {limite} documentos con más argumentos vinculados.")
        sql = f"""
            SELECT
                d.id,
                d.nombre,
                d.nombre_archivo,
                d.registrado_en,
                COUNT(ad.argumento_id)  AS total_argumentos
            FROM {db.documento} d
            JOIN {db.argumento_documento} ad ON ad.documento_id = d.id
            GROUP BY d.id, d.nombre, d.nombre_archivo, d.registrado_en
            ORDER BY total_argumentos DESC
            LIMIT %s
        """
        try:
            return await _query(sql, [limite], fetchall=True)
        except Exception as e:
            logger.error(f"[FiltroSemantico] Error en documentosConMasArgumentos: {e}")
            raise

    @staticmethod
    async def documentosPorProblematica(problematicaCod: int) -> list[dict]:
        logger.info(f"[FiltroSemantico] Documentos vinculados a problematica_cod: {problematicaCod}")
        sql = f"""
            SELECT DISTINCT
                d.id,
                d.nombre,
                d.nombre_archivo,
                d.registrado_en,
                cp.descripcion  AS problematica_descripcion
            FROM {db.documento} d
            JOIN {db.argumento_documento} ad   ON ad.documento_id = d.id
            JOIN {db.argumento} a              ON a.id = ad.argumento_id
            JOIN {db.catalogo_problematica} cp ON cp.codigo = a.problematica_cod
            WHERE a.problematica_cod = %s
            ORDER BY d.registrado_en DESC
        """
        try:
            return await _query(sql, [problematicaCod], fetchall=True)
        except Exception as e:
            logger.error(f"[FiltroSemantico] Error en documentosPorProblematica: {e}")
            raise

    @staticmethod
    async def documentosSinArgumentos() -> list[dict]:
        logger.info("[FiltroSemantico] Buscando documentos sin argumentos vinculados.")
        sql = f"""
            SELECT
                d.id,
                d.nombre,
                d.nombre_archivo,
                d.registrado_en
            FROM {db.documento} d
            WHERE NOT EXISTS (
                SELECT 1
                FROM {db.argumento_documento} ad
                WHERE ad.documento_id = d.id
            )
            ORDER BY d.registrado_en DESC
        """
        try:
            return await _query(sql, fetchall=True)
        except Exception as e:
            logger.error(f"[FiltroSemantico] Error en documentosSinArgumentos: {e}")
            raise

    @staticmethod
    async def fragmentosPorDocumentoConConteo() -> list[dict]:
        logger.info("[FiltroSemantico] Conteo de fragmentos por documento.")
        sql = f"""
            SELECT
                d.id,
                d.nombre,
                d.nombre_archivo,
                d.registrado_en,
                COUNT(f.id)  AS total_fragmentos
            FROM {db.documento} d
            LEFT JOIN {db.fragmento} f ON f.documento_id = d.id
            GROUP BY d.id, d.nombre, d.nombre_archivo, d.registrado_en
            ORDER BY d.registrado_en DESC
        """
        try:
            return await _query(sql, fetchall=True)
        except Exception as e:
            logger.error(f"[FiltroSemantico] Error en fragmentosPorDocumentoConConteo: {e}")
            raise

    # -------------------------------------------------------------------------
    # CRUCE GENERAL
    # -------------------------------------------------------------------------

    @staticmethod
    async def resumenGeneralPorBarrio(barrioId: str) -> dict:
        logger.info(f"[FiltroSemantico] Resumen general para barrio_id: '{barrioId}'")
        sql = f"""
            SELECT
                b.nombre                        AS barrio_nombre,
                COUNT(DISTINCT o.id)            AS total_opiniones,
                COUNT(DISTINCT o.tema)          AS temas_unicos,
                COUNT(DISTINCT a.id)            AS total_argumentos,
                COALESCE(SUM(a.frecuencia), 0)  AS frecuencia_acumulada
            FROM {db.barrio} b
            LEFT JOIN {db.opinion_clasificada} o ON o.barrio_id = b.id
            LEFT JOIN {db.argumento} a           ON a.opinion_id = o.id
            WHERE b.id = %s
            GROUP BY b.nombre
        """
        try:
            result = await _query(sql, [barrioId], fetchone=True)
            return result or {}
        except Exception as e:
            logger.error(f"[FiltroSemantico] Error en resumenGeneralPorBarrio: {e}")
            raise

    @staticmethod
    async def cruzarBarrioProblematica(barrioId: str, problematicaCod: int) -> dict:
        logger.info(f"[FiltroSemantico] Cruce barrio_id: '{barrioId}' x problematica_cod: {problematicaCod}")
        sql = f"""
            SELECT
                b.nombre                        AS barrio_nombre,
                cp.descripcion                  AS problematica_descripcion,
                COUNT(DISTINCT o.id)            AS total_opiniones,
                COUNT(DISTINCT a.id)            AS total_argumentos,
                COALESCE(SUM(a.frecuencia), 0)  AS frecuencia_acumulada
            FROM {db.barrio} b
            LEFT JOIN {db.opinion_clasificada} o ON o.barrio_id = b.id
            LEFT JOIN {db.argumento} a           ON a.opinion_id = o.id
                                               AND a.problematica_cod = %s
            JOIN {db.catalogo_problematica} cp   ON cp.codigo = %s
            WHERE b.id = %s
            GROUP BY b.nombre, cp.descripcion
        """
        try:
            result = await _query(sql, [problematicaCod, problematicaCod, barrioId], fetchone=True)
            return result or {}
        except Exception as e:
            logger.error(f"[FiltroSemantico] Error en cruzarBarrioProblematica: {e}")
            raise


# ---------------------------------------------------------------------------
# Barrio
# ---------------------------------------------------------------------------

class Barrio:
    """
    Clase de acceso a la tabla gestion_eventos.barrio.
    Solo lectura desde este módulo — barrio es una entidad compartida
    gestionada por el módulo de gestión de eventos.
    """

    @staticmethod
    async def obtenerPorId(barrioId: str) -> dict | None:
        logger.info(f"[Barrio] Buscando barrio por id: '{barrioId}'")
        sql = f"""
            SELECT id, nombre
            FROM {db.barrio}
            WHERE id = %s
        """
        try:
            return await _query(sql, [barrioId], fetchone=True)
        except Exception as e:
            logger.error(f"[Barrio] Error en obtenerPorId: {e}")
            raise

    @staticmethod
    async def buscarPorNombre(nombre: str) -> list[dict]:
        logger.info(f"[Barrio] Buscando barrios por nombre: '{nombre}'")
        sql = f"""
            SELECT id, nombre
            FROM {db.barrio}
            WHERE nombre ILIKE %s
            ORDER BY nombre ASC
        """
        try:
            return await _query(sql, [f"%{nombre}%"], fetchall=True)
        except Exception as e:
            logger.error(f"[Barrio] Error en buscarPorNombre: {e}")
            raise

    @staticmethod
    async def listar() -> list[dict]:
        logger.info("[Barrio] Listando todos los barrios.")
        sql = f"""
            SELECT id, nombre
            FROM {db.barrio}
            ORDER BY nombre ASC
        """
        try:
            return await _query(sql, fetchall=True)
        except Exception as e:
            logger.error(f"[Barrio] Error en listar: {e}")
            raise