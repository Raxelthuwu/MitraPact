import logging
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from Backend.moduloBusquedaSemantica.services import BusquedaService

logger = logging.getLogger(__name__)
_busqueda_svc = BusquedaService()

@method_decorator(csrf_exempt, name='dispatch')
class DocumentoBusquedaView(View):
    """
    GET /busqueda/documentos/
    Busca y lista documentos según los parámetros recibidos.

    Query params:
        ?nombre=                    → busca por nombre aproximado
        ?nombre=&conTemas=true      → busca por nombre con temas agrupados
        ?fechaInicio=&fechaFin=     → busca por rango de fechas (YYYY-MM-DD)
        ?tema=                      → busca por tema aproximado
        sin params                  → lista todos los documentos con temas
    """

    async def get(self, request):
        try:
            nombre      = request.GET.get('nombre', '').strip()
            conTemas    = request.GET.get('conTemas', '').strip().lower()
            fechaInicio = request.GET.get('fechaInicio', '').strip()
            fechaFin    = request.GET.get('fechaFin', '').strip()
            tema        = request.GET.get('tema', '').strip()

            if nombre and conTemas == 'true':
                resultado = await _busqueda_svc.buscarDocumentosPorNombreConTemas(nombre)
                return JsonResponse({'documentos': resultado}, status=200)

            if nombre:
                resultado = await _busqueda_svc.buscarDocumentosPorNombre(nombre)
                return JsonResponse({'documentos': resultado}, status=200)

            if fechaInicio and fechaFin:
                resultado = await _busqueda_svc.buscarDocumentosPorFecha(fechaInicio, fechaFin)
                return JsonResponse({'documentos': resultado}, status=200)

            if tema:
                resultado = await _busqueda_svc.buscarDocumentosPorTema(tema)
                return JsonResponse({'documentos': resultado}, status=200)

            resultado = await _busqueda_svc.listarDocumentosConTemas()
            return JsonResponse({'documentos': resultado}, status=200)

        except Exception as e:
            logger.error(f"[DocumentoBusquedaView] Error en get: {e}")
            return JsonResponse({'error': 'Error interno al buscar documentos.'}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class TemaBusquedaView(View):
    """
    GET /busqueda/temas/
    Lista todos los temas únicos registrados en el sistema.
    """

    async def get(self, request):
        try:
            temas = await _busqueda_svc.listarTemas()
            return JsonResponse({'temas': temas}, status=200)

        except Exception as e:
            logger.error(f"[TemaBusquedaView] Error en get: {e}")
            return JsonResponse({'error': 'Error interno al listar temas.'}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class FragmentoBusquedaView(View):
    """
    GET /busqueda/fragmentos/
    Busca fragmentos de un documento identificado por nombre aproximado.

    Query params:
        ?nombre=            → lista todos los fragmentos del documento
        ?nombre=&pagina=    → retorna el fragmento de una página específica
        ?nombre=&texto=     → busca fragmentos que contengan el texto
    """

    async def get(self, request):
        try:
            nombre = request.GET.get('nombre', '').strip()
            pagina = request.GET.get('pagina', '').strip()
            texto  = request.GET.get('texto', '').strip()

            if not nombre:
                return JsonResponse({'error': 'El parámetro nombre es requerido.'}, status=400)

            if pagina:
                resultado = await _busqueda_svc.obtenerFragmentoPorPagina(nombre, int(pagina))
                return JsonResponse(resultado, status=200)

            if texto:
                resultado = await _busqueda_svc.buscarFragmentosPorTexto(nombre, texto)
                return JsonResponse(resultado, status=200)

            resultado = await _busqueda_svc.obtenerFragmentosPorDocumento(nombre)
            return JsonResponse(resultado, status=200)

        except ValueError:
            return JsonResponse({'error': 'El parámetro pagina debe ser un número entero.'}, status=400)

        except Exception as e:
            logger.error(f"[FragmentoBusquedaView] Error en get: {e}")
            return JsonResponse({'error': 'Error interno al buscar fragmentos.'}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class ArgumentoBusquedaView(View):
    """
    GET /busqueda/argumentos/
    Lista los argumentos vinculados a un documento identificado por nombre aproximado.

    Query params:
        ?nombre=    → nombre parcial o completo del documento
    """

    async def get(self, request):
        try:
            nombre = request.GET.get('nombre', '').strip()

            if not nombre:
                return JsonResponse({'error': 'El parámetro nombre es requerido.'}, status=400)

            resultado = await _busqueda_svc.listarArgumentosDeDocumento(nombre)
            return JsonResponse(resultado, status=200)

        except Exception as e:
            logger.error(f"[ArgumentoBusquedaView] Error en get: {e}")
            return JsonResponse({'error': 'Error interno al listar argumentos.'}, status=500)