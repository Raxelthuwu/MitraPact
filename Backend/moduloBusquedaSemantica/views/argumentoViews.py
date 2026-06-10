# Backend/moduloBusquedaSemantica/views/argumentoViews.py

import json
import logging
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from Backend.moduloBusquedaSemantica.services import ArgumentoService

logger = logging.getLogger(__name__)
_argumento_svc = ArgumentoService()


@method_decorator(csrf_exempt, name='dispatch')
class ArgumentoDetalleView(View):
    """
    GET    /argumentos/<pk>/  — obtiene un argumento por UUID
    PUT    /argumentos/<pk>/  — actualiza texto y/o frecuencia
    DELETE /argumentos/<pk>/  — elimina el argumento
    """

    async def get(self, request, pk):
        try:
            resultado = await _argumento_svc.obtenerPorId(pk)
            if not resultado:
                return JsonResponse({'error': 'Argumento no encontrado.'}, status=404)
            return JsonResponse(resultado, status=200)
        except Exception as e:
            logger.error(f"[ArgumentoDetalleView] Error en get: {e}")
            return JsonResponse({'error': 'Error interno.'}, status=500)

    async def put(self, request, pk):
        try:
            data      = json.loads(request.body or '{}')
            texto     = data.get('texto', '').strip() or None
            frecuencia = data.get('frecuencia')
            documentoIds = data.get('documentoIds')
            if frecuencia is not None:
                frecuencia = int(frecuencia)

            resultado = await _argumento_svc.actualizar(pk, texto=texto, frecuencia=frecuencia, documentoIds=documentoIds,)
            return JsonResponse(resultado, status=200)
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=404)
        except Exception as e:
            logger.error(f"[ArgumentoDetalleView] Error en put: {e}")
            return JsonResponse({'error': 'Error interno al actualizar.'}, status=500)

    async def delete(self, request, pk):
        try:
            eliminado = await _argumento_svc.eliminar(pk)
            if not eliminado:
                return JsonResponse({'error': 'Argumento no encontrado.'}, status=404)
            return JsonResponse({'mensaje': 'Argumento eliminado correctamente.'}, status=200)
        except Exception as e:
            logger.error(f"[ArgumentoDetalleView] Error en delete: {e}")
            return JsonResponse({'error': 'Error interno al eliminar.'}, status=500)
        
@method_decorator(csrf_exempt, name='dispatch')
class ArgumentoCreateView(View):
    """
    POST /argumentos/  — crea un argumento manual y lo vincula a documentos
    """
    async def post(self, request):
        try:
            data           = json.loads(request.body or '{}')
            texto          = data.get('texto', '').strip()
            tema           = data.get('tema', '').strip() or 'sin_clasificar'
            problematicaCod = data.get('problematicaCod')
            frecuencia     = int(data.get('frecuencia', 1))
            documentoIds   = data.get('documentoIds', [])
            
            # --- NUEVO: Extraer opinionId del JSON ---
            opinionId      = data.get('opinionId') 

            if not texto:
                return JsonResponse({'error': 'El campo texto es requerido.'}, status=400)
            if not problematicaCod:
                return JsonResponse({'error': 'El campo problematicaCod es requerido.'}, status=400)

            resultado = await _argumento_svc.crear(
                texto          = texto,
                tema           = tema,
                problematicaCod = int(problematicaCod),
                frecuencia     = frecuencia,
                documentoIds   = documentoIds,
                opinionId      = opinionId, 
            )
            return JsonResponse(resultado, status=201)
        except Exception as e:
            logger.error(f"[ArgumentoCreateView] Error en post: {e}")
            return JsonResponse({'error': 'Error interno al crear el argumento.'}, status=500)