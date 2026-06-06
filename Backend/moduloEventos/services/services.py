import csv
import io
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from asgiref.sync import sync_to_async
from django.db.models import Avg, F
from django.utils import timezone

from Backend.moduloEventos.interfaces import (
    IEventoService,
    IEventoTipoService,
    IDisponibilidadService,
    IAsignacionService,
    ICoberturaService,
    IObservacionService,
    IParticipacionExternaService,
    IMaterialPublicitarioService,
    IEstadoMaterialService,
    ITerritorioService,
)
from Backend.moduloEventos.models import (
    Asignacion,
    Barrio,
    Cobertura,
    EstadoMaterial,
    Evento,
    EventoTipo,
    HorarioDisponible,
    MaterialPublicitario,
    Observacion,
    ParticipacionExterna,
    PuntoInteres,
    Sector,
    Simpatizante,
)

# Diccionario de conversión para mapear el día de la semana de Python al del negocio
DIAS_MAP = {
    0: "Lunes", 1: "Martes", 2: "Miércoles", 3: "Jueves",
    4: "Viernes", 5: "Sábado", 6: "Domingo"
}

# =============================================================================
# EventoService
# =============================================================================
class EventoService(IEventoService):

    def _serializar(self, obj: Evento) -> Dict[str, Any]:
        return {
            "id": str(obj.id),
            "nombre": obj.nombre,
            "descripcion": obj.descripcion,
            "fecha": obj.fecha.isoformat() if obj.fecha else None,
            "hora_inicio": obj.hora_inicio.isoformat() if obj.hora_inicio else None,
            "hora_fin": obj.hora_fin.isoformat() if obj.hora_fin else None,
            "duracion_min": obj.duracion_min,
            "objetivo": obj.objetivo,
            "resultado_esperado": obj.resultado_esperado,
            "resultado_obtenido": obj.resultado_obtenido,
            "capacidad": obj.capacidad,
            "estado": obj.estado,
            "coordinador_id": str(obj.coordinador_id) if obj.coordinador_id else None,
            "barrio_id": str(obj.barrio_id) if obj.barrio_id else None,
            "sector_id": str(obj.sector_id) if obj.sector_id else None,
            "punto_interes_id": str(obj.punto_interes_id) if obj.punto_interes_id else None,
        }

    async def listar(self) -> List[Dict[str, Any]]:
        eventos = await sync_to_async(list)(
            Evento.objects.select_related("coordinador", "barrio", "sector", "punto_interes").order_by("-fecha", "hora_inicio")
        )
        return [self._serializar(e) for e in eventos]

    async def obtener(self, pk: uuid.UUID) -> Optional[Dict[str, Any]]:
        try:
            evento = await sync_to_async(Evento.objects.get)(pk=pk)
            return self._serializar(evento)
        except Evento.DoesNotExist:
            return None

    async def crear(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        def _crear():
            # RF-EV-01: Inserción explícita de la jerarquía territorial completa
            evento = Evento.objects.create(
                nombre=datos["nombre"],
                descripcion=datos.get("descripcion"),
                fecha=datos["fecha"],
                hora_inicio=datos["hora_inicio"],
                hora_fin=datos["hora_fin"],
                duracion_min=datos.get("duracion_min"),
                objetivo=datos.get("objetivo"),
                resultado_esperado=datos.get("resultado_esperado"),
                capacidad=datos.get("capacidad", 0),
                estado=Evento.Estado.PLANIFICADO,
                coordinador_id=datos.get("coordinador_id"),
                barrio_id=datos.get("barrio_id"),
                sector_id=datos.get("sector_id"),
                punto_interes_id=datos.get("punto_interes_id"),
            )
            return self._serializar(evento)
        return await sync_to_async(_crear)()

    async def actualizar(self, pk: uuid.UUID, datos: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        def _actualizar():
            try:
                evento = Evento.objects.get(pk=pk)
                # RF-EV-03: Validación e impedimento estricto de edición ante estados inmutables
                if evento.estado in [Evento.Estado.EN_EJECUCION, Evento.Estado.FINALIZADO]:
                    raise ValueError("No es posible modificar un evento en ejecución o que ya se encuentra finalizado.")
                
                for key, val in datos.items():
                    if hasattr(evento, key):
                        setattr(evento, key, val)
                evento.save()
                return self._serializar(evento)
            except Evento.DoesNotExist:
                return None
        return await sync_to_async(_actualizar)()

    async def cambiar_estado(self, pk: uuid.UUID, estado: str) -> Optional[Dict[str, Any]]:
        def _cambiar():
            try:
                evento = Evento.objects.get(pk=pk)
                if estado in Evento.Estado.values:
                    evento.estado = estado
                    evento.save()
                return self._serializar(evento)
            except Evento.DoesNotExist:
                return None
        return await sync_to_async(_cambiar)()


# =============================================================================
# EventoTipoService
# =============================================================================
class EventoTipoService(IEventoTipoService):
    async def listar_por_evento(self, evento_pk: uuid.UUID) -> List[Dict[str, Any]]:
        tipos = await sync_to_async(list)(EventoTipo.objects.filter(evento_id=evento_pk))
        return [{"id": str(t.id), "tipo": t.tipo} for t in tipos]

    async def agregar(self, evento_pk: uuid.UUID, tipo: str) -> Dict[str, Any]:
        def _agregar():
            t = EventoTipo.objects.create(evento_id=evento_pk, tipo=tipo)
            return {"id": str(t.id), "tipo": t.tipo}
        return await sync_to_async(_agregar)()

    async def eliminar(self, pk: uuid.UUID) -> bool:
        def _eliminar():
            count, _ = EventoTipo.objects.filter(pk=pk).delete()
            return count > 0
        return await sync_to_async(_eliminar)()


# =============================================================================
# DisponibilidadService
# =============================================================================
class DisponibilidadService(IDisponibilidadService):
    async def consultar_disponibles(self, evento_pk: uuid.UUID, ocupacion: Optional[str] = None) -> List[Dict[str, Any]]:
        def _consultar():
            try:
                evento = Evento.objects.get(pk=evento_pk)
            except Evento.DoesNotExist:
                return []

            dia_nombre = DIAS_MAP[evento.fecha.weekday()]
            
            # RF-EV-06 & RF-EV-22: Filtrar simpatizantes con horarios compatibles y opcionalmente por ocupación
            simpatizantes_qs = Simpatizante.objects.filter(
                horarios__dia_semana=dia_nombre,
                horarios__hora_inicio__lte=evento.hora_inicio,
                horarios__hora_fin__gte=evento.hora_fin
            )
            
            if ocupacion:
                simpatizantes_qs = simpatizantes_qs.filter(ocupacion__iexact=ocupacion)

            # Excluir simpatizantes que ya posean cruces de horarios activos en otros eventos el mismo día
            excluir_ids = Asignacion.objects.filter(
                evento__fecha=evento.fecha,
                evento__hora_inicio__lt=evento.hora_fin,
                evento__hora_fin__gt=evento.hora_inicio
            ).values_list("simpatizante_id", flat=True)

            simpatizantes = simpatizantes_qs.exclude(id__in=excluir_ids).distinct()
            
            resultado = []
            for s in simpatizantes:
                # RF-EV-23: Control Territorial - Verificar si trabajó recientemente en el mismo sector
                reciente = Asignacion.objects.filter(
                    simpatizante=s,
                    evento__sector_id=evento.sector_id,
                    asistio=True
                ).exists()

                resultado.append({
                    "id": str(s.id),
                    "nombre": s.nombre,
                    "cedula": s.cedula,
                    "ocupacion": s.ocupacion,
                    "alerta_territorial": reciente  # Informa si ya estuvo activo en la misma zona
                })
            return resultado
        return await sync_to_async(_consultar)()


# =============================================================================
# AsignacionService
# =============================================================================
class AsignacionService(IAsignacionService):
    async def listar_por_evento(self, evento_pk: uuid.UUID) -> List[Dict[str, Any]]:
        asigs = await sync_to_async(list)(
            Asignacion.objects.filter(evento_id=evento_pk).select_related("simpatizante")
        )
        return [{
            "id": str(a.id),
            "simpatizante_id": str(a.simpatizante_id),
            "nombre": a.simpatizante.nombre,
            "ocupacion": a.simpatizante.ocupacion,
            "rol": a.rol,
            "metodo": a.metodo,
            "asistio": a.asistio
        } for a in asigs]

    async def asignar_manual(self, evento_pk: uuid.UUID, simpatizante_id: uuid.UUID, rol: str) -> Dict[str, Any]:
        def _asignar():
            simpatizante = Simpatizante.objects.get(pk=simpatizante_id)
            asig, _ = Asignacion.objects.get_or_create(
                evento_id=evento_pk,
                simpatizante_id=simpatizante_id,
                defaults={"rol": rol, "metodo": Asignacion.Metodo.MANUAL}
            )
            
            # RF-EV-11: Sincronizar automáticamente el contador de cobertura
            cobertura_svc = CoberturaService()
            cobertura_svc._calcular_sincrono(evento_pk, simpatizante.ocupacion)
            
            return {"id": str(asig.id), "rol": asig.rol, "metodo": asig.metodo}
        return await sync_to_async(_asignar)()

    async def asignar_automatica(self, evento_pk: uuid.UUID) -> Dict[str, Any]:
        def _auto():
            disp_svc = DisponibilidadService()
            # Obtenemos los candidatos disponibles que cumplen con las reglas
            candidatos = disp_svc.consultar_disponibles(evento_pk)
            coberturas = Cobertura.objects.filter(evento_id=evento_pk)
            
            asignados_count = 0
            for cob in coberturas:
                faltantes = cob.requeridos - cob.asignados
                if faltantes <= 0:
                    continue
                
                # Filtrar candidatos viables para la ocupación, priorizando los que no tienen alertas territoriales
                viables = [c for c in candidatos if c["ocupacion"].lower() == cob.ocupacion.lower()]
                viables.sort(key=lambda x: x["alerta_territorial"]) # Falses primero
                
                for cand in viables[:faltantes]:
                    Asignacion.objects.get_or_create(
                        evento_id=evento_pk,
                        simpatizante_id=cand["id"],
                        defaults={"rol": Asignacion.Rol.STAFF, "metodo": Asignacion.Metodo.AUTOMATICO}
                    )
                    asignados_count += 1
                
                # Refrescar cobertura del perfil procesado
                cobertura_svc = CoberturaService()
                cobertura_svc._calcular_sincrono(evento_pk, cob.ocupacion)

            return {"status": "Proceso completado", "nuevas_asignaciones": asignados_count}
        return await sync_to_async(_auto)()

    async def actualizar_rol(self, asignacion_pk: uuid.UUID, nuevo_rol: str) -> Optional[Dict[str, Any]]:
        def _rol():
            try:
                asig = Asignacion.objects.get(pk=asignacion_pk)
                asig.rol = nuevo_rol
                asig.save()
                return {"id": str(asig.id), "rol": asig.rol}
            except Asignacion.DoesNotExist:
                return None
        return await sync_to_async(_rol)()

    async def remover_personal(self, asignacion_pk: uuid.UUID) -> bool:
        def _remover():
            try:
                asig = Asignacion.objects.select_related("simpatizante").get(pk=asignacion_pk)
                evento_id = asig.evento_id
                ocupacion = asig.simpatizante.ocupacion
                asig.delete()
                
                # RF-EV-11: Sincronizar dinámicamente al remover personal
                cobertura_svc = CoberturaService()
                cobertura_svc._calcular_sincrono(evento_id, ocupacion)
                return True
            except Asignacion.DoesNotExist:
                return False
        return await sync_to_async(_remover)()

    async def registrar_asistencia(self, asignacion_pk: uuid.UUID, asistio: bool) -> Optional[Dict[str, Any]]:
        def _asistencia():
            try:
                asig = Asignacion.objects.get(pk=asignacion_pk)
                asig.asistio = asistio
                asig.save()
                return {"id": str(asig.id), "asistio": asig.asistio}
            except Asignacion.DoesNotExist:
                return None
        return await sync_to_async(_asistencia)()


# =============================================================================
# CoberturaService
# =============================================================================
class CoberturaService(ICoberturaService):
    async def listar_por_evento(self, evento_pk: uuid.UUID) -> List[Dict[str, Any]]:
        cobs = await sync_to_async(list)(Cobertura.objects.filter(evento_id=evento_pk))
        return [{
            "id": str(c.id),
            "ocupacion": c.ocupacion,
            "requeridos": c.requeridos,
            "asignados": c.asignados
        } for c in cobs]

    def _calcular_sincrono(self, evento_pk: uuid.UUID, ocupacion: str) -> None:
        # RF-EV-11: Automatización integral del cálculo y actualización de asignados reales
        conteo = Asignacion.objects.filter(
            evento_id=evento_pk,
            simpatizante__ocupacion__iexact=ocupacion
        ).count()
        
        Cobertura.objects.filter(
            evento_id=evento_pk,
            ocupacion__iexact=ocupacion
        ).update(asignados=conteo)

    async def sincronizar_conteo(self, evento_pk: uuid.UUID, ocupacion: str) -> None:
        await sync_to_async(self._calcular_sincrono)(evento_pk, ocupacion)


# =============================================================================
# ObservacionService
# =============================================================================
class ObservacionService(IObservacionService):
    async def listar_por_evento(self, evento_pk: uuid.UUID) -> List[Dict[str, Any]]:
        obs = await sync_to_async(list)(Observacion.objects.filter(evento_id=evento_pk).order_by("registrado_en"))
        return [{
            "id": str(o.id),
            "momento": o.momento,
            "contenido": o.contenido,
            "registrado_en": o.registrado_en.isoformat() if o.registrado_en else None
        } for o in obs]

    async def registrar(self, evento_pk: uuid.UUID, momento: str, contenido: str) -> Dict[str, Any]:
        def _registrar():
            obs = Observacion.objects.create(
                evento_id=evento_pk,
                momento=momento,
                contenido=contenido,
                registrado_en=timezone.now() # Sincronización limpia con PostgreSQL sin usar auto_now_add
            )
            return {"id": str(obs.id), "momento": obs.momento, "contenido": obs.contenido}
        return await sync_to_async(_registrar)()


# =============================================================================
# ParticipacionExternaService
# =============================================================================
class ParticipacionExternaService(IParticipacionExternaService):
    async def obtener_por_evento(self, evento_pk: uuid.UUID) -> Optional[Dict[str, Any]]:
        try:
            part = await sync_to_async(ParticipacionExterna.objects.get)(evento_id=evento_pk)
            return {"id": str(part.id), "cantidad": part.cantidad, "notes": part.notes}
        except ParticipacionExterna.DoesNotExist:
            return None

    async def registrar(self, evento_pk: uuid.UUID, cantidad: int, notes: Optional[str]) -> Dict[str, Any]:
        def _reg():
            part, _ = ParticipacionExterna.objects.update_or_create(
                evento_id=evento_pk,
                defaults={"cantidad": cantidad, "notes": notes}
            )
            return {"id": str(part.id), "cantidad": part.cantidad}
        return await sync_to_async(_reg)()


# =============================================================================
# MaterialPublicitarioService
# =============================================================================
class MaterialPublicitarioService(IMaterialPublicitarioService):
    async def obtener_por_evento(self, evento_pk: uuid.UUID) -> Optional[Dict[str, Any]]:
        try:
            mat = await sync_to_async(MaterialPublicitario.objects.get)(evento_id=evento_pk)
            return {"id": str(mat.id), "entregado": mat.entregado, "restante": mat.restante}
        except MaterialPublicitario.DoesNotExist:
            return None

    async def registrar(self, evento_pk: uuid.UUID, entregado: int, restante: int) -> Dict[str, Any]:
        def _reg():
            mat, _ = MaterialPublicitario.objects.update_or_create(
                evento_id=evento_pk,
                defaults={"entregado": entregado, "restante": restante}
            )
            return {"id": str(mat.id), "entregado": mat.entregado, "restante": mat.restante}
        return await sync_to_async(_reg)()


# =============================================================================
# EstadoMaterialService
# =============================================================================
class EstadoMaterialService(IEstadoMaterialService):
    async def listar(self, evento_pk: uuid.UUID) -> List[Dict[str, Any]]:
        est = await sync_to_async(list)(EstadoMaterial.objects.filter(evento_id=evento_pk).order_by("-registrado_en"))
        return [{
            "id": str(e.id),
            "estado": e.estado,
            "notas": e.notas,
            "registrado_en": e.registrado_en.isoformat() if e.registrado_en else None
        } for e in est]

    async def registrar(self, evento_pk: uuid.UUID, estado: str, notas: Optional[str]) -> Dict[str, Any]:
        def _reg():
            obj = EstadoMaterial.objects.create(
                evento_id=evento_pk,
                estado=estado,
                notas=notas,
                registrado_en=timezone.now()
            )
            return {"id": str(obj.id), "estado": obj.estado}
        return await sync_to_async(_reg)()

    async def cargar_csv(self, contenido: str) -> Dict[str, Any]:
        def _procesar():
            lector = csv.reader(io.StringIO(contenido.strip()))
            creados, errores = 0, []
            
            # Mapa numérico solicitado (escala de 1 a 5 mapeado a los strings de negocio)
            escala_map = {
                "5": EstadoMaterial.Estado.CONSERVADO,
                "4": EstadoMaterial.Estado.CONSERVADO,
                "3": EstadoMaterial.Estado.DETERIORADO,
                "2": EstadoMaterial.Estado.RETIRADO,
                "1": EstadoMaterial.Estado.VANDALIZADO,
            }

            for idx, fila in enumerate(lector, start=1):
                if not fila or len(fila) < 2:
                    errores.append(f"Fila {idx}: Estructura inválida.")
                    continue
                
                evento_num, escala_num = fila[0].strip(), fila[1].strip()
                notas = fila[2].strip() if len(fila) > 2 else None

                try:
                    # Encontrar el evento respectivo
                    evento = Evento.objects.filter(nombre__icontains=evento_num).first() or Evento.objects.filter(pk=uuid.UUID(evento_num)).first()
                    if not evento:
                        errores.append(f"Fila {idx}: Evento '{evento_num}' no encontrado.")
                        continue
                    
                    estado_str = escala_map.get(escala_num)
                    if not estado_str:
                        errores.append(f"Fila {idx}: Escala numérica '{escala_num}' fuera de rango (1-5).")
                        continue

                    EstadoMaterial.objects.create(
                        evento=evento,
                        estado=estado_str,
                        notas=notas,
                        registrado_en=timezone.now()
                    )
                    creados += 1
                except Exception as ex:
                    errores.append(f"Fila {idx}: Error inesperado ({str(ex)}).")
            
            return {"registrados": creados, "errores": errores}
        return await sync_to_async(_procesar)()

    async def promedio_estado(self, evento_pk: uuid.UUID) -> Dict[str, Any]:
        def _promedio():
            # Mapeamos los estados a un peso matemático para extraer el KPI real de conservación
            qs = EstadoMaterial.objects.filter(evento_id=evento_pk)
            total = qs.count()
            if total == 0:
                return {"promedio": 0.0, "total_muestras": 0}
            
            pesos = {
                EstadoMaterial.Estado.CONSERVADO: 5.0,
                EstadoMaterial.Estado.DETERIORADO: 3.0,
                EstadoMaterial.Estado.RETIRADO: 2.0,
                EstadoMaterial.Estado.VANDALIZADO: 1.0,
            }
            
            suma = sum(pesos.get(e.estado, 0.0) for e in qs)
            return {"promedio": round(suma / total, 2), "total_muestras": total}
        return await sync_to_async(_promedio)()


# =============================================================================
# TerritorioService
# =============================================================================
class TerritorioService(ITerritorioService):
    async def listar_barrios(self) -> List[Dict[str, Any]]:
        barrios = await sync_to_async(list)(Barrio.objects.order_by("nombre"))
        return [{"id": str(b.id), "nombre": b.nombre} for b in barrios]

    async def listar_sectores(self, barrio_pk: Optional[uuid.UUID] = None) -> List[Dict[str, Any]]:
        qs = Sector.objects.select_related("barrio").order_by("nombre")
        if barrio_pk:
            qs = qs.filter(barrio_id=barrio_pk)
        sectores = await sync_to_async(list)(qs)
        return [{"id": str(s.id), "nombre": s.nombre, "barrio_id": str(s.barrio_id)} for s in sectores]

    async def listar_puntos_interes(self, sector_pk: Optional[uuid.UUID] = None) -> List[Dict[str, Any]]:
        qs = PuntoInteres.objects.select_related("sector").order_by("nombre")
        if sector_pk:
            qs = qs.filter(sector_id=sector_pk)
        puntos = await sync_to_async(list)(qs)
        return [{"id": str(p.id), "nombre": p.nombre, "sector_id": str(p.sector_id)} for p in puntos]