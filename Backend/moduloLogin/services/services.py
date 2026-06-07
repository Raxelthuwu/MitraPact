import hashlib
import logging
from typing import Any, Dict, Optional

from asgiref.sync import sync_to_async
from django.contrib.auth.hashers import check_password  # ← agregar

from Backend.moduloLogin.interfaces.interfaces import ILoginService
from Backend.moduloLogin.models import Coordinador

logger = logging.getLogger(__name__)


class LoginService(ILoginService):

    async def autenticar(
        self, email: str, password_plano: str
    ) -> Optional[Dict[str, Any]]:
        logger.debug("[LoginService] autenticar: email=%s", email)

        coordinador = await sync_to_async(Coordinador.get_by_email)(email.lower())

        if coordinador is None:
            logger.warning("[LoginService] autenticar: email no encontrado email=%s", email)
            return None

        # check_password verifica contra PBKDF2/bcrypt generado por make_password
        es_valido = await sync_to_async(check_password)(
            password_plano, coordinador.get("password_hash", "")
        )

        if not es_valido:
            logger.warning("[LoginService] autenticar: contraseña incorrecta email=%s", email)
            return None

        logger.info("[LoginService] autenticar: éxito coordinador_id=%s", coordinador["id"])
        return {
            "id":     str(coordinador["id"]),
            "nombre": coordinador.get("nombre", ""),
            "email":  coordinador.get("email", ""),
        }

    async def obtener_coordinador(
        self, coordinador_id: str
    ) -> Optional[Dict[str, Any]]:
        logger.debug("[LoginService] obtener_coordinador: id=%s", coordinador_id)
        result = await sync_to_async(Coordinador.get_by_id)(coordinador_id)
        if result:
            result["id"] = str(result["id"])
        return result