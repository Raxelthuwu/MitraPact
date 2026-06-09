import logging
import os
import asyncio
import fitz
from typing import Optional
from django.conf import settings
from app.config.semanticManager import SemanticManager
from Backend.moduloBusquedaSemantica.models import (
    Documento,
    Fragmento,
    TemaDocumento,
)
from Backend.moduloBusquedaSemantica.interfaces import IDocumentoService

logger = logging.getLogger(__name__)
class DocumentoService(IDocumentoService):
    """
    Servicio encargado de gestionar el ciclo de vida completo de un documento PDF.
    Orquesta la extracción de texto, persistencia en PostgreSQL y la indexación
    vectorial en ChromaDB para su posterior consulta semántica.
    """

    DEFAULT_CHUNK_SIZE: int = 500

    # -------------------------------------------------------------------------
    # PÚBLICOS
    # -------------------------------------------------------------------------

    async def cargar(
        self,
        archivo,
        nombre: str,
        temas: Optional[list[str]] = None,
        chunkSize: Optional[int] = None
    ) -> dict:
        logger.info(f"[DocumentoService] Iniciando carga del documento: '{nombre}'")

        tamanoChunk   = chunkSize or self.DEFAULT_CHUNK_SIZE
        nombreArchivo = archivo.name
        rutaArchivo   = os.path.join(settings.DOCUMENTOS_PDF_DIR, nombreArchivo)

        await asyncio.to_thread(self._guardarArchivo, archivo, rutaArchivo)

        documento = await Documento.insertar(nombre, nombreArchivo)
        if not documento:
            raise RuntimeError(f"[DocumentoService] No se pudo persistir el documento '{nombre}' en PG.")

        documentoId = documento['id']
        logger.info(f"[DocumentoService] Documento persistido con id: '{documentoId}'")

        try:
            paginas         = await self._extraerPaginas(rutaArchivo)
            totalFragmentos = await self._persistirFragmentos(documentoId, paginas, tamanoChunk)
            temasFinales    = await self._clasificarTemas(documentoId, paginas, temas)

            logger.info(
                f"[DocumentoService] Carga completada | "
                f"fragmentos: {totalFragmentos} | temas: {len(temasFinales)}"
            )

            return {
                'documento':       documento,
                'totalFragmentos': totalFragmentos,
                'temas':           temasFinales
            }

        except Exception as e:
            logger.error(f"[DocumentoService] Error durante la carga — limpiando datos parciales: {e}")
            await self._limpiarDocumento(documentoId)
            await Documento.eliminar(documentoId)
            raise

    async def actualizar(
            self,
            documentoId: str,
            archivo=None,
            nombre: Optional[str] = None,
            temas: Optional[list[str]] = None,
            chunkSize: Optional[int] = None
        ) -> dict:
            logger.info(f"[DocumentoService] Iniciando actualización del documento id: '{documentoId}'")

            tamanoChunk = chunkSize or self.DEFAULT_CHUNK_SIZE
            documentoActual = await Documento.obtenerPorId(documentoId)
            
            if not documentoActual:
                raise ValueError(f"[DocumentoService] Documento id: '{documentoId}' no encontrado.")

            # 1. Si llega archivo nuevo, procesamos todo de cero (limpiamos)
            if archivo:
                nombreArchivo = archivo.name
                rutaArchivo = os.path.join(settings.DOCUMENTOS_PDF_DIR, nombreArchivo)
                await asyncio.to_thread(self._guardarArchivo, archivo, rutaArchivo)
                
                # Limpiamos solo si estamos cambiando el PDF
                await self._limpiarDocumento(documentoId)
            else:
                # Si NO hay archivo, usamos la ruta existente
                nombreArchivo = documentoActual.get('nombre_archivo')
                rutaArchivo = os.path.join(settings.DOCUMENTOS_PDF_DIR, nombreArchivo)

            # 2. Actualizamos el nombre en DB
            documento = await Documento.actualizar(
                documentoId,
                nombre=nombre,
                nombreArchivo=nombreArchivo
            )

            # 3. MANTENEMOS los temas antiguos si el usuario no envió temas nuevos
            if temas is not None:
                # Si el usuario envió lista de temas (aunque sea vacía), actualizamos
                await TemaDocumento.eliminarPorDocumento(documentoId)
                if len(temas) > 0:
                    await TemaDocumento.insertarBatch(documentoId, temas)
                temasFinales = temas
            else:
                # Si no envió temas, recuperamos los que ya tenía para devolverlos en la respuesta
                temasExistentes = await TemaDocumento.obtenerPorDocumento(documentoId)
                temasFinales = [t['tema'] for t in temasExistentes]

            # 4. Solo re-procesamos texto/fragmentos si subió un archivo nuevo
            if archivo:
                paginas = await self._extraerPaginas(rutaArchivo)
                await self._persistirFragmentos(documentoId, paginas, tamanoChunk)
                # Nota: Si subió archivo nuevo, intentamos clasificar solo si temas estaba vacío
                if not temas: 
                    temasFinales = await self._clasificarTemas(documentoId, paginas, None)

            return {
                'documento': documento,
                'temas': temasFinales
            }

    async def eliminar(self, documentoId: str) -> bool:
        """
        Elimina un documento y todos sus datos asociados.
        Borra fragmentos y temas de PG, y sus vectores correspondientes de ChromaDB.

        Args:
            documentoId: UUID del documento a eliminar.

        Returns:
            True si se eliminó correctamente, False si no se encontró.
        """
        logger.info(f"[DocumentoService] Eliminando documento id: '{documentoId}'")

        documento = await Documento.obtenerPorId(documentoId)
        if not documento:
            logger.warning(f"[DocumentoService] Documento id: '{documentoId}' no encontrado.")
            return False

        await self._limpiarDocumento(documentoId)
        await Documento.eliminar(documentoId)

        logger.info(f"[DocumentoService] Documento id: '{documentoId}' eliminado correctamente.")
        return True

    # -------------------------------------------------------------------------
    # PRIVADOS
    # -------------------------------------------------------------------------

    def _guardarArchivo(self, archivo, ruta: str) -> None:
        """
        Guarda el archivo PDF en disco de forma síncrona.
        Se ejecuta en un hilo secundario via asyncio.to_thread para no
        bloquear el event loop.

        Args:
            archivo: Archivo recibido desde la view.
            ruta:    Ruta absoluta donde se guardará el archivo.
        """
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        with open(ruta, 'wb') as destino:
            for chunk in archivo.chunks():
                destino.write(chunk)
        logger.info(f"[DocumentoService] Archivo guardado en: '{ruta}'")

    async def _extraerPaginas(self, rutaArchivo: str) -> list[str]:
        """
        Extrae el contenido textual del PDF página por página usando fitz (pymupdf).
        La operación de lectura se ejecuta en hilo secundario para no bloquear
        el event loop de Django.

        Args:
            rutaArchivo: Ruta absoluta al archivo PDF en disco.

        Returns:
            list[str] donde cada índice corresponde al texto de una página.
        """
        logger.info(f"[DocumentoService] Extrayendo páginas de: '{rutaArchivo}'")
        return await asyncio.to_thread(self._syncExtraerPaginas, rutaArchivo)

    def _syncExtraerPaginas(self, rutaArchivo: str) -> list[str]:
        """
        Implementación síncrona de la extracción de páginas con fitz.
        Solo debe llamarse via asyncio.to_thread.

        Args:
            rutaArchivo: Ruta absoluta al archivo PDF.

        Returns:
            list[str] con el texto de cada página.
        """
        paginas = []
        with fitz.open(rutaArchivo) as pdf:
            for numeroPagina in range(len(pdf)):
                pagina = pdf[numeroPagina]
                texto  = pagina.get_text().strip()
                if texto:
                    paginas.append(texto)
        return paginas

    async def _fragmentar(self, texto: str, chunkSize: int) -> list[str]:
        """
        Divide un texto en chunks de tamaño configurable respetando
        límites de párrafo para no cortar ideas a la mitad.

        Args:
            texto:     Texto completo a fragmentar.
            chunkSize: Tamaño máximo de cada chunk en caracteres.

        Returns:
            list[str] con los chunks generados.
        """
        parrafos = [p.strip() for p in texto.split('\n\n') if p.strip()]
        chunks   = []
        actual   = ''

        for parrafo in parrafos:
            # Si agregar el párrafo supera el chunk, guardamos el actual y empezamos uno nuevo
            if len(actual) + len(parrafo) + 2 > chunkSize:
                if actual:
                    chunks.append(actual.strip())
                actual = parrafo
            else:
                actual = f"{actual}\n\n{parrafo}" if actual else parrafo

        if actual:
            chunks.append(actual.strip())

        return chunks

    async def _persistirFragmentos(
        self,
        documentoId: str,
        paginas: list[str],
        chunkSize: int          # se mantiene en firma para no romper llamadas existentes
    ) -> int:
        """
        Por cada página extrae párrafos individuales, vectoriza cada uno
        y los persiste en PG + ChromaDB.
        Cada párrafo = 1 fragmento = 1 vector. El campo 'pagina' indica
        de qué página del PDF proviene el párrafo.
        """
        logger.info(
            f"[DocumentoService] Persistiendo fragmentos por párrafo "
            f"para documento_id: '{documentoId}'"
        )

        embedding = SemanticManager.getEmbeddingService()
        chroma    = SemanticManager.getChromaService()
        coleccion = chroma.getOrCreateCollection(
                'fragmentos_vec',
                metadata={"hnsw:space": "cosine"}
)

        fragmentosParaBatch = []
        totalFragmentos     = 0

        for numeroPagina, textoPagina in enumerate(paginas, start=1):
            parrafos = await self._extraerParrafos(textoPagina)

            if not parrafos:
                logger.warning(
                    f"[DocumentoService] Página {numeroPagina} sin párrafos válidos — omitida."
                )
                continue

            for idxParrafo, parrafo in enumerate(parrafos):
                vector   = await embedding.embed(parrafo)
                vectorId = f"{documentoId}_p{numeroPagina}_pr{idxParrafo}"

                await asyncio.to_thread(
                    coleccion.upsert,
                    ids        = [vectorId],
                    embeddings = [vector],
                    documents  = [parrafo],
                    metadatas  = [{
                        'documento_id': str(documentoId),
                        'pagina':       numeroPagina,
                        'parrafo_idx':  idxParrafo,
                    }]
                )

                fragmentosParaBatch.append({
                    'documentoId': documentoId,
                    'pagina':      numeroPagina,
                    'contenido':   parrafo,
                    'vectorId':    vectorId,
                })
                totalFragmentos += 1

        await Fragmento.insertarBatch(fragmentosParaBatch)
        logger.info(
            f"[DocumentoService] {totalFragmentos} párrafos persistidos y vectorizados."
        )
        return totalFragmentos

    async def _clasificarTemas(
        self,
        documentoId: str,
        paginas: list[str],
        temasUsuario: Optional[list[str]] = None
    ) -> list[str]:
        """
        Si el usuario provee temas los usa directamente y los persiste.
        Si no, intenta inferirlos consultando opiniones_vec en ChromaDB.
        En ambos casos persiste via TemaDocumento.insertarBatch.

        Args:
            documentoId:  UUID del documento.
            paginas:      Lista de textos por página.
            temasUsuario: Temas provistos por el usuario. Opcional.

        Returns:
            list[str] con los temas persistidos.
        """
        logger.info(f"[DocumentoService] Clasificando temas para documento_id: '{documentoId}'")

        # Si el usuario proveyó temas los usamos directamente
        if temasUsuario and len(temasUsuario) > 0:
            logger.info(f"[DocumentoService] Usando temas provistos por el usuario: {temasUsuario}")
            await TemaDocumento.insertarBatch(documentoId, temasUsuario)
            return temasUsuario

        # Si no hay temas del usuario intentamos inferirlos desde opiniones_vec
        logger.info(f"[DocumentoService] Infiriendo temas desde opiniones_vec...")

        textoCompleto   = '\n\n'.join(paginas)
        embedding       = SemanticManager.getEmbeddingService()
        chroma          = SemanticManager.getChromaService()
        vectorDocumento = await embedding.embed(textoCompleto[:5000])

        coleccion  = chroma.getOrCreateCollection('opiniones_vec')
        resultados = await asyncio.to_thread(
            coleccion.query,
            query_embeddings = [vectorDocumento],
            n_results        = 5
        )

        temas = []
        if resultados and resultados.get('metadatas'):
            for metadata in resultados['metadatas'][0]:
                tema = metadata.get('tema')
                if tema and tema not in temas and tema != 'sin_clasificar':
                    temas.append(tema)

        if temas:
            await TemaDocumento.insertarBatch(documentoId, temas)
            logger.info(f"[DocumentoService] Temas inferidos y persistidos: {temas}")
        else:
            logger.warning(
                f"[DocumentoService] No se identificaron temas para "
                f"documento_id: '{documentoId}' — sin temas registrados."
            )

        return temas

    async def _limpiarDocumento(self, documentoId: str) -> None:
        """
        Elimina todos los datos asociados a un documento antes de re-indexarlo
        o eliminarlo definitivamente. Borra fragmentos y temas de PG, y elimina
        los vectores correspondientes de ChromaDB.

        Args:
            documentoId: UUID del documento a limpiar.
        """
        logger.info(f"[DocumentoService] Limpiando datos del documento_id: '{documentoId}'")

        chroma    = SemanticManager.getChromaService()
        coleccion = chroma.getOrCreateCollection('fragmentos_vec')

        # Obtener vector_ids antes de eliminar de PG
        fragmentos = await Fragmento.obtenerPorDocumento(documentoId)
        vectorIds = list(set(f['vector_id'] for f in fragmentos if f.get('vector_id')))

        # Eliminar vectores de Chroma
        if vectorIds:
            await asyncio.to_thread(coleccion.delete, ids=vectorIds)
            logger.info(f"[DocumentoService] {len(vectorIds)} vectores eliminados de Chroma.")

        # Eliminar de PG
        await Fragmento.eliminarPorDocumento(documentoId)
        await TemaDocumento.eliminarPorDocumento(documentoId)

        logger.info(f"[DocumentoService] Limpieza completada para documento_id: '{documentoId}'")


    async def _extraerParrafos(self, textoPagina: str) -> list[str]:
        """
        Divide el texto de una página en párrafos limpios.
        Estrategia:
        1. Separar por doble salto de línea (párrafos explícitos).
        2. Separar por punto seguido de mayúscula (oraciones largas sin salto).
        3. Descartar párrafos menores a PARAGRAPH_MIN_LENGTH caracteres.
        """
        import re

        minLen = getattr(settings, 'PARAGRAPH_MIN_LENGTH', 80)

        # Paso 1 — split por doble salto de línea
        bloques = re.split(r'\n{2,}', textoPagina.strip())

        parrafos = []
        for bloque in bloques:
            bloque = bloque.strip()
            if not bloque:
                continue

            # Paso 2 — si el bloque es muy largo, subdividir por punto + mayúscula
            if len(bloque) > 800:
                sub = re.split(r'(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÑ])', bloque)
                for s in sub:
                    s = s.strip()
                    if len(s) >= minLen:
                        parrafos.append(s)
            else:
                if len(bloque) >= minLen:
                    parrafos.append(bloque)

        return parrafos
