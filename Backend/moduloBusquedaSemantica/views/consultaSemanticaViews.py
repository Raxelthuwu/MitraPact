import logging
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from Backend.moduloBusquedaSemantica.services import ConsultaSemanticaService

logger = logging.getLogger(__name__)
_consulta_svc = ConsultaSemanticaService()

@method_decorator(csrf_exempt, name='dispatch')
class ConsultaSemanticaView(View):
    """
    GET /consulta/
    Consulta semántica sobre documentos y argumentos indexados.

    Query params:
        ?consulta=                      → búsqueda en lenguaje natural sobre fragmentos
        ?consulta=&nResultados=         → top N fragmentos (default 5)
        ?problematica=                  → argumentos más relevantes de una problemática
        ?problematica=&nResultados=     → top N argumentos (default 5)
    """

    async def get(self, request):
        try:
            consulta     = request.GET.get('consulta', '').strip()
            problematica = request.GET.get('problematica', '').strip()
            nResultados  = request.GET.get('nResultados', '5').strip()

            if not consulta and not problematica:
                return JsonResponse(
                    {'error': 'Se requiere el parámetro consulta o problematica.'},
                    status=400
                )

            nResultados = int(nResultados)

            if consulta:
                resultado = await _consulta_svc.buscarPorLenguajeNatural(
                    consulta    = consulta,
                    nResultados = nResultados
                )
                return JsonResponse(resultado, status=200)

            resultado = await _consulta_svc.buscarArgumentosPorProblematica(
                problematicaCod = int(problematica),
                nResultados     = nResultados
            )
            return JsonResponse({'argumentos': resultado}, status=200)

        except ValueError:
            return JsonResponse(
                {'error': 'Los parámetros nResultados y problematica deben ser números enteros.'},
                status=400
            )

        except Exception as e:
            logger.error(f"[ConsultaSemanticaView] Error en get: {e}")
            return JsonResponse({'error': 'Error interno al realizar la consulta semántica.'}, status=500)