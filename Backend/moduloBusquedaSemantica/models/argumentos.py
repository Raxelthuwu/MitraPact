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


    # INSERT


    @staticmethod
    async def insertar(opinionId: str | None, texto: str, tema: str, problematicaCod: int, frecuencia: int) -> dict | None:
        logger.info(f"[Argumento] Insertando argumento | opinion_id: '{opinionId}' | tema: '{tema}'")
        sql = f"""
            INSERT INTO {db.argumento} (opinion_id, texto, tema, problematica_cod, frecuencia, identificado_en)
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
        """
        Inserción en lote. Cada dict debe tener:
        opinionId, texto, tema, problematicaCod, frecuencia
        """
        logger.info(f"[Argumento] Insertando lote de {len(argumentos)} argumentos.")
        sql = f"""
            INSERT INTO {db.argumento} (opinion_id, texto, tema, problematica_cod, frecuencia, identificado_en)
            VALUES (%s, %s, %s, %s, %s, NOW())
            RETURNING id, opinion_id, texto, tema, problematica_cod, frecuencia, identificado_en
        """

        def _batch():
            resultados = []
            with connection.cursor() as cursor:
                for a in argumentos:
                    cursor.execute(sql, [
                        a['opinionId'],
                        a['texto'],
                        a['tema'],
                        a['problematicaCod'],
                        a['frecuencia']
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


    # UPDATE


    @staticmethod
    async def actualizar(argumentoId: str, texto: str = None, frecuencia: int = None) -> dict | None:
        logger.info(f"[Argumento] Actualizando argumento id: '{argumentoId}'")

        campos = []
        valores = []

        if texto is not None:
            campos.append("texto = %s")
            valores.append(texto)
        if frecuencia is not None:
            campos.append("frecuencia = %s")
            valores.append(frecuencia)

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


    # GET — lógica interna (por ID)

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
        """Todos los argumentos de una opinión clasificada. Uso interno."""
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
        """Todos los argumentos de una problemática. Uso interno para lógica semántica."""
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
        """
        El usuario filtra argumentos por tema.
        Join con CATALOGO_PROBLEMATICA para mostrar descripción legible.
        """
        logger.info(f"[Argumento] Buscando argumentos por tema: '{tema}'")
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
        """
        El usuario consulta argumentos de una problemática con su descripción legible.
        Join con CATALOGO_PROBLEMATICA.
        """
        logger.info(f"[Argumento] Buscando argumentos por problematica_cod: {problematicaCod} con descripción.")
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
        """
        Top N argumentos más frecuentes de un tema.
        Vista resumen para el usuario coordinador.
        Join con CATALOGO_PROBLEMATICA para descripción legible.
        """
        logger.info(f"[Argumento] Top {limite} argumentos más frecuentes para tema: '{tema}'")
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
    async def incrementarFrecuencia(argumentoId: str) -> dict | None:
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

    @staticmethod
    async def eliminar(argumentoId: str) -> None:
        logger.info(f"[Argumento] Eliminando argumento id: '{argumentoId}'")
        sql = f"DELETE FROM {db.argumento} WHERE id = %s"
        try:
            await _query(sql, [argumentoId])
        except Exception as e:
            logger.error(f"[Argumento] Error al eliminar: {e}")
            raise