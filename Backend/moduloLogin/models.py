import logging
from typing import Any, Dict, List, Optional
from django.db import connection

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
from app import db

logger = logging.getLogger(__name__)


def _fetchone(cursor) -> Optional[Dict[str, Any]]:
    row = cursor.fetchone()
    if row is None:
        return None
    columns = [col[0] for col in cursor.description]
    return dict(zip(columns, row))


def _fetchall(cursor) -> List[Dict[str, Any]]:
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


# =============================================================================
# COORDINADOR — modelo de autenticación
# =============================================================================

class Coordinador:

    @staticmethod
    def get_by_email(email: str) -> Optional[Dict[str, Any]]:
        with connection.cursor() as cur:
            cur.execute(
                f"SELECT id, nombre, email, password_hash FROM {db.coordinador} WHERE email = %s",
                [email],
            )
            result = _fetchone(cur)
            logger.warning(f"[Coordinador.get_by_email] query table={db.coordinador} email={email} result={result}")
            return result
    @staticmethod
    def get_by_id(coordinador_id: str) -> Optional[Dict[str, Any]]:
        """Retorna id, nombre, email (sin password_hash)."""
        with connection.cursor() as cur:
            cur.execute(
                f"SELECT id, nombre, email FROM {db.coordinador} WHERE id = %s",
                [coordinador_id],
            )
            return _fetchone(cur)