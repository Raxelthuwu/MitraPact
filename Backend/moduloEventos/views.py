import uuid

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from Backend.moduloEventos.services import (
    AsignacionService,
    CoberturaService,
    DisponibilidadService,
    EstadoMaterialService,
    EventoService,
    EventoTipoService,
    MaterialPublicitarioService,
    ObservacionService,
    ParticipacionExternaService,
    TerritorioService,
)

# Service singletons
eventoSvc           = EventoService()
eventoTipoSvc       = EventoTipoService()
asignacionSvc       = AsignacionService()
disponibilidadSvc   = DisponibilidadService()
coberturaSvc        = CoberturaService()
observacionSvc      = ObservacionService()
participacionSvc    = ParticipacionExternaService()
materialSvc         = MaterialPublicitarioService()
estadoMaterialSvc   = EstadoMaterialService()
territorioSvc       = TerritorioService()


# =============================================================================
# EVENTOS
# =============================================================================

async def evento_lista(request: HttpRequest) -> HttpResponse:
    eventos = await eventoSvc.listar()
    return render(request, "eventos/evento_lista.html", {"eventos": eventos})


async def evento_crear(request: HttpRequest) -> HttpResponse:
    barrios = await territorioSvc.listar_barrios()

    if request.method == "POST":
        datos = {
            "nombre":             request.POST.get("nombre", "").strip(),
            "descripcion":        request.POST.get("descripcion", "").strip() or None,
            "fecha":              request.POST.get("fecha"),
            "hora_inicio":        request.POST.get("hora_inicio"),
            "hora_fin":           request.POST.get("hora_fin"),
            "duracion_min":       request.POST.get("duracion_min") or None,
            "objetivo":           request.POST.get("objetivo", "").strip() or None,
            "resultado_esperado": request.POST.get("resultado_esperado", "").strip() or None,
            "capacidad":          int(request.POST.get("capacidad", 0)),
            "estado":             request.POST.get("estado", "PLANIFICADO"),
            "coordinador_id":     request.POST.get("coordinador_id") or None,
            "barrio_id":          request.POST.get("barrio_id") or None,
        }

        if not datos["nombre"] or not datos["fecha"]:
            messages.error(request, "El nombre y la fecha son obligatorios.")
            return render(request, "eventos/evento_form.html", {"barrios": barrios, "datos": datos})

        evento = await eventoSvc.crear(datos)
        messages.success(request, "Evento creado exitosamente.")
        return redirect("eventos:evento_detalle", pk=evento["id"])

    return render(request, "eventos/evento_form.html", {"barrios": barrios})


async def evento_detalle(request: HttpRequest, pk: uuid.UUID) -> HttpResponse:
    evento = await eventoSvc.obtener(pk)
    if not evento:
        messages.error(request, "Evento no encontrado.")
        return redirect("eventos:evento_lista")

    tipos          = await eventoTipoSvc.listar_por_evento(pk)
    asignaciones   = await asignacionSvc.listar(pk)
    coberturas     = await coberturaSvc.listar(pk)
    observaciones  = await observacionSvc.listar(pk)
    participacion  = await participacionSvc.obtener(pk)
    material       = await materialSvc.obtener(pk)
    estados_mat    = await estadoMaterialSvc.listar(pk)
    promedio_mat   = await estadoMaterialSvc.promedio_estado(pk)

    return render(request, "eventos/evento_detalle.html", {
        "evento":        evento,
        "tipos":         tipos,
        "asignaciones":  asignaciones,
        "coberturas":    coberturas,
        "observaciones": observaciones,
        "participacion": participacion,
        "material":      material,
        "estados_mat":   estados_mat,
        "promedio_mat":  promedio_mat,
    })


async def evento_editar(request: HttpRequest, pk: uuid.UUID) -> HttpResponse:
    evento  = await eventoSvc.obtener(pk)
    barrios = await territorioSvc.listar_barrios()

    if not evento:
        messages.error(request, "Evento no encontrado.")
        return redirect("eventos:evento_lista")

    if request.method == "POST":
        datos = {
            "nombre":             request.POST.get("nombre", "").strip(),
            "descripcion":        request.POST.get("descripcion", "").strip() or None,
            "fecha":              request.POST.get("fecha"),
            "hora_inicio":        request.POST.get("hora_inicio"),
            "hora_fin":           request.POST.get("hora_fin"),
            "duracion_min":       request.POST.get("duracion_min") or None,
            "objetivo":           request.POST.get("objetivo", "").strip() or None,
            "resultado_esperado": request.POST.get("resultado_esperado", "").strip() or None,
            "resultado_obtenido": request.POST.get("resultado_obtenido", "").strip() or None,
            "capacidad":          int(request.POST.get("capacidad", 0)),
            "estado":             request.POST.get("estado", evento["estado"]),
            "barrio_id":          request.POST.get("barrio_id") or None,
        }

        actualizado = await eventoSvc.actualizar(pk, datos)
        if actualizado:
            messages.success(request, "Evento actualizado.")
        return redirect("eventos:evento_detalle", pk=pk)

    return render(request, "eventos/evento_form.html", {
        "evento":  evento,
        "barrios": barrios,
        "editar":  True,
    })


# =============================================================================
# TIPOS DE EVENTO
# =============================================================================

async def evento_tipo_agregar(request: HttpRequest, evento_pk: uuid.UUID) -> HttpResponse:
    if request.method == "POST":
        tipo = request.POST.get("tipo", "").strip()
        if tipo:
            await eventoTipoSvc.agregar(evento_pk, tipo)
            messages.success(request, "Tipo agregado.")
        else:
            messages.error(request, "Debe seleccionar un tipo.")
    return redirect("eventos:evento_detalle", pk=evento_pk)


async def evento_tipo_eliminar(request: HttpRequest, pk: uuid.UUID) -> HttpResponse:
    evento_pk = request.POST.get("evento_pk")
    if request.method == "POST":
        await eventoTipoSvc.eliminar(pk)
        messages.success(request, "Tipo eliminado.")
    return redirect("eventos:evento_detalle", pk=evento_pk)


# =============================================================================
# DISPONIBILIDAD
# =============================================================================

async def consultar_disponibilidad(request: HttpRequest, evento_pk: uuid.UUID) -> HttpResponse:
    evento      = await eventoSvc.obtener(evento_pk)
    disponibles = await disponibilidadSvc.simpatizantes_disponibles(evento_pk)

    return render(request, "eventos/disponibilidad.html", {
        "evento":      evento,
        "disponibles": disponibles,
    })


# =============================================================================
# ASIGNACIÓN DE PERSONAL
# =============================================================================

async def asignacion_lista(request: HttpRequest, evento_pk: uuid.UUID) -> HttpResponse:
    evento       = await eventoSvc.obtener(evento_pk)
    asignaciones = await asignacionSvc.listar(evento_pk)
    return render(request, "eventos/asignacion_lista.html", {
        "evento":       evento,
        "asignaciones": asignaciones,
    })


async def asignacion_manual(request: HttpRequest, evento_pk: uuid.UUID) -> HttpResponse:
    evento      = await eventoSvc.obtener(evento_pk)
    disponibles = await disponibilidadSvc.simpatizantes_disponibles(evento_pk)

    if request.method == "POST":
        simpatizante_id = request.POST.get("simpatizante_id", "").strip()
        rol             = request.POST.get("rol", "").strip()

        if not simpatizante_id or not rol:
            messages.error(request, "Debe seleccionar un simpatizante y un rol.")
            return render(request, "eventos/asignacion_manual.html", {
                "evento": evento, "disponibles": disponibles,
            })

        # Advertencia territorial (RF-EV-23)
        tiene_participacion = await disponibilidadSvc.advertencia_territorial(
            uuid.UUID(simpatizante_id), evento_pk
        )
        if tiene_participacion:
            messages.warning(
                request,
                "Advertencia: esta persona participó recientemente en actividades del mismo sector."
            )

        await asignacionSvc.asignar_manual(evento_pk, uuid.UUID(simpatizante_id), rol)
        messages.success(request, "Personal asignado exitosamente.")
        return redirect("eventos:asignacion_lista", evento_pk=evento_pk)

    return render(request, "eventos/asignacion_manual.html", {
        "evento":      evento,
        "disponibles": disponibles,
    })


async def asignacion_automatica(request: HttpRequest, evento_pk: uuid.UUID) -> HttpResponse:
    evento = await eventoSvc.obtener(evento_pk)

    if request.method == "POST":
        usar_disponibilidad     = request.POST.get("usar_disponibilidad") == "on"
        ocupacion               = request.POST.get("ocupacion", "").strip() or None
        excluir_sector_reciente = request.POST.get("excluir_sector_reciente") == "on"

        asignados = await asignacionSvc.asignar_automatico(
            evento_pk,
            usar_disponibilidad=usar_disponibilidad,
            usar_ocupacion=ocupacion,
            excluir_sector_reciente=excluir_sector_reciente,
        )

        messages.success(request, f"Asignación automática completada: {len(asignados)} personas asignadas.")
        return redirect("eventos:asignacion_lista", evento_pk=evento_pk)

    return render(request, "eventos/asignacion_automatica.html", {"evento": evento})


async def asignacion_editar(request: HttpRequest, pk: uuid.UUID) -> HttpResponse:
    if request.method == "POST":
        evento_pk = request.POST.get("evento_pk")
        datos = {
            "rol":     request.POST.get("rol", "").strip() or None,
            "asistio": request.POST.get("asistio") == "on",
        }
        await asignacionSvc.actualizar(pk, datos)
        messages.success(request, "Asignación actualizada.")
        return redirect("eventos:asignacion_lista", evento_pk=evento_pk)

    return redirect("eventos:evento_lista")


async def asignacion_eliminar(request: HttpRequest, pk: uuid.UUID) -> HttpResponse:
    if request.method == "POST":
        evento_pk = request.POST.get("evento_pk")
        await asignacionSvc.eliminar(pk)
        messages.success(request, "Asignación eliminada.")
        return redirect("eventos:asignacion_lista", evento_pk=evento_pk)
    return redirect("eventos:evento_lista")


# =============================================================================
# COBERTURA
# =============================================================================

async def cobertura_lista(request: HttpRequest, evento_pk: uuid.UUID) -> HttpResponse:
    evento     = await eventoSvc.obtener(evento_pk)
    coberturas = await coberturaSvc.listar(evento_pk)
    return render(request, "eventos/cobertura_lista.html", {
        "evento": evento, "coberturas": coberturas,
    })


async def cobertura_agregar(request: HttpRequest, evento_pk: uuid.UUID) -> HttpResponse:
    if request.method == "POST":
        datos = {
            "ocupacion":  request.POST.get("ocupacion", "").strip(),
            "requeridos": int(request.POST.get("requeridos", 0)),
            "asignados":  int(request.POST.get("asignados", 0)),
        }
        if not datos["ocupacion"]:
            messages.error(request, "La ocupación es obligatoria.")
        else:
            await coberturaSvc.agregar(evento_pk, datos)
            messages.success(request, "Cobertura registrada.")
    return redirect("eventos:cobertura_lista", evento_pk=evento_pk)


async def cobertura_eliminar(request: HttpRequest, pk: uuid.UUID) -> HttpResponse:
    if request.method == "POST":
        evento_pk = request.POST.get("evento_pk")
        await coberturaSvc.eliminar(pk)
        messages.success(request, "Cobertura eliminada.")
        return redirect("eventos:cobertura_lista", evento_pk=evento_pk)
    return redirect("eventos:evento_lista")


# =============================================================================
# REGISTRO OPERATIVO
# =============================================================================

async def observacion_agregar(request: HttpRequest, evento_pk: uuid.UUID) -> HttpResponse:
    if request.method == "POST":
        momento   = request.POST.get("momento", "").strip()
        contenido = request.POST.get("contenido", "").strip()

        if not momento or not contenido:
            messages.error(request, "El momento y el contenido son obligatorios.")
        else:
            await observacionSvc.agregar(evento_pk, momento, contenido)
            messages.success(request, "Observación registrada.")

    return redirect("eventos:evento_detalle", pk=evento_pk)


async def asistencia_registrar(request: HttpRequest, evento_pk: uuid.UUID) -> HttpResponse:
    evento       = await eventoSvc.obtener(evento_pk)
    asignaciones = await asignacionSvc.listar(evento_pk)

    if request.method == "POST":
        asistencias = {
            a["simpatizante_id"]: request.POST.get(f"asistio_{a['simpatizante_id']}") == "on"
            for a in asignaciones
        }
        actualizados = await asignacionSvc.registrar_asistencia(evento_pk, asistencias)
        messages.success(request, f"Asistencia registrada para {actualizados} personas.")
        return redirect("eventos:evento_detalle", pk=evento_pk)

    return render(request, "eventos/asistencia.html", {
        "evento": evento, "asignaciones": asignaciones,
    })


async def participacion_externa_registrar(request: HttpRequest, evento_pk: uuid.UUID) -> HttpResponse:
    if request.method == "POST":
        cantidad = int(request.POST.get("cantidad", 0))
        notas    = request.POST.get("notas", "").strip() or None
        await participacionSvc.registrar(evento_pk, cantidad, notas)
        messages.success(request, "Participación externa registrada.")
    return redirect("eventos:evento_detalle", pk=evento_pk)


# =============================================================================
# MATERIAL PUBLICITARIO
# =============================================================================

async def material_detalle(request: HttpRequest, evento_pk: uuid.UUID) -> HttpResponse:
    evento       = await eventoSvc.obtener(evento_pk)
    material     = await materialSvc.obtener(evento_pk)
    estados      = await estadoMaterialSvc.listar(evento_pk)
    promedio     = await estadoMaterialSvc.promedio_estado(evento_pk)

    return render(request, "eventos/material.html", {
        "evento":   evento,
        "material": material,
        "estados":  estados,
        "promedio": promedio,
    })


async def material_registrar(request: HttpRequest, evento_pk: uuid.UUID) -> HttpResponse:
    if request.method == "POST":
        entregado = int(request.POST.get("entregado", 0))
        restante  = int(request.POST.get("restante", 0))
        await materialSvc.registrar(evento_pk, entregado, restante)
        messages.success(request, "Material publicitario registrado.")
    return redirect("eventos:material_detalle", evento_pk=evento_pk)


async def estado_material_registrar(request: HttpRequest, evento_pk: uuid.UUID) -> HttpResponse:
    if request.method == "POST":
        estado = request.POST.get("estado", "").strip()
        notas  = request.POST.get("notas", "").strip() or None

        if not estado:
            messages.error(request, "El estado es obligatorio.")
        else:
            await estadoMaterialSvc.registrar(evento_pk, estado, notas)
            messages.success(request, "Estado del material registrado.")

    return redirect("eventos:material_detalle", evento_pk=evento_pk)


async def estado_material_cargar_csv(request: HttpRequest, evento_pk: uuid.UUID) -> HttpResponse:
    if request.method == "POST" and request.FILES.get("archivo_csv"):
        archivo = request.FILES["archivo_csv"]
        contenido = archivo.read().decode("utf-8")
        resultado = await estadoMaterialSvc.cargar_csv(contenido)

        if resultado["errores"]:
            for error in resultado["errores"]:
                messages.warning(request, error)

        messages.success(
            request,
            f"CSV procesado: {resultado['procesados']} registros importados."
        )

    return redirect("eventos:material_detalle", evento_pk=evento_pk)