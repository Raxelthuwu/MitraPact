import logging
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from Backend.moduloBusquedaSemantica.services import FilterService
from Backend.moduloBusquedaSemantica.models import OpinionClasificada

logger = logging.getLogger(__name__)
_filter_svc = FilterService()

@method_decorator(csrf_exempt, name='dispatch')
class DistribucionFilterView(View):
    """
    GET /filter/distribucion/
    Distribuciones globales de argumentos y opiniones.

    Query params:
        ?tipo=argumentos          → distribucion de argumentos por problematica
        ?tipo=opinionesPorBarrio  → distribucion de opiniones por barrio y tema
        ?tipo=opinionesPorTema    → distribucion global de opiniones por tema
    """

    async def get(self, request):
        try:
            tipo = request.GET.get('tipo', '').strip()

            if tipo == 'argumentos':
                resultado = await _filter_svc.distribucionArgumentosPorProblematica()
                return JsonResponse({'distribucion': resultado}, status=200)

            if tipo == 'opinionesPorBarrio':
                resultado = await _filter_svc.distribucionOpinionesPorBarrio()
                return JsonResponse({'distribucion': resultado}, status=200)

            if tipo == 'opinionesPorTema':
                resultado = await _filter_svc.distribucionOpinionesPorTema()
                return JsonResponse({'distribucion': resultado}, status=200)
            
            # En DistribucionFilterView.get(), antes del return de error final:

            if tipo == 'problematicas':
                resultado = await _filter_svc.listarProblematicas()
                return JsonResponse({'problematicas': resultado}, status=200)
    
            return JsonResponse(
                {'error': 'El parámetro tipo es requerido. Valores válidos: argumentos, opinionesPorBarrio, opinionesPorTema.'},
                status=400
            )

        except Exception as e:
            logger.error(f"[DistribucionFilterView] Error en get: {e}")
            return JsonResponse({'error': 'Error interno al obtener distribución.'}, status=500) 


@method_decorator(csrf_exempt, name='dispatch')
class ProblematicaFilterView(View):
    """
    GET /filter/problematica/
    Consultas analíticas por código de problemática.

    Query params:
        ?cod=                         → argumentos más frecuentes de la problemática
        ?cod=&limite=                 → top N argumentos (default 10)
        ?cod=&documentos=true         → documentos vinculados a la problemática
    """

    async def get(self, request):
        try:
            cod       = request.GET.get('cod', '').strip()
            documentos = request.GET.get('documentos', '').strip().lower()
            limite    = request.GET.get('limite', '10').strip()

            if not cod:
                return JsonResponse({'error': 'El parámetro cod es requerido.'}, status=400)

            problematicaCod = int(cod)
            limite          = int(limite)

            if documentos == 'true':
                resultado = await _filter_svc.documentosPorProblematica(problematicaCod)
                return JsonResponse({'documentos': resultado}, status=200)

            resultado = await _filter_svc.argumentosMasFrecuentesPorProblematica(problematicaCod, limite)
            return JsonResponse({'argumentos': resultado}, status=200)

        except ValueError:
            return JsonResponse({'error': 'Los parámetros cod y limite deben ser números enteros.'}, status=400)

        except Exception as e:
            logger.error(f"[ProblematicaFilterView] Error en get: {e}")
            return JsonResponse({'error': 'Error interno al consultar problemática.'}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class TemaFilterView(View):
    """
    GET /filter/tema/
    Argumentos más frecuentes de un tema.

    Query params:
        ?tema=          → tema parcial o completo a consultar
        ?limite=        → top N argumentos (default 10)
    """

    async def get(self, request):
        try:
            tema   = request.GET.get('tema', '').strip()
            limite = request.GET.get('limite', '10').strip()

            if not tema:
                return JsonResponse({'error': 'El parámetro tema es requerido.'}, status=400)

            limite    = int(limite)
            resultado = await _filter_svc.argumentosMasFrecuentesPorTema(tema, limite)
            return JsonResponse({'argumentos': resultado}, status=200)

        except ValueError:
            return JsonResponse({'error': 'El parámetro limite debe ser un número entero.'}, status=400)

        except Exception as e:
            logger.error(f"[TemaFilterView] Error en get: {e}")
            return JsonResponse({'error': 'Error interno al consultar tema.'}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class OpinionFilterView(View):
    """
    GET /filter/opiniones/
    Consultas de opiniones clasificadas.

    Query params:
        ?fechaInicio=&fechaFin=   → opiniones dentro del rango (YYYY-MM-DD)
        ?buscar=                  → busca por texto de encuesta o tema (mín. 2 chars)
    """

    async def get(self, request):
        try:
            fechaInicio = request.GET.get('fechaInicio', '').strip()
            fechaFin    = request.GET.get('fechaFin', '').strip()
            buscar      = request.GET.get('buscar', '').strip()

            if buscar:
                if len(buscar) < 2:
                    return JsonResponse({'opiniones': []}, status=200)
                resultado = await OpinionClasificada.buscarParaSelector(buscar)
                return JsonResponse({'opiniones': resultado}, status=200)

            if not fechaInicio or not fechaFin:
                return JsonResponse(
                    {'error': 'Indica ?buscar= o los parámetros fechaInicio y fechaFin (YYYY-MM-DD).'},
                    status=400
                )

            resultado = await _filter_svc.opinionesPorRangoFecha(fechaInicio, fechaFin)
            return JsonResponse({'opiniones': resultado}, status=200)

        except Exception as e:
            logger.error(f"[OpinionFilterView] Error en get: {e}")
            return JsonResponse({'error': 'Error interno al consultar opiniones.'}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class BarrioFilterView(View):
    """
    GET /filter/barrio/
    Consultas analíticas por barrio buscado por nombre aproximado.
    Si hay varios barrios coincidentes retorna seleccion_requerida.

    Query params:
        ?barrio=                          → resumen general del barrio
        ?barrio=&tipo=temas               → temas más recurrentes del barrio
        ?barrio=&tipo=argumentos          → argumentos más frecuentes del barrio
        ?barrio=&tipo=argumentos&limite=  → top N argumentos (default 10)
        ?barrio=&tipo=opiniones           → resumen de opiniones del barrio
        ?barrio=&tema=                    → opiniones del barrio filtradas por tema
        ?barrio=&problematica=            → cruce del barrio con una problemática
    """

    async def get(self, request):
        try:
            barrio      = request.GET.get('barrio', '').strip()
            tipo        = request.GET.get('tipo', '').strip()
            tema        = request.GET.get('tema', '').strip()
            problematica = request.GET.get('problematica', '').strip()
            limite      = request.GET.get('limite', '10').strip()

            if not barrio:
                return JsonResponse({'error': 'El parámetro barrio es requerido.'}, status=400)

            limite = int(limite)

            if tema:
                resultado = await _filter_svc.opinionesPorBarrioYTema(barrio, tema)
                return JsonResponse(resultado, status=200)

            if problematica:
                resultado = await _filter_svc.cruzarBarrioProblematica(barrio, int(problematica))
                return JsonResponse({'argumentos': resultado}, status=200)

            if tipo == 'temas':
                resultado = await _filter_svc.temasMasRecurrentesPorBarrio(barrio)
                return JsonResponse(resultado, status=200)

            if tipo == 'argumentos':
                resultado = await _filter_svc.argumentosPorBarrio(barrio, limite)
                return JsonResponse(resultado, status=200)

            if tipo == 'opiniones':
                resultado = await _filter_svc.listarOpinionesPorBarrio(barrio)
                return JsonResponse(resultado, status=200)

            resultado = await _filter_svc.resumenGeneralPorBarrio(barrio)
            return JsonResponse(resultado, status=200)

        except ValueError:
            return JsonResponse({'error': 'Los parámetros limite y problematica deben ser números enteros.'}, status=400)

        except Exception as e:
            logger.error(f"[BarrioFilterView] Error en get: {e}")
            return JsonResponse({'error': 'Error interno al consultar barrio.'}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class AuditoriaFilterView(View):
    """
    GET /filter/auditoria/
    Consultas de auditoría para verificar integridad del índice semántico.

    Query params:
        ?tipo=documentosSinArgumentos   → documentos sin argumentos vinculados
        ?tipo=argumentosSinDocumento    → argumentos sin documento vinculado
        ?tipo=fragmentosPorDocumento    → conteo de fragmentos por documento
        ?limite=                        → top N documentos con más argumentos (default 10)
    """

    async def get(self, request):
        try:
            tipo   = request.GET.get('tipo', '').strip()
            limite = request.GET.get('limite', '').strip()

            if tipo == 'documentosSinArgumentos':
                resultado = await _filter_svc.documentosSinArgumentos()
                return JsonResponse({'documentos': resultado}, status=200)

            if tipo == 'argumentosSinDocumento':
                resultado = await _filter_svc.argumentosSinDocumentoVinculado()
                return JsonResponse({'argumentos': resultado}, status=200)

            if tipo == 'fragmentosPorDocumento':
                resultado = await _filter_svc.fragmentosPorDocumentoConConteo()
                return JsonResponse({'fragmentos': resultado}, status=200)

            if limite:
                resultado = await _filter_svc.documentosConMasArgumentos(int(limite))
                return JsonResponse({'documentos': resultado}, status=200)

            return JsonResponse(
                {'error': 'Indica ?tipo= o ?limite= para usar esta vista.'},
                status=400
            )

        except ValueError:
            return JsonResponse({'error': 'El parámetro limite debe ser un número entero.'}, status=400)

        except Exception as e:
            logger.error(f"[AuditoriaFilterView] Error en get: {e}")
            return JsonResponse({'error': 'Error interno al consultar auditoría.'}, status=500)