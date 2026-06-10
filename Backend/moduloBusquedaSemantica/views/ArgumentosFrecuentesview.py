import logging

from asgiref.sync import sync_to_async
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from Backend.moduloBusquedaSemantica.models import Argumento
from app import db

logger = logging.getLogger(__name__)


# ── Helper de query ───────────────────────────────────────────────────────────

def _ejecutar(sql, params=None, fetchall=False, fetchone=False):
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


# ── Vista HTML ────────────────────────────────────────────────────────────────

async def argumentos_frecuentes_vista(request):
    return render(request, 'moduloBusquedaSemantica/argumentos_frecuentes.html')


# ── API: listado de argumentos ────────────────────────────────────────────────

class ArgumentosFrecuentesView(View):
    """
    GET /semantica/argumentos/frecuentes/api/
        ?limite=50          → top global
        ?barrio_id=<uuid>   → top por barrio
    """
    async def get(self, request):
        try:
            limite    = int(request.GET.get('limite', 50))
            barrio_id = request.GET.get('barrio_id', '').strip()

            if barrio_id:
                argumentos = await Argumento.topPorBarrio(barrio_id, limite)
            else:
                argumentos = await Argumento.topGlobal(limite)

            return JsonResponse({'argumentos': argumentos})
        except Exception as e:
            logger.error(f'[ArgumentosFrecuentesView] GET error: {e}')
            return JsonResponse({'error': str(e)}, status=500)


# ── API: incrementar frecuencia ───────────────────────────────────────────────

class ArgumentoIncrementarView(View):
    """
    POST /semantica/argumentos/<pk>/incrementar/
    Incrementa en 1 la frecuencia del argumento indicado.
    """
    async def post(self, request, pk: str):
        try:
            actualizado = await Argumento.incrementarFrecuencia(pk)
            if actualizado is None:
                return JsonResponse({'error': 'Argumento no encontrado.'}, status=404)
            return JsonResponse({'argumento': actualizado})
        except Exception as e:
            logger.error(f'[ArgumentoIncrementarView] POST error: {e}')
            return JsonResponse({'error': str(e)}, status=500)


# ── API: opiniones clasificadas — query directa con JOIN ──────────────────────

class OpinionesClasificadasView(View):
    """
    GET /semantica/opiniones/clasificadas/
        Sin parámetros      → todas (límite 200)
        ?limite=N           → control de límite
        ?barrio_id=<uuid>   → filtro por barrio
        ?tema=<str>         → filtro por tema (ILIKE)
        Ambos combinables entre sí.

    La query hace JOIN directo con barrio y encuesta para traer
    barrio_nombre y opinion_texto en una sola consulta.
    """
    async def get(self, request):
        try:
            limite    = int(request.GET.get('limite', 200))
            barrio_id = request.GET.get('barrio_id', '').strip()
            tema      = request.GET.get('tema', '').strip()

            condiciones = []
            params      = []

            if barrio_id:
                condiciones.append("o.barrio_id = %s")
                params.append(barrio_id)

            if tema:
                condiciones.append("(o.tema ILIKE %s OR e.opinion_politica ILIKE %s)")
                params.extend([f"%{tema}%", f"%{tema}%"])

            where = f"WHERE {' AND '.join(condiciones)}" if condiciones else ""

            params.append(limite)

            sql = f"""
                SELECT
                    o.id,
                    o.tema,
                    o.clasificado_en,
                    b.id                            AS barrio_id,
                    b.nombre                        AS barrio_nombre,
                    LEFT(e.opinion_politica, 200)   AS opinion_texto
                FROM {db.opinion_clasificada} o
                JOIN {db.barrio}   b ON b.id = o.barrio_id
                JOIN {db.encuesta} e ON e.id = o.encuesta_id
                {where}
                ORDER BY o.clasificado_en DESC
                LIMIT %s
            """

            opiniones = await _query(sql, params, fetchall=True)
            return JsonResponse({'opiniones': opiniones or []})

        except Exception as e:
            logger.error(f'[OpinionesClasificadasView] GET error: {e}')
            return JsonResponse({'error': str(e)}, status=500)