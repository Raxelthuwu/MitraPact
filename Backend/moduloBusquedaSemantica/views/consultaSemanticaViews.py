import logging
import json
from datetime import datetime, date
from decimal import Decimal
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from Backend.moduloBusquedaSemantica.services import ConsultaSemanticaService

logger = logging.getLogger(__name__)
_consulta_svc = ConsultaSemanticaService()


def _safe_json_response(data, status=200):
    """JsonResponse que serializa datetime, Decimal y UUID sin explotar."""
    return JsonResponse(data, encoder=DjangoJSONEncoder, safe=False, status=status)


@method_decorator(csrf_exempt, name='dispatch')
class ConsultaSemanticaView(View):
    async def get(self, request):
        try:
            consulta     = request.GET.get('consulta', '').strip()
            problematica = request.GET.get('problematica', '').strip()
            nResultados  = int(request.GET.get('nResultados', '5').strip())

            logger.info(
                f"[ConsultaSemanticaView] GET — consulta='{consulta}' "
                f"problematica='{problematica}' nResultados={nResultados}"
            )

            if not consulta and not problematica:
                return _safe_json_response(
                    {'error': 'Se requiere el parámetro consulta o problematica.'},
                    status=400
                )

            if consulta:
                resultado = await _consulta_svc.buscarPorLenguajeNatural(
                    consulta=consulta, nResultados=nResultados
                )
                return _safe_json_response(resultado)

            # — búsqueda por problemática —
            cod_int = int(problematica)
            logger.info(f"[ConsultaSemanticaView] Llamando buscarArgumentosPorProblematica(cod={cod_int})")

            resultado = await _consulta_svc.buscarArgumentosPorProblematica(
                problematicaCod=cod_int, nResultados=nResultados
            )

            logger.info(
                f"[ConsultaSemanticaView] RESULTADO: {len(resultado)} argumentos "
                f"para problematica={problematica} — primero: {resultado[0] if resultado else 'VACÍO'}"
            )
            return _safe_json_response({'argumentos': resultado})

        except ValueError as e:
            logger.warning(f"[ConsultaSemanticaView] ValueError: {e}", exc_info=True)
            return _safe_json_response(
                {'error': 'nResultados y problematica deben ser enteros.'},
                status=400
            )
        except Exception as e:
            logger.error(f"[ConsultaSemanticaView] EXCEPCIÓN INESPERADA: {e}", exc_info=True)
            return _safe_json_response(
                {'error': 'Error interno al realizar la consulta semántica.'},
                status=500
            )


_consulta_semantica_svc = ConsultaSemanticaService()


@method_decorator(csrf_exempt, name='dispatch')
class ArgumentoDetailView(View):
    async def patch(self, request, pk):
        try:
            data             = json.loads(request.body)
            nuevo_tema       = data.get('tema', '').strip() or None
            problematica_cod = data.get('problematica_cod')

            if not nuevo_tema:
                return _safe_json_response(
                    {'error': 'El campo tema es requerido.'}, status=400
                )

            if problematica_cod not in (None, ''):
                problematica_cod = int(problematica_cod)
            else:
                problematica_cod = None

            resultado = await _consulta_semantica_svc.actualizar_argumento(
                argumento_id=pk,
                tema=nuevo_tema,
                problematica_cod=problematica_cod
            )
            return _safe_json_response(resultado)

        except ValueError as e:
            return _safe_json_response({'error': str(e)}, status=404)
        except Exception as e:
            logger.error(f"[ArgumentoDetailView] Error: {e}", exc_info=True)
            return _safe_json_response(
                {'error': 'Error interno al actualizar el argumento.'}, status=500
            )
        
@method_decorator(csrf_exempt, name='dispatch')
class BusquedaPalabrasView(View):
    async def get(self, request):
        try:
            texto       = request.GET.get('texto', '').strip()
            nResultados = int(request.GET.get('nResultados', '20'))

            if not texto or len(texto) < 2:
                return _safe_json_response(
                    {'error': 'El texto debe tener al menos 2 caracteres.'},
                    status=400
                )

            resultado = await _consulta_svc.buscarPorPalabras(texto, nResultados)
            return _safe_json_response(resultado)

        except Exception as e:
            logger.error(f"[BusquedaPalabrasView] Error: {e}", exc_info=True)
            return _safe_json_response(
                {'error': 'Error interno en la búsqueda.'},
                status=500
            )