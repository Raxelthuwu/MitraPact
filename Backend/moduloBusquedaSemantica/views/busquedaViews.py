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
    GET /semantica/busqueda/documentos/ o /semantica/consulta/
    Adaptado exactamente a los parámetros reales del Frontend ('consulta' y 'nResultados')
    """

    async def get(self, request):
        try:
            # 1. Capturamos los nombres reales que arrojan tus logs de consola
            consulta     = request.GET.get('consulta', '').strip()  # Antes 'query'
            documento    = request.GET.get('documento', '').strip()
            tema         = request.GET.get('tema', '').strip()
            
            # Capturamos el límite de resultados (por defecto 5 si no viene)
            n_resultados = request.GET.get('nResultados', '5').strip()
            limit        = int(n_resultados) if n_resultados.isdigit() else 5

            # 2. Si hay criterios semánticos activos, procesamos de forma vectorial
            if consulta or documento or tema:
                logger.info(f"[DocumentoBusquedaView] Búsqueda Activa -> Consulta: '{consulta}', Doc: '{documento}', Límite: {limit}")
                
                resultado_fragmentos = await _busqueda_svc.buscarSemanticaVectorialAvanzada(
                    query=consulta,          # Le pasamos el texto limpio
                    documento_nombre=documento, 
                    tema=tema,
                    limit=limit              # Pasamos el límite a la base de datos vectorial
                )
                return JsonResponse({'fragmentos': resultado_fragmentos}, status=200)

            # 3. Si no hay parámetros, es la carga inicial de documentos para el selector
            logger.info("[DocumentoBusquedaView] Carga limpia. Listando catálogo de documentos.")
            catálogo_documentos = await _busqueda_svc.listarDocumentosConTemas()
            return JsonResponse({'documentos': catálogo_documentos}, status=200)

        except Exception as e:
            logger.error(f"[DocumentoBusquedaView] Error en buscador adaptado: {e}", exc_info=True)
            return JsonResponse({'error': 'Error interno al procesar los filtros semánticos.'}, status=500)


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