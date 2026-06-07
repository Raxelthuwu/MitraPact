import logging
from typing import Any, Dict, List, Optional
from django.db import connection

import sys
import os

# Esto añade la carpeta raíz (MITRAPACT) al path de Python si no lo está ya
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app import db

logger = logging.getLogger(__name__)


# =============================================================================
# HELPERS
# =============================================================================

def _fetchall(cursor) -> List[Dict[str, Any]]:
    """Convierte filas del cursor en lista de dicts."""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def _fetchone(cursor) -> Optional[Dict[str, Any]]:
    """Convierte una fila del cursor en dict, o None."""
    row = cursor.fetchone()
    if row is None:
        return None
    columns = [col[0] for col in cursor.description]
    return dict(zip(columns, row))


# =============================================================================
# BARRIO
# =============================================================================

class Barrio:

    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        with connection.cursor() as cur:
            cur.execute(f"SELECT id, nombre FROM {db.barrio} ORDER BY nombre")
            return _fetchall(cur)

    @staticmethod
    def get_by_id(barrio_id: str) -> Optional[Dict[str, Any]]:
        with connection.cursor() as cur:
            cur.execute(
                f"SELECT id, nombre FROM {db.barrio} WHERE id = %s",
                [barrio_id],
            )
            return _fetchone(cur)

    @staticmethod
    def create(nombre: str) -> str:
        with connection.cursor() as cur:
            cur.execute(
                f"INSERT INTO {db.barrio} (nombre) VALUES (%s) RETURNING id",
                [nombre],
            )
            return str(cur.fetchone()[0])

    @staticmethod
    def update(barrio_id: str, nombre: str) -> bool:
        with connection.cursor() as cur:
            cur.execute(
                f"UPDATE {db.barrio} SET nombre = %s WHERE id = %s",
                [nombre, barrio_id],
            )
            return cur.rowcount > 0

    @staticmethod
    def delete(barrio_id: str) -> bool:
        with connection.cursor() as cur:
            cur.execute(f"DELETE FROM {db.barrio} WHERE id = %s", [barrio_id])
            return cur.rowcount > 0


# =============================================================================
# SECTOR
# =============================================================================

class Sector:

    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        with connection.cursor() as cur:
            cur.execute(
                f"SELECT id, nombre, barrio_id FROM {db.sector} ORDER BY nombre"
            )
            return _fetchall(cur)

    @staticmethod
    def get_by_barrio(barrio_id: str) -> List[Dict[str, Any]]:
        with connection.cursor() as cur:
            cur.execute(
                f"SELECT id, nombre, barrio_id FROM {db.sector} WHERE barrio_id = %s ORDER BY nombre",
                [barrio_id],
            )
            return _fetchall(cur)

    @staticmethod
    def get_by_id(sector_id: str) -> Optional[Dict[str, Any]]:
        with connection.cursor() as cur:
            cur.execute(
                f"SELECT id, nombre, barrio_id FROM {db.sector} WHERE id = %s",
                [sector_id],
            )
            return _fetchone(cur)

    @staticmethod
    def create(nombre: str, barrio_id: str) -> str:
        with connection.cursor() as cur:
            cur.execute(
                f"INSERT INTO {db.sector} (nombre, barrio_id) VALUES (%s, %s) RETURNING id",
                [nombre, barrio_id],
            )
            return str(cur.fetchone()[0])

    @staticmethod
    def update(sector_id: str, nombre: str, barrio_id: str) -> bool:
        with connection.cursor() as cur:
            cur.execute(
                f"UPDATE {db.sector} SET nombre = %s, barrio_id = %s WHERE id = %s",
                [nombre, barrio_id, sector_id],
            )
            return cur.rowcount > 0

    @staticmethod
    def delete(sector_id: str) -> bool:
        with connection.cursor() as cur:
            cur.execute(f"DELETE FROM {db.sector} WHERE id = %s", [sector_id])
            return cur.rowcount > 0


# =============================================================================
# PUNTO DE INTERÉS
# =============================================================================

class PuntoInteres:

    @staticmethod
    def get_by_sector(sector_id: str) -> List[Dict[str, Any]]:
        with connection.cursor() as cur:
            cur.execute(
                f"SELECT id, nombre, sector_id FROM {db.punto_interes} WHERE sector_id = %s ORDER BY nombre",
                [sector_id],
            )
            return _fetchall(cur)

    @staticmethod
    def get_by_id(punto_id: str) -> Optional[Dict[str, Any]]:
        with connection.cursor() as cur:
            cur.execute(
                f"SELECT id, nombre, sector_id FROM {db.punto_interes} WHERE id = %s",
                [punto_id],
            )
            return _fetchone(cur)

    @staticmethod
    def create(nombre: str, sector_id: str) -> str:
        with connection.cursor() as cur:
            cur.execute(
                f"INSERT INTO {db.punto_interes} (nombre, sector_id) VALUES (%s, %s) RETURNING id",
                [nombre, sector_id],
            )
            return str(cur.fetchone()[0])

    @staticmethod
    def update(punto_id: str, nombre: str, sector_id: str) -> bool:
        with connection.cursor() as cur:
            cur.execute(
                f"UPDATE {db.punto_interes} SET nombre = %s, sector_id = %s WHERE id = %s",
                [nombre, sector_id, punto_id],
            )
            return cur.rowcount > 0

    @staticmethod
    def delete(punto_id: str) -> bool:
        with connection.cursor() as cur:
            cur.execute(f"DELETE FROM {db.punto_interes} WHERE id = %s", [punto_id])
            return cur.rowcount > 0


# =============================================================================
# COORDINADOR
# =============================================================================

class Coordinador:

    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        with connection.cursor() as cur:
            cur.execute(
                f"SELECT id, nombre, email FROM {db.coordinador} ORDER BY nombre"
            )
            return _fetchall(cur)

    @staticmethod
    def get_by_id(coordinador_id: str) -> Optional[Dict[str, Any]]:
        with connection.cursor() as cur:
            cur.execute(
                f"SELECT id, nombre, email FROM {db.coordinador} WHERE id = %s",
                [coordinador_id],
            )
            return _fetchone(cur)

    @staticmethod
    def get_by_email(email: str) -> Optional[Dict[str, Any]]:
        """Incluye password_hash — solo para autenticación."""
        with connection.cursor() as cur:
            cur.execute(
                f"SELECT id, nombre, email, password_hash FROM {db.coordinador} WHERE email = %s",
                [email],
            )
            return _fetchone(cur)

    @staticmethod
    def create(nombre: str, email: str, password_hash: str) -> str:
        with connection.cursor() as cur:
            cur.execute(
                f"""INSERT INTO {db.coordinador} (nombre, email, password_hash)
                    VALUES (%s, %s, %s) RETURNING id""",
                [nombre, email, password_hash],
            )
            return str(cur.fetchone()[0])

    @staticmethod
    def update(coordinador_id: str, nombre: str, email: str) -> bool:
        with connection.cursor() as cur:
            cur.execute(
                f"UPDATE {db.coordinador} SET nombre = %s, email = %s WHERE id = %s",
                [nombre, email, coordinador_id],
            )
            return cur.rowcount > 0

    @staticmethod
    def update_password(coordinador_id: str, password_hash: str) -> bool:
        with connection.cursor() as cur:
            cur.execute(
                f"UPDATE {db.coordinador} SET password_hash = %s WHERE id = %s",
                [password_hash, coordinador_id],
            )
            return cur.rowcount > 0


# =============================================================================
# SIMPATIZANTE
# =============================================================================

class Simpatizante:

    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        with connection.cursor() as cur:
            cur.execute(
                f"""SELECT id, nombre, cedula, telefono, edad, ocupacion,
                           lugar_votacion, puesto_votacion, mesa_votacion,
                           opinion_politica, barrio_id
                    FROM {db.simpatizante} ORDER BY nombre"""
            )
            return _fetchall(cur)

    @staticmethod
    def get_by_id(simpatizante_id: str) -> Optional[Dict[str, Any]]:
        with connection.cursor() as cur:
            cur.execute(
                f"""SELECT id, nombre, cedula, telefono, edad, ocupacion,
                           lugar_votacion, puesto_votacion, mesa_votacion,
                           opinion_politica, barrio_id
                    FROM {db.simpatizante} WHERE id = %s""",
                [simpatizante_id],
            )
            return _fetchone(cur)

    @staticmethod
    def get_by_barrio(barrio_id: str) -> List[Dict[str, Any]]:
        with connection.cursor() as cur:
            cur.execute(
                f"""SELECT id, nombre, cedula, telefono, edad, ocupacion,
                           lugar_votacion, puesto_votacion, mesa_votacion,
                           opinion_politica, barrio_id
                    FROM {db.simpatizante} WHERE barrio_id = %s ORDER BY nombre""",
                [barrio_id],
            )
            return _fetchall(cur)

    @staticmethod
    def create(
        nombre: str,
        cedula: str,
        telefono: Optional[str],
        edad: int,
        ocupacion: str,
        lugar_votacion: str,
        puesto_votacion: str,
        mesa_votacion: str,
        opinion_politica: Optional[str],
        barrio_id: Optional[str],
    ) -> str:
        with connection.cursor() as cur:
            cur.execute(
                f"""INSERT INTO {db.simpatizante}
                    (nombre, cedula, telefono, edad, ocupacion,
                     lugar_votacion, puesto_votacion, mesa_votacion,
                     opinion_politica, barrio_id)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
                [nombre, cedula, telefono, edad, ocupacion,
                 lugar_votacion, puesto_votacion, mesa_votacion,
                 opinion_politica, barrio_id],
            )
            return str(cur.fetchone()[0])

    @staticmethod
    def update(simpatizante_id: str, payload: Dict[str, Any]) -> bool:
        allowed = {
            "nombre", "cedula", "telefono", "edad", "ocupacion",
            "lugar_votacion", "puesto_votacion", "mesa_votacion",
            "opinion_politica", "barrio_id",
        }
        fields = {k: v for k, v in payload.items() if k in allowed}
        if not fields:
            return False
        set_clause = ", ".join(f"{k} = %s" for k in fields)
        values = list(fields.values()) + [simpatizante_id]
        with connection.cursor() as cur:
            cur.execute(
                f"UPDATE {db.simpatizante} SET {set_clause} WHERE id = %s",
                values,
            )
            return cur.rowcount > 0

    @staticmethod
    def delete(simpatizante_id: str) -> bool:
        with connection.cursor() as cur:
            cur.execute(
                f"DELETE FROM {db.simpatizante} WHERE id = %s", [simpatizante_id]
            )
            return cur.rowcount > 0


# =============================================================================
# HORARIO DISPONIBLE
# =============================================================================

class HorarioDisponible:

    @staticmethod
    def get_by_simpatizante(simpatizante_id: str) -> List[Dict[str, Any]]:
        with connection.cursor() as cur:
            cur.execute(
                f"""SELECT id, simpatizante_id, dia_semana, hora_inicio, hora_fin
                    FROM {db.horario_disponible} WHERE simpatizante_id = %s
                    ORDER BY dia_semana, hora_inicio""",
                [simpatizante_id],
            )
            return _fetchall(cur)

    @staticmethod
    def create(
        simpatizante_id: str,
        dia_semana: str,
        hora_inicio: str,
        hora_fin: str,
    ) -> str:
        with connection.cursor() as cur:
            cur.execute(
                f"""INSERT INTO {db.horario_disponible}
                    (simpatizante_id, dia_semana, hora_inicio, hora_fin)
                    VALUES (%s, %s, %s, %s) RETURNING id""",
                [simpatizante_id, dia_semana, hora_inicio, hora_fin],
            )
            return str(cur.fetchone()[0])

    @staticmethod
    def delete(horario_id: str) -> bool:
        with connection.cursor() as cur:
            cur.execute(
                f"DELETE FROM {db.horario_disponible} WHERE id = %s", [horario_id]
            )
            return cur.rowcount > 0

    @staticmethod
    def get_disponibles_para_evento(
        fecha: str,
        dia_semana: str,
        hora_inicio: str,
        hora_fin: str,
    ) -> List[Dict[str, Any]]:
        """
        Devuelve simpatizantes cuyo horario registrado es compatible
        con la fecha/hora del evento (RF-EV-06, RF-EV-22).
        """
        with connection.cursor() as cur:
            cur.execute(
                f"""SELECT s.id, s.nombre, s.cedula, s.ocupacion, s.barrio_id,
                           h.dia_semana, h.hora_inicio, h.hora_fin
                    FROM {db.horario_disponible} h
                    JOIN {db.simpatizante} s ON s.id = h.simpatizante_id
                    WHERE h.dia_semana = %s
                      AND h.hora_inicio <= %s
                      AND h.hora_fin   >= %s
                    ORDER BY s.nombre""",
                [dia_semana, hora_inicio, hora_fin],
            )
            return _fetchall(cur)


# =============================================================================
# EVENTO
# =============================================================================

class Evento:

    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        with connection.cursor() as cur:
            cur.execute(
                f"""SELECT id, nombre, descripcion, fecha, hora_inicio, hora_fin,
                           duracion_min, objetivo, resultado_esperado,
                           resultado_obtenido, capacidad, estado,
                           coordinador_id, barrio_id
                    FROM {db.evento} ORDER BY fecha DESC, hora_inicio"""
            )
            return _fetchall(cur)

    @staticmethod
    def get_by_id(evento_id: str) -> Optional[Dict[str, Any]]:
        with connection.cursor() as cur:
            cur.execute(
                f"""SELECT id, nombre, descripcion, fecha, hora_inicio, hora_fin,
                           duracion_min, objetivo, resultado_esperado,
                           resultado_obtenido, capacidad, estado,
                           coordinador_id, barrio_id
                    FROM {db.evento} WHERE id = %s""",
                [evento_id],
            )
            return _fetchone(cur)

    @staticmethod
    def create(
        nombre: str,
        descripcion: Optional[str],
        fecha: str,
        hora_inicio: str,
        hora_fin: str,
        duracion_min: Optional[int],
        objetivo: Optional[str],
        resultado_esperado: Optional[str],
        resultado_obtenido: Optional[str]=None,
        capacidad: int=0,
        estado: str = "PLANIFICADO",
        coordinador_id: str = None,
        barrio_id: Optional[str] = None,
    ) -> str:
        with connection.cursor() as cur:
            cur.execute(
                f"""INSERT INTO {db.evento}
                    (nombre, descripcion, fecha, hora_inicio, hora_fin,
                     duracion_min, objetivo, resultado_esperado, resultado_obtenido,
                     capacidad, estado, coordinador_id, barrio_id)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
                [nombre, descripcion, fecha, hora_inicio, hora_fin,
                 duracion_min, objetivo, resultado_esperado, resultado_obtenido,
                 capacidad, estado, coordinador_id, barrio_id],
            )
            return str(cur.fetchone()[0])

    @staticmethod
    def update(evento_id: str, payload: Dict[str, Any]) -> bool:
        allowed = {
            "nombre", "descripcion", "fecha", "hora_inicio", "hora_fin",
            "duracion_min", "objetivo", "resultado_esperado",
            "resultado_obtenido", "capacidad", "estado",
            "coordinador_id", "barrio_id",
        }
        fields = {k: v for k, v in payload.items() if k in allowed}
        if not fields:
            return False
        set_clause = ", ".join(f"{k} = %s" for k in fields)
        values = list(fields.values()) + [evento_id]
        with connection.cursor() as cur:
            cur.execute(
                f"UPDATE {db.evento} SET {set_clause} WHERE id = %s",
                values,
            )
            return cur.rowcount > 0

    @staticmethod
    def update_estado(evento_id: str, estado: str) -> bool:
        with connection.cursor() as cur:
            cur.execute(
                f"UPDATE {db.evento} SET estado = %s WHERE id = %s",
                [estado, evento_id],
            )
            return cur.rowcount > 0

    @staticmethod
    def delete(evento_id: str) -> bool:
        with connection.cursor() as cur:
            cur.execute(f"DELETE FROM {db.evento} WHERE id = %s", [evento_id])
            return cur.rowcount > 0


# =============================================================================
# EVENTO TIPO
# =============================================================================

class EventoTipo:

    @staticmethod
    def get_by_evento(evento_id: str) -> List[Dict[str, Any]]:
        with connection.cursor() as cur:
            cur.execute(
                f"SELECT id, evento_id, tipo FROM {db.evento_tipo} WHERE evento_id = %s ORDER BY tipo",
                [evento_id],
            )
            return _fetchall(cur)

    @staticmethod
    def create(evento_id: str, tipo: str) -> str:
        with connection.cursor() as cur:
            cur.execute(
                f"INSERT INTO {db.evento_tipo} (evento_id, tipo) VALUES (%s, %s) RETURNING id",
                [evento_id, tipo],
            )
            return str(cur.fetchone()[0])

    @staticmethod
    def delete(tipo_id: str) -> bool:
        with connection.cursor() as cur:
            cur.execute(f"DELETE FROM {db.evento_tipo} WHERE id = %s", [tipo_id])
            return cur.rowcount > 0

    @staticmethod
    def delete_by_evento(evento_id: str) -> int:
        with connection.cursor() as cur:
            cur.execute(
                f"DELETE FROM {db.evento_tipo} WHERE evento_id = %s", [evento_id]
            )
            return cur.rowcount


# =============================================================================
# ASIGNACIÓN
# =============================================================================

class Asignacion:

    @staticmethod
    def get_by_evento(evento_id: str) -> List[Dict[str, Any]]:
        with connection.cursor() as cur:
            cur.execute(
                f"""SELECT a.id, a.evento_id, a.simpatizante_id, a.rol,
                           a.metodo, a.asistio,
                           s.nombre AS simpatizante_nombre,
                           s.ocupacion AS simpatizante_ocupacion
                    FROM {db.asignacion} a
                    JOIN {db.simpatizante} s ON s.id = a.simpatizante_id
                    WHERE a.evento_id = %s ORDER BY s.nombre""",
                [evento_id],
            )
            return _fetchall(cur)

    @staticmethod
    def get_by_id(asignacion_id: str) -> Optional[Dict[str, Any]]:
        with connection.cursor() as cur:
            cur.execute(
                f"""SELECT id, evento_id, simpatizante_id, rol, metodo, asistio
                    FROM {db.asignacion} WHERE id = %s""",
                [asignacion_id],
            )
            return _fetchone(cur)

    @staticmethod
    def create(
        evento_id: str,
        simpatizante_id: str,
        rol: Optional[str],
        metodo: Optional[str],
    ) -> str:
        with connection.cursor() as cur:
            cur.execute(
                f"""INSERT INTO {db.asignacion}
                    (evento_id, simpatizante_id, rol, metodo)
                    VALUES (%s, %s, %s, %s) RETURNING id""",
                [evento_id, simpatizante_id, rol, metodo],
            )
            return str(cur.fetchone()[0])

    @staticmethod
    def update_rol(asignacion_id: str, rol: str) -> bool:
        with connection.cursor() as cur:
            cur.execute(
                f"UPDATE {db.asignacion} SET rol = %s WHERE id = %s",
                [rol, asignacion_id],
            )
            return cur.rowcount > 0

    @staticmethod
    def registrar_asistencia(asignacion_id: str, asistio: bool) -> bool:
        with connection.cursor() as cur:
            cur.execute(
                f"UPDATE {db.asignacion} SET asistio = %s WHERE id = %s",
                [asistio, asignacion_id],
            )
            return cur.rowcount > 0

    @staticmethod
    def delete(asignacion_id: str) -> bool:
        with connection.cursor() as cur:
            cur.execute(
                f"DELETE FROM {db.asignacion} WHERE id = %s", [asignacion_id]
            )
            return cur.rowcount > 0

    @staticmethod
    def existe(evento_id: str, simpatizante_id: str) -> bool:
        with connection.cursor() as cur:
            cur.execute(
                f"""SELECT 1 FROM {db.asignacion}
                    WHERE evento_id = %s AND simpatizante_id = %s""",
                [evento_id, simpatizante_id],
            )
            return cur.fetchone() is not None

    @staticmethod
    def get_sectores_recientes_simpatizante(simpatizante_id: str, dias: int = 30) -> List[str]:
        """
        Sectores en los que el simpatizante participó en los últimos N días
        — apoya RF-EV-23 (Control de Participación Territorial).
        """
        with connection.cursor() as cur:
            cur.execute(
                f"""SELECT DISTINCT b_sector.id AS sector_id
                    FROM {db.asignacion} a
                    JOIN {db.evento} e ON e.id = a.evento_id
                    JOIN {db.barrio} b ON b.id = e.barrio_id
                    JOIN {db.sector} b_sector ON b_sector.barrio_id = b.id
                    WHERE a.simpatizante_id = %s
                      AND e.fecha >= CURRENT_DATE - (%s || ' days')::INTERVAL""",
                [simpatizante_id, dias],
            )
            return [row[0] for row in cur.fetchall()]


# =============================================================================
# COBERTURA
# =============================================================================

class Cobertura:

    @staticmethod
    def get_by_evento(evento_id: str) -> List[Dict[str, Any]]:
        with connection.cursor() as cur:
            cur.execute(
                f"""SELECT id, evento_id, ocupacion, requeridos, asignados
                    FROM {db.cobertura} WHERE evento_id = %s ORDER BY ocupacion""",
                [evento_id],
            )
            return _fetchall(cur)

    @staticmethod
    def create(evento_id: str, ocupacion: str, requeridos: int) -> str:
        with connection.cursor() as cur:
            cur.execute(
                f"""INSERT INTO {db.cobertura} (evento_id, ocupacion, requeridos)
                    VALUES (%s, %s, %s) RETURNING id""",
                [evento_id, ocupacion, requeridos],
            )
            return str(cur.fetchone()[0])

    @staticmethod
    def update(cobertura_id: str, ocupacion: str, requeridos: int, asignados: int) -> bool:
        with connection.cursor() as cur:
            cur.execute(
                f"""UPDATE {db.cobertura}
                    SET ocupacion = %s, requeridos = %s, asignados = %s
                    WHERE id = %s""",
                [ocupacion, requeridos, asignados, cobertura_id],
            )
            return cur.rowcount > 0

    @staticmethod
    def incrementar_asignados(evento_id: str, ocupacion: str) -> None:
        with connection.cursor() as cur:
            cur.execute(
                f"""UPDATE {db.cobertura}
                    SET asignados = asignados + 1
                    WHERE evento_id = %s AND ocupacion = %s""",
                [evento_id, ocupacion],
            )

    @staticmethod
    def delete(cobertura_id: str) -> bool:
        with connection.cursor() as cur:
            cur.execute(f"DELETE FROM {db.cobertura} WHERE id = %s", [cobertura_id])
            return cur.rowcount > 0


# =============================================================================
# OBSERVACIÓN
# =============================================================================

class Observacion:

    @staticmethod
    def get_by_evento(evento_id: str) -> List[Dict[str, Any]]:
        with connection.cursor() as cur:
            cur.execute(
                f"""SELECT id, evento_id, momento, contenido, registrado_en
                    FROM {db.observacion} WHERE evento_id = %s
                    ORDER BY registrado_en""",
                [evento_id],
            )
            return _fetchall(cur)

    @staticmethod
    def create(evento_id: str, momento: str, contenido: str) -> str:
        with connection.cursor() as cur:
            cur.execute(
                f"""INSERT INTO {db.observacion} (evento_id, momento, contenido)
                    VALUES (%s, %s, %s) RETURNING id""",
                [evento_id, momento, contenido],
            )
            return str(cur.fetchone()[0])

    @staticmethod
    def delete(observacion_id: str) -> bool:
        with connection.cursor() as cur:
            cur.execute(
                f"DELETE FROM {db.observacion} WHERE id = %s", [observacion_id]
            )
            return cur.rowcount > 0


# =============================================================================
# PARTICIPACIÓN EXTERNA
# =============================================================================

class ParticipacionExterna:

    @staticmethod
    def get_by_evento(evento_id: str) -> Optional[Dict[str, Any]]:
        with connection.cursor() as cur:
            cur.execute(
                f"""SELECT id, evento_id, cantidad, notas
                    FROM {db.participacion_externa} WHERE evento_id = %s""",
                [evento_id],
            )
            return _fetchone(cur)

    @staticmethod
    def create(evento_id: str, cantidad: int, notas: Optional[str]) -> str:
        with connection.cursor() as cur:
            cur.execute(
                f"""INSERT INTO {db.participacion_externa} (evento_id, cantidad, notas)
                    VALUES (%s, %s, %s) RETURNING id""",
                [evento_id, cantidad, notas],
            )
            return str(cur.fetchone()[0])

    @staticmethod
    def update(participacion_id: str, cantidad: int, notas: Optional[str]) -> bool:
        with connection.cursor() as cur:
            cur.execute(
                f"""UPDATE {db.participacion_externa}
                    SET cantidad = %s, notas = %s WHERE id = %s""",
                [cantidad, notas, participacion_id],
            )
            return cur.rowcount > 0


# =============================================================================
# MATERIAL PUBLICITARIO
# =============================================================================

class MaterialPublicitario:

    @staticmethod
    def get_by_evento(evento_id: str) -> Optional[Dict[str, Any]]:
        with connection.cursor() as cur:
            cur.execute(
                f"""SELECT id, evento_id, entregado, restante
                    FROM {db.material_publicitario} WHERE evento_id = %s""",
                [evento_id],
            )
            return _fetchone(cur)

    @staticmethod
    def create(evento_id: str, entregado: int, restante: int) -> str:
        with connection.cursor() as cur:
            cur.execute(
                f"""INSERT INTO {db.material_publicitario} (evento_id, entregado, restante)
                    VALUES (%s, %s, %s) RETURNING id""",
                [evento_id, entregado, restante],
            )
            return str(cur.fetchone()[0])

    @staticmethod
    def update(material_id: str, entregado: int, restante: int) -> bool:
        with connection.cursor() as cur:
            cur.execute(
                f"""UPDATE {db.material_publicitario}
                    SET entregado = %s, restante = %s WHERE id = %s""",
                [entregado, restante, material_id],
            )
            return cur.rowcount > 0


# =============================================================================
# ESTADO MATERIAL
# =============================================================================

class EstadoMaterial:

    @staticmethod
    def get_by_evento(evento_id: str) -> List[Dict[str, Any]]:
        with connection.cursor() as cur:
            cur.execute(
                f"""SELECT id, evento_id, estado, notas, registrado_en
                    FROM {db.estado_material} WHERE evento_id = %s
                    ORDER BY registrado_en""",
                [evento_id],
            )
            return _fetchall(cur)

    @staticmethod
    def create(evento_id: str, estado: str, notas: Optional[str]) -> str:
        with connection.cursor() as cur:
            cur.execute(
                f"""INSERT INTO {db.estado_material} (evento_id, estado, notas)
                    VALUES (%s, %s, %s) RETURNING id""",
                [evento_id, estado, notas],
            )
            return str(cur.fetchone()[0])

    @staticmethod
    def promedio_estado_numerico(evento_id: str) -> Optional[float]:
        """
        RF-EV-22 — Promedio numérico del estado del material observado.
        Solo aplica cuando el estado está almacenado como valor numérico (1-5).
        """
        with connection.cursor() as cur:
            cur.execute(
                f"""SELECT AVG(CAST(estado AS NUMERIC))
                    FROM {db.estado_material}
                    WHERE evento_id = %s
                      AND estado ~ '^[1-5]$'""",
                [evento_id],
            )
            row = cur.fetchone()
            return float(row[0]) if row and row[0] is not None else None

    @staticmethod
    def bulk_create_from_csv(rows: List[Dict[str, Any]]) -> int:
        """
        RF-EV-21 — Inserción masiva desde CSV.
        Cada row debe tener: evento_id, estado, notas.
        """
        inserted = 0
        with connection.cursor() as cur:
            for row in rows:
                cur.execute(
                    f"""INSERT INTO {db.estado_material} (evento_id, estado, notas)
                        VALUES (%s, %s, %s)""",
                    [row["evento_id"], row["estado"], row.get("notas")],
                )
                inserted += cur.rowcount
        return inserted


# =============================================================================
# AUDITORÍA
# =============================================================================

class Auditoria:

    @staticmethod
    def get_by_tabla_registro(tabla: str, registro_id: str) -> List[Dict[str, Any]]:
        with connection.cursor() as cur:
            cur.execute(
                f"""SELECT id, coordinador_id, tabla, registro_id, accion, cambios, en
                    FROM {db.auditoria}
                    WHERE tabla = %s AND registro_id = %s
                    ORDER BY en DESC""",
                [tabla, registro_id],
            )
            return _fetchall(cur)

    @staticmethod
    def get_recientes(limit: int = 50) -> List[Dict[str, Any]]:
        with connection.cursor() as cur:
            cur.execute(
                f"""SELECT id, coordinador_id, tabla, registro_id, accion, cambios, en
                    FROM {db.auditoria} ORDER BY en DESC LIMIT %s""",
                [limit],
            )
            return _fetchall(cur)