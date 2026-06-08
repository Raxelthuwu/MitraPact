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


class ArgumentoDocumento:

    # -------------------------------------------------------------------------
    # INSERT
    # -------------------------------------------------------------------------

    @staticmethod
    async def insertar(argumentoId: str, documentoId: str) -> dict | None:
        logger.info(f"[ArgumentoDocumento] Vinculando argumento_id: '{argumentoId}' con documento_id: '{documentoId}'")
        sql = f"""
            INSERT INTO {db.argumento_documento} (argumento_id, documento_id)
            VALUES (%s, %s)
            RETURNING id, argumento_id, documento_id
        """
        try:
            return await _query(sql, [argumentoId, documentoId], fetchone=True)
        except Exception as e:
            logger.error(f"[ArgumentoDocumento] Error al insertar: {e}")
            raise

    @staticmethod
    async def insertarBatch(argumentoId: str, documentoIds: list[str]) -> list[dict]:
        """Vincula un argumento con múltiples documentos de una sola vez."""
        logger.info(f"[ArgumentoDocumento] Vinculando argumento_id: '{argumentoId}' con {len(documentoIds)} documentos.")
        sql = f"""
            INSERT INTO {db.argumento_documento} (argumento_id, documento_id)
            VALUES (%s, %s)
            ON CONFLICT ON CONSTRAINT uq_argumento_documento DO NOTHING
            RETURNING id, argumento_id, documento_id
        """

        def _batch():
            resultados = []
            with connection.cursor() as cursor:
                for documentoId in documentoIds:
                    cursor.execute(sql, [argumentoId, documentoId])
                    row = cursor.fetchone()
                    if row:
                        cols = [col.name for col in cursor.description]
                        resultados.append(dict(zip(cols, row)))
            return resultados

        try:
            return await sync_to_async(_batch, thread_sensitive=True)()
        except Exception as e:
            logger.error(f"[ArgumentoDocumento] Error en insertarBatch: {e}")
            raise


    # DELETE

    @staticmethod
    async def eliminar(argumentoId: str, documentoId: str) -> bool:
        """Elimina el vínculo entre un argumento y un documento específico."""
        logger.info(f"[ArgumentoDocumento] Eliminando vínculo argumento_id: '{argumentoId}' | documento_id: '{documentoId}'")
        sql = f"""
            DELETE FROM {db.argumento_documento}
            WHERE argumento_id = %s AND documento_id = %s
        """
        try:
            count = await _query(sql, [argumentoId, documentoId], rowcount=True)
            return count > 0
        except Exception as e:
            logger.error(f"[ArgumentoDocumento] Error al eliminar: {e}")
            raise

    @staticmethod
    async def eliminarPorArgumento(argumentoId: str) -> int:
        """Elimina todos los vínculos de un argumento. Retorna cantidad eliminada."""
        logger.info(f"[ArgumentoDocumento] Eliminando todos los vínculos del argumento_id: '{argumentoId}'")
        sql = f"""
            DELETE FROM {db.argumento_documento}
            WHERE argumento_id = %s
        """
        try:
            return await _query(sql, [argumentoId], rowcount=True)
        except Exception as e:
            logger.error(f"[ArgumentoDocumento] Error en eliminarPorArgumento: {e}")
            raise

    # -------------------------------------------------------------------------
    # GET — lógica interna (por ID)
    # -------------------------------------------------------------------------

    @staticmethod
    async def obtenerPorId(argumentoDocumentoId: str) -> dict | None:
        logger.info(f"[ArgumentoDocumento] Buscando vínculo por id: '{argumentoDocumentoId}'")
        sql = f"""
            SELECT id, argumento_id, documento_id
            FROM {db.argumento_documento}
            WHERE id = %s
        """
        try:
            return await _query(sql, [argumentoDocumentoId], fetchone=True)
        except Exception as e:
            logger.error(f"[ArgumentoDocumento] Error en obtenerPorId: {e}")
            raise

    @staticmethod
    async def obtenerDocumentosPorArgumento(argumentoId: str) -> list[dict]:
        """IDs de documentos vinculados a un argumento. Uso interno."""
        logger.info(f"[ArgumentoDocumento] Obteniendo documentos del argumento_id: '{argumentoId}'")
        sql = f"""
            SELECT id, argumento_id, documento_id
            FROM {db.argumento_documento}
            WHERE argumento_id = %s
        """
        try:
            return await _query(sql, [argumentoId], fetchall=True)
        except Exception as e:
            logger.error(f"[ArgumentoDocumento] Error en obtenerDocumentosPorArgumento: {e}")
            raise

    @staticmethod
    async def obtenerArgumentosPorDocumento(documentoId: str) -> list[dict]:
        """IDs de argumentos vinculados a un documento. Uso interno."""
        logger.info(f"[ArgumentoDocumento] Obteniendo argumentos del documento_id: '{documentoId}'")
        sql = f"""
            SELECT id, argumento_id, documento_id
            FROM {db.argumento_documento}
            WHERE documento_id = %s
        """
        try:
            return await _query(sql, [documentoId], fetchall=True)
        except Exception as e:
            logger.error(f"[ArgumentoDocumento] Error en obtenerArgumentosPorDocumento: {e}")
            raise

    # -------------------------------------------------------------------------
    # GET — orientado a usuario
    # -------------------------------------------------------------------------

    @staticmethod
    async def listarDocumentosDeArgumento(argumentoId: str) -> list[dict]:
        """
        El usuario ve qué documentos respaldan un argumento.
        Join con DOCUMENTO para mostrar nombre legible.
        """
        logger.info(f"[ArgumentoDocumento] Listando documentos que respaldan argumento_id: '{argumentoId}'")
        sql = f"""
            SELECT
                ad.id           AS vinculo_id,
                d.id            AS documento_id,
                d.nombre        AS documento_nombre,
                d.nombre_archivo,
                d.registrado_en
            FROM {db.argumento_documento} ad
            JOIN {db.documento} d ON d.id = ad.documento_id
            WHERE ad.argumento_id = %s
            ORDER BY d.registrado_en DESC
        """
        try:
            return await _query(sql, [argumentoId], fetchall=True)
        except Exception as e:
            logger.error(f"[ArgumentoDocumento] Error en listarDocumentosDeArgumento: {e}")
            raise

    @staticmethod
    async def listarArgumentosDeDocumento(documentoId: str) -> list[dict]:
        """
        El usuario ve qué argumentos están respaldados por un documento.
        Join con ARGUMENTO y CATALOGO_PROBLEMATICA para mostrar info legible.
        """
        logger.info(f"[ArgumentoDocumento] Listando argumentos respaldados por documento_id: '{documentoId}'")
        sql = f"""
            SELECT
                ad.id               AS vinculo_id,
                a.id                AS argumento_id,
                a.texto,
                a.tema,
                a.frecuencia,
                cp.descripcion      AS problematica_descripcion
            FROM {db.argumento_documento} ad
            JOIN {db.argumento} a ON a.id = ad.argumento_id
            JOIN {db.catalogo_problematica} cp ON cp.codigo = a.problematica_cod
            WHERE ad.documento_id = %s
            ORDER BY a.frecuencia DESC
        """
        try:
            return await _query(sql, [documentoId], fetchall=True)
        except Exception as e:
            logger.error(f"[ArgumentoDocumento] Error en listarArgumentosDeDocumento: {e}")
            raise