# Backend/moduloBusquedaSemantica/views/documentoViews.py
import logging
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from Backend.moduloBusquedaSemantica.services import DocumentoService, BusquedaService

logger = logging.getLogger(__name__)

_documento_svc = DocumentoService()
_busqueda_svc  = BusquedaService()


@method_decorator(csrf_exempt, name='dispatch')
class DocumentoView(View):
    """
    POST /documentos/
    Carga un nuevo documento PDF al sistema.
    """

    async def post(self, request):
        try:
            archivo = request.FILES.get('archivo')
            if not archivo:
                return JsonResponse({'error': 'El campo archivo es requerido.'}, status=400)

            nombre    = request.POST.get('nombre', '').strip()
            temasRaw  = request.POST.get('temas', '')
            chunkSize = request.POST.get('chunkSize')

            if not nombre:
                return JsonResponse({'error': 'El campo nombre es requerido.'}, status=400)

            temas     = [t.strip() for t in temasRaw.split(',') if t.strip()] if temasRaw else None
            chunkSize = int(chunkSize) if chunkSize else None

            resultado = await _documento_svc.cargar(
                archivo   = archivo,
                nombre    = nombre,
                temas     = temas,
                chunkSize = chunkSize,
            )

            return JsonResponse(resultado, status=201)

        except Exception as e:
            logger.error(f"[DocumentoView] Error en post: {e}")
            return JsonResponse({'error': 'Error interno al cargar el documento.'}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class DocumentoDetalleView(View):
    """
    PUT    /documentos/<pk>/   — actualiza por UUID
    DELETE /documentos/<pk>/   — elimina por UUID
    """

    async def put(self, request, pk):
        try:
            archivo   = request.FILES.get('archivo')
            nombre    = request.POST.get('nombre', '').strip() or None
            temasRaw  = request.POST.get('temas', '')
            temasEnviado = request.POST.get('temas_enviado')  # ← nuevo
            chunkSize = request.POST.get('chunkSize')

            temas     = [t.strip() for t in temasRaw.split(',') if t.strip()] if temasEnviado else None  # ← cambiado
            chunkSize = int(chunkSize) if chunkSize else None

            resultado = await _documento_svc.actualizar(
                documentoId = pk,
                archivo     = archivo,
                nombre      = nombre,
                temas       = temas,
                chunkSize   = chunkSize,
            )
            return JsonResponse(resultado, status=200)
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=404)
        except Exception as e:
            logger.error(f"[DocumentoDetalleView] Error en put: {e}")
            return JsonResponse({'error': 'Error interno al actualizar el documento.'}, status=500)

    async def delete(self, request, pk):
        try:
            eliminado = await _documento_svc.eliminar(pk)

            if not eliminado:
                return JsonResponse({'error': 'No se encontró el documento.'}, status=404)

            return JsonResponse({'mensaje': 'Documento eliminado correctamente.'}, status=200)

        except Exception as e:
            logger.error(f"[DocumentoDetalleView] Error en delete: {e}")
            return JsonResponse({'error': 'Error interno al eliminar el documento.'}, status=500)