# Backend/moduloBusquedaSemantica/services/argumentoService.py

import logging
from Backend.moduloBusquedaSemantica.models import Argumento, ArgumentoDocumento

logger = logging.getLogger(__name__)


class ArgumentoService:
    """
    Servicio CRUD de argumentos para gestión manual desde el frontend.
    """


    async def obtenerPorId(self, argumentoId: str) -> dict | None:
        logger.info(f"[ArgumentoService] Obteniendo argumento id: '{argumentoId}'")
        try:
            return await Argumento.obtenerPorId(argumentoId)
        except Exception as e:
            logger.error(f"[ArgumentoService] Error en obtenerPorId: {e}")
            raise

    async def crear(self, texto: str, tema: str, problematicaCod: int, frecuencia: int, documentoIds: list[str], opinionId: str | None = None) -> dict:
        logger.info(f"[ArgumentoService] Creando argumento manual | tema: '{tema}'")
        try:
            argumento = await Argumento.insertar(
                opinionId      = opinionId, # --- NUEVO: Usar la variable en vez de None ---
                texto          = texto,
                tema           = tema,
                problematicaCod = problematicaCod,
                frecuencia     = frecuencia,
            )
            if documentoIds:
                await ArgumentoDocumento.insertarBatch(argumento['id'], documentoIds)
            return argumento
        except Exception as e:
            logger.error(f"[ArgumentoService] Error en crear: {e}")
            raise

    async def actualizar(self, argumentoId: str, texto: str = None, frecuencia: int = None) -> dict | None:
        logger.info(f"[ArgumentoService] Actualizando argumento id: '{argumentoId}'")
        try:
            resultado = await Argumento.actualizar(argumentoId, texto=texto, frecuencia=frecuencia)
            if not resultado:
                raise ValueError(f"Argumento id: '{argumentoId}' no encontrado.")
            return resultado
        except Exception as e:
            logger.error(f"[ArgumentoService] Error en actualizar: {e}")
            raise

    async def eliminar(self, argumentoId: str) -> bool:
        logger.info(f"[ArgumentoService] Eliminando argumento id: '{argumentoId}'")
        try:
            existente = await Argumento.obtenerPorId(argumentoId)
            if not existente:
                return False
            await Argumento.eliminar(argumentoId)
            return True
        except Exception as e:
            logger.error(f"[ArgumentoService] Error en eliminar: {e}")
            raise