# Backend/moduloBusquedaSemantica/views/documentoViews.py
import logging
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http.multipartparser import MultiPartParser

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
    PUT    /busqueda/documentos/<pk>/  — actualiza por UUID
    DELETE /busqueda/documentos/<pk>/  — elimina por UUID
    """

    async def put(self, request, pk):
        try:
            # -----------------------------------------------------------------
            # SOLUCIÓN ROBUSTA: Parseo manual del flujo Multipart en PUT
            # -----------------------------------------------------------------
            # Extraemos de forma explícita los datos del formulario (put_data) 
            # y los archivos (files) directamente desde el stream de la petición.
            put_data, files = MultiPartParser(
                request.META, 
                request, 
                request.upload_handlers
            ).parse()

            archivo      = files.get('archivo')
            nombre       = put_data.get('nombre', '').strip() or None
            temasRaw     = put_data.get('temas', '')
            temasEnviado = put_data.get('temas_enviado')
            chunkSize    = put_data.get('chunkSize')

            # Procesamiento de la lógica de negocio
            temas     = [t.strip() for t in temasRaw.split(',') if t.strip()] if temasEnviado else None
            chunkSize = int(chunkSize) if chunkSize else None

            # Llamada al servicio con los datos extraídos
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