import logging
from asgiref.sync import sync_to_async
from django.db import connection
from app import db

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Helper interno
# ─────────────────────────────────────────────────────────────────────────────

def _ejecutar(sql, params=None, fetchone=False, fetchall=False, rowcount=False):
    """
    Ejecuta una query síncrona con connection.cursor() y retorna el resultado.
    Siempre se llama via sync_to_async para no bloquear el event loop.
    """
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


# ─────────────────────────────────────────────────────────────────────────────
# Documento
# ─────────────────────────────────────────────────────────────────────────────

class Documento:

    @staticmethod
    async def insertar(nombre: str, nombreArchivo: str) -> dict | None:
        logger.info(f"[Documento] Insertando documento: '{nombre}' | archivo: '{nombreArchivo}'")
        sql = f"""
            INSERT INTO {db.documento} (nombre, nombre_archivo, registrado_en, actualizado_en)
            VALUES (%s, %s, NOW(), NOW())
            RETURNING id, nombre, nombre_archivo, registrado_en, actualizado_en
        """
        try:
            return await _query(sql, [nombre, nombreArchivo], fetchone=True)
        except Exception as e:
            logger.error(f"[Documento] Error al insertar: {e}")
            raise

    @staticmethod
    async def actualizar(documentoId: str, nombre: str = None, nombreArchivo: str = None) -> dict | None:
        logger.info(f"[Documento] Actualizando documento id: '{documentoId}'")
        campos, valores = [], []
        if nombre is not None:
            campos.append("nombre = %s"); valores.append(nombre)
        if nombreArchivo is not None:
            campos.append("nombre_archivo = %s"); valores.append(nombreArchivo)
        if not campos:
            logger.warning("[Documento] No se proporcionaron campos para actualizar.")
            return None
        campos.append("actualizado_en = NOW()")
        valores.append(documentoId)
        sql = f"""
            UPDATE {db.documento}
            SET {', '.join(campos)}
            WHERE id = %s
            RETURNING id, nombre, nombre_archivo, registrado_en, actualizado_en
        """
        try:
            return await _query(sql, valores, fetchone=True)
        except Exception as e:
            logger.error(f"[Documento] Error al actualizar: {e}")
            raise

    @staticmethod
    async def obtenerPorId(documentoId: str) -> dict | None:
        logger.info(f"[Documento] Buscando documento por id: '{documentoId}'")
        sql = f"""
            SELECT id, nombre, nombre_archivo, registrado_en, actualizado_en
            FROM {db.documento} WHERE id = %s
        """
        try:
            return await _query(sql, [documentoId], fetchone=True)
        except Exception as e:
            logger.error(f"[Documento] Error en obtenerPorId: {e}")
            raise

    @staticmethod
    async def buscarPorNombre(nombre: str) -> list[dict]:
        logger.info(f"[Documento] Buscando documentos por nombre: '{nombre}'")
        sql = f"""
            SELECT id, nombre, nombre_archivo, registrado_en, actualizado_en
            FROM {db.documento}
            WHERE nombre ILIKE %s
            ORDER BY registrado_en DESC
        """
        try:
            return await _query(sql, [f"%{nombre}%"], fetchall=True)
        except Exception as e:
            logger.error(f"[Documento] Error en buscarPorNombre: {e}")
            raise

    @staticmethod
    async def buscarPorRangoFecha(fechaInicio: str, fechaFin: str) -> list[dict]:
        logger.info(f"[Documento] Buscando documentos entre {fechaInicio} y {fechaFin}")
        sql = f"""
            SELECT id, nombre, nombre_archivo, registrado_en, actualizado_en
            FROM {db.documento}
            WHERE registrado_en BETWEEN %s AND %s
            ORDER BY registrado_en DESC
        """
        try:
            return await _query(sql, [fechaInicio, fechaFin], fetchall=True)
        except Exception as e:
            logger.error(f"[Documento] Error en buscarPorRangoFecha: {e}")
            raise

    @staticmethod
    async def listarConTemas() -> list[dict]:
        logger.info("[Documento] Listando documentos con temas asociados.")
        sql = f"""
            SELECT
                d.id,
                d.nombre,
                d.nombre_archivo,
                d.registrado_en,
                COALESCE(
                    ARRAY_AGG(DISTINCT td.tema ORDER BY td.tema) FILTER (WHERE td.tema IS NOT NULL),
                    ARRAY[]::text[]
                ) AS temas,
                COUNT(DISTINCT f.id)  AS total_fragmentos,
                COUNT(DISTINCT ad.id) AS total_argumentos
            FROM {db.documento} d
            LEFT JOIN {db.tema_documento} td        ON td.documento_id = d.id
            LEFT JOIN {db.fragmento} f              ON f.documento_id  = d.id
            LEFT JOIN {db.argumento_documento} ad   ON ad.documento_id = d.id
            GROUP BY d.id, d.nombre, d.nombre_archivo, d.registrado_en
            ORDER BY d.registrado_en DESC
        """
        try:
            return await _query(sql, fetchall=True)
        except Exception as e:
            logger.error(f"[Documento] Error en listarConTemas: {e}")
            raise

    @staticmethod
    async def eliminar(documentoId: str) -> bool:
        logger.info(f"[Documento] Eliminando documento id: '{documentoId}'")
        sql = f"DELETE FROM {db.documento} WHERE id = %s"
        try:
            count = await _query(sql, [documentoId], rowcount=True)
            return count > 0
        except Exception as e:
            logger.error(f"[Documento] Error en eliminar: {e}")
            raise


# ─────────────────────────────────────────────────────────────────────────────
# Fragmento
# ─────────────────────────────────────────────────────────────────────────────

class Fragmento:

    @staticmethod
    async def insertar(documentoId: str, pagina: int, contenido: str, vectorId: str) -> dict | None:
        logger.info(f"[Fragmento] Insertando fragmento para documento_id: '{documentoId}' | pág: {pagina}")
        sql = f"""
            INSERT INTO {db.fragmento} (documento_id, pagina, contenido, vector_id)
            VALUES (%s, %s, %s, %s)
            RETURNING id, documento_id, pagina, contenido, vector_id
        """
        try:
            return await _query(sql, [documentoId, pagina, contenido, vectorId], fetchone=True)
        except Exception as e:
            logger.error(f"[Fragmento] Error al insertar: {e}")
            raise

    @staticmethod
    async def buscarPorTextoGlobal(texto: str, limite: int = 20, documento: str = None) -> list[dict]:
        logger.info(f"[Fragmento] Búsqueda global por texto: '{texto}' | documento: '{documento}'")

        where = "WHERE f.contenido ILIKE %s"
        params = [f"%{texto}%"]

        if documento:
            where += " AND d.nombre ILIKE %s"
            params.append(f"%{documento}%")

        params.append(limite)

        sql = f"""
            SELECT
                f.id,
                f.documento_id,
                f.pagina,
                f.contenido,
                f.vector_id,
                d.nombre AS documento_nombre
            FROM {db.fragmento} f
            JOIN {db.documento} d ON d.id = f.documento_id
            {where}
            ORDER BY d.nombre ASC, f.pagina ASC
            LIMIT %s
        """
        try:
            return await _query(sql, params, fetchall=True)
        except Exception as e:
            logger.error(f"[Fragmento] Error en buscarPorTextoGlobal: {e}")
            raise

    @staticmethod
    async def insertarBatch(fragmentos: list[dict]) -> list[dict]:
        logger.info(f"[Fragmento] Insertando lote de {len(fragmentos)} fragmentos.")
        sql = f"""
            INSERT INTO {db.fragmento} (documento_id, pagina, contenido, vector_id)
            VALUES (%s, %s, %s, %s)
            RETURNING id, documento_id, pagina, contenido, vector_id
        """

        def _batch():
            resultados = []
            with connection.cursor() as cursor:
                for f in fragmentos:
                    cursor.execute(sql, [f['documentoId'], f['pagina'], f['contenido'], f['vectorId']])
                    row = cursor.fetchone()
                    if row:
                        cols = [col.name for col in cursor.description]
                        resultados.append(dict(zip(cols, row)))
            return resultados

        try:
            return await sync_to_async(_batch, thread_sensitive=True)()
        except Exception as e:
            logger.error(f"[Fragmento] Error en insertarBatch: {e}")
            raise

    @staticmethod
    async def actualizar(fragmentoId: str, contenido: str = None, vectorId: str = None) -> dict | None:
        logger.info(f"[Fragmento] Actualizando fragmento id: '{fragmentoId}'")
        campos, valores = [], []
        if contenido is not None:
            campos.append("contenido = %s"); valores.append(contenido)
        if vectorId is not None:
            campos.append("vector_id = %s"); valores.append(vectorId)
        if not campos:
            logger.warning("[Fragmento] No se proporcionaron campos para actualizar.")
            return None
        valores.append(fragmentoId)
        sql = f"""
            UPDATE {db.fragmento}
            SET {', '.join(campos)}
            WHERE id = %s
            RETURNING id, documento_id, pagina, contenido, vector_id
        """
        try:
            return await _query(sql, valores, fetchone=True)
        except Exception as e:
            logger.error(f"[Fragmento] Error al actualizar: {e}")
            raise

    @staticmethod
    async def eliminarPorDocumento(documentoId: str) -> int:
        logger.info(f"[Fragmento] Eliminando fragmentos del documento_id: '{documentoId}'")
        sql = f"DELETE FROM {db.fragmento} WHERE documento_id = %s"
        try:
            return await _query(sql, [documentoId], rowcount=True)
        except Exception as e:
            logger.error(f"[Fragmento] Error en eliminarPorDocumento: {e}")
            raise

    @staticmethod
    async def obtenerPorId(fragmentoId: str) -> dict | None:
        logger.info(f"[Fragmento] Buscando fragmento por id: '{fragmentoId}'")
        sql = f"""
            SELECT id, documento_id, pagina, contenido, vector_id
            FROM {db.fragmento} WHERE id = %s
        """
        try:
            return await _query(sql, [fragmentoId], fetchone=True)
        except Exception as e:
            logger.error(f"[Fragmento] Error en obtenerPorId: {e}")
            raise

    @staticmethod
    async def obtenerPorDocumento(documentoId: str) -> list[dict]:
        logger.info(f"[Fragmento] Obteniendo fragmentos del documento_id: '{documentoId}'")
        sql = f"""
            SELECT id, documento_id, pagina, contenido, vector_id
            FROM {db.fragmento}
            WHERE documento_id = %s
            ORDER BY pagina ASC
        """
        try:
            return await _query(sql, [documentoId], fetchall=True)
        except Exception as e:
            logger.error(f"[Fragmento] Error en obtenerPorDocumento: {e}")
            raise

    @staticmethod
    async def obtenerPorVectorId(vectorId: str) -> dict | None:
        logger.info(f"[Fragmento] Buscando fragmento por vector_id: '{vectorId}'")
        sql = f"""
            SELECT id, documento_id, pagina, contenido, vector_id
            FROM {db.fragmento} WHERE vector_id = %s
        """
        try:
            return await _query(sql, [vectorId], fetchone=True)
        except Exception as e:
            logger.error(f"[Fragmento] Error en obtenerPorVectorId: {e}")
            raise

    @staticmethod
    async def obtenerPorVectorIdConNombre(vectorId: str) -> dict | None:
        """
        Como obtenerPorVectorId pero con JOIN a Documento para incluir nombre.
        """
        logger.info(f"[Fragmento] Buscando fragmento+nombre por vector_id: '{vectorId}'")
        sql = f"""
            SELECT
                f.id,
                f.documento_id,
                f.pagina,
                f.contenido,
                f.vector_id,
                d.nombre AS documento_nombre
            FROM {db.fragmento} f
            JOIN {db.documento} d ON d.id = f.documento_id
            WHERE f.vector_id = %s
        """
        try:
            return await _query(sql, [vectorId], fetchone=True)
        except Exception as e:
            logger.error(f"[Fragmento] Error en obtenerPorVectorIdConNombre: {e}")
            raise

    @staticmethod
    async def obtenerParrafosPorVectorId(vectorId: str) -> list[dict]:
        """
        Retorna el fragmento dividido en párrafos individuales,
        cada uno con su índice y contenido limpio.
        """
        import re
        fragmento = await Fragmento.obtenerPorVectorIdConNombre(vectorId)
        if not fragmento:
            return []

        contenido = fragmento.get('contenido', '') or ''
        parrafos_raw = re.split(r'\n{2,}|(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÑ])', contenido.strip())

        parrafos = []
        for i, p in enumerate(parrafos_raw):
            p = p.strip()
            if len(p) < 30:
                continue
            parrafos.append({
                **fragmento,
                'contenido':      p,
                'parrafo_indice': i,
                'contenido_full': contenido,
            })

        return parrafos if parrafos else [fragmento]

    @staticmethod
    async def buscarPorPagina(documentoId: str, pagina: int) -> dict | None:
        logger.info(f"[Fragmento] Buscando fragmento pág {pagina} del documento_id: '{documentoId}'")
        sql = f"""
            SELECT id, documento_id, pagina, contenido, vector_id
            FROM {db.fragmento}
            WHERE documento_id = %s AND pagina = %s
        """
        try:
            return await _query(sql, [documentoId, pagina], fetchone=True)
        except Exception as e:
            logger.error(f"[Fragmento] Error en buscarPorPagina: {e}")
            raise

    @staticmethod
    async def listarPorDocumentoConNombre(documentoId: str) -> list[dict]:
        logger.info(f"[Fragmento] Listando fragmentos con nombre de documento para doc_id: '{documentoId}'")
        sql = f"""
            SELECT
                f.id, f.pagina, f.contenido, f.vector_id,
                d.nombre        AS documento_nombre,
                d.nombre_archivo AS documento_archivo
            FROM {db.fragmento} f
            JOIN {db.documento} d ON d.id = f.documento_id
            WHERE f.documento_id = %s
            ORDER BY f.pagina ASC
        """
        try:
            return await _query(sql, [documentoId], fetchall=True)
        except Exception as e:
            logger.error(f"[Fragmento] Error en listarPorDocumentoConNombre: {e}")
            raise

    @staticmethod
    async def buscarContenidoPorTexto(documentoId: str, texto: str) -> list[dict]:
        logger.info(f"[Fragmento] Buscando texto '{texto}' en documento_id: '{documentoId}'")
        sql = f"""
            SELECT id, documento_id, pagina, contenido, vector_id
            FROM {db.fragmento}
            WHERE documento_id = %s AND contenido ILIKE %s
            ORDER BY pagina ASC
        """
        try:
            return await _query(sql, [documentoId, f"%{texto}%"], fetchall=True)
        except Exception as e:
            logger.error(f"[Fragmento] Error en buscarContenidoPorTexto: {e}")
            raise


# ─────────────────────────────────────────────────────────────────────────────
# TemaDocumento
# ─────────────────────────────────────────────────────────────────────────────

class TemaDocumento:

    @staticmethod
    async def insertar(tema: str, documentoId: str) -> dict | None:
        logger.info(f"[TemaDocumento] Insertando tema: '{tema}' para documento_id: '{documentoId}'")
        sql = f"""
            INSERT INTO {db.tema_documento} (tema, documento_id)
            VALUES (%s, %s)
            RETURNING id, tema, documento_id
        """
        try:
            return await _query(sql, [tema, documentoId], fetchone=True)
        except Exception as e:
            logger.error(f"[TemaDocumento] Error al insertar: {e}")
            raise

    @staticmethod
    async def insertarBatch(documentoId: str, temas: list[str]) -> list[dict]:
        logger.info(f"[TemaDocumento] Insertando {len(temas)} temas para documento_id: '{documentoId}'")
        sql = f"""
            INSERT INTO {db.tema_documento} (tema, documento_id)
            VALUES (%s, %s)
            RETURNING id, tema, documento_id
        """

        def _batch():
            resultados = []
            with connection.cursor() as cursor:
                for tema in temas:
                    cursor.execute(sql, [tema, documentoId])
                    row = cursor.fetchone()
                    if row:
                        cols = [col.name for col in cursor.description]
                        resultados.append(dict(zip(cols, row)))
            return resultados

        try:
            return await sync_to_async(_batch, thread_sensitive=True)()
        except Exception as e:
            logger.error(f"[TemaDocumento] Error en insertarBatch: {e}")
            raise

    @staticmethod
    async def actualizar(temaId: str, tema: str) -> dict | None:
        logger.info(f"[TemaDocumento] Actualizando tema id: '{temaId}' -> '{tema}'")
        sql = f"""
            UPDATE {db.tema_documento}
            SET tema = %s
            WHERE id = %s
            RETURNING id, tema, documento_id
        """
        try:
            return await _query(sql, [tema, temaId], fetchone=True)
        except Exception as e:
            logger.error(f"[TemaDocumento] Error al actualizar: {e}")
            raise

    @staticmethod
    async def eliminarPorDocumento(documentoId: str) -> int:
        logger.info(f"[TemaDocumento] Eliminando temas del documento_id: '{documentoId}'")
        sql = f"DELETE FROM {db.tema_documento} WHERE documento_id = %s"
        try:
            return await _query(sql, [documentoId], rowcount=True)
        except Exception as e:
            logger.error(f"[TemaDocumento] Error en eliminarPorDocumento: {e}")
            raise

    @staticmethod
    async def obtenerPorId(temaId: str) -> dict | None:
        logger.info(f"[TemaDocumento] Buscando tema por id: '{temaId}'")
        sql = f"""
            SELECT id, tema, documento_id
            FROM {db.tema_documento} WHERE id = %s
        """
        try:
            return await _query(sql, [temaId], fetchone=True)
        except Exception as e:
            logger.error(f"[TemaDocumento] Error en obtenerPorId: {e}")
            raise

    @staticmethod
    async def obtenerPorDocumento(documentoId: str) -> list[dict]:
        logger.info(f"[TemaDocumento] Obteniendo temas del documento_id: '{documentoId}'")
        sql = f"""
            SELECT id, tema, documento_id
            FROM {db.tema_documento}
            WHERE documento_id = %s
            ORDER BY tema ASC
        """
        try:
            return await _query(sql, [documentoId], fetchall=True)
        except Exception as e:
            logger.error(f"[TemaDocumento] Error en obtenerPorDocumento: {e}")
            raise

    @staticmethod
    async def buscarDocumentosPorTema(tema: str) -> list[dict]:
        logger.info(f"[TemaDocumento] Buscando documentos por tema: '{tema}'")
        sql = f"""
            SELECT
                td.id           AS tema_id,
                td.tema,
                d.id            AS documento_id,
                d.nombre        AS documento_nombre,
                d.nombre_archivo,
                d.registrado_en
            FROM {db.tema_documento} td
            JOIN {db.documento} d ON d.id = td.documento_id
            WHERE td.tema ILIKE %s
            ORDER BY d.registrado_en DESC
        """
        try:
            return await _query(sql, [f"%{tema}%"], fetchall=True)
        except Exception as e:
            logger.error(f"[TemaDocumento] Error en buscarDocumentosPorTema: {e}")
            raise

    @staticmethod
    async def listarTemasUnicos() -> list[str]:
        logger.info("[TemaDocumento] Listando temas únicos.")
        sql = f"""
            SELECT DISTINCT tema
            FROM {db.tema_documento}
            ORDER BY tema ASC
        """

        def _fetch():
            with connection.cursor() as cursor:
                cursor.execute(sql)
                return [row[0] for row in cursor.fetchall()]

        try:
            return await sync_to_async(_fetch, thread_sensitive=True)()
        except Exception as e:
            logger.error(f"[TemaDocumento] Error en listarTemasUnicos: {e}")
            raise

    @staticmethod
    async def listarDocumentosConTemasPorNombre(nombre: str) -> list[dict]:
        logger.info(f"[TemaDocumento] Buscando documentos por nombre '{nombre}' con temas.")
        sql = f"""
            SELECT
                d.id,
                d.nombre,
                d.nombre_archivo,
                d.registrado_en,
                COALESCE(
                    ARRAY_AGG(td.tema ORDER BY td.tema) FILTER (WHERE td.tema IS NOT NULL),
                    ARRAY[]::text[]
                ) AS temas
            FROM {db.documento} d
            LEFT JOIN {db.tema_documento} td ON td.documento_id = d.id
            WHERE d.nombre ILIKE %s
            GROUP BY d.id, d.nombre, d.nombre_archivo, d.registrado_en
            ORDER BY d.registrado_en DESC
        """
        try:
            return await _query(sql, [f"%{nombre}%"], fetchall=True)
        except Exception as e:
            logger.error(f"[TemaDocumento] Error en listarDocumentosConTemasPorNombre: {e}")
            raise