from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class ILoginService(ABC):

    @abstractmethod
    async def autenticar(
        self, email: str, password_plano: str
    ) -> Optional[Dict[str, Any]]:
        """
        Verifica credenciales. Retorna dict con id, nombre, email
        si son correctas, o None si no coinciden.
        """
        pass

    @abstractmethod
    async def obtener_coordinador(
        self, coordinador_id: str
    ) -> Optional[Dict[str, Any]]:
        """Retorna datos del coordinador por id (sin password_hash)."""
        pass