import logging

from django.shortcuts import render, redirect
from django.views import View
import asyncio

from Backend.moduloLogin.services.services import LoginService

logger = logging.getLogger(__name__)

SESSION_KEY = "coordinador_id"
_login_svc  = LoginService()


# =============================================================================
# Utilidades de sesión — importables desde otros módulos
# =============================================================================

def get_coordinador_sesion(request) -> dict | None:
    cid = request.session.get(SESSION_KEY)
    if not cid:
        return None
    return {
        "id":     cid,
        "nombre": request.session.get("coordinador_nombre", ""),
        "email":  request.session.get("coordinador_email", ""),
    }




def login_requerido(view_func):
    async def wrapper(request, *args, **kwargs):
        if not request.session.get(SESSION_KEY):
            return redirect("login")
        if asyncio.iscoroutinefunction(view_func):
            return await view_func(request, *args, **kwargs)
        else:
            return view_func(request, *args, **kwargs)
    wrapper.__name__ = getattr(view_func, "__name__", "wrapped")
    return wrapper


class LoginRequeridoMixin:
    """Mixin async para vistas basadas en clase."""
    async def dispatch(self, request, *args, **kwargs):
        if not request.session.get(SESSION_KEY):
            return redirect("login")
        return await super().dispatch(request, *args, **kwargs)


# =============================================================================
# LOGIN
# =============================================================================

class LoginView(View):

    async def get(self, request):
        if request.session.get(SESSION_KEY):
            return redirect("eventos_frontend")
        return render(request, "moduloLogin/login.html")

    async def post(self, request):
        email    = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")

        if not email or not password:
            return render(request, "moduloLogin/login.html", {
                "error": "Completa todos los campos.",
                "email": email,
            })

        coordinador = await _login_svc.autenticar(email, password)

        if coordinador is None:
            return render(request, "moduloLogin/login.html", {
                "error": "Correo o contraseña incorrectos.",
                "email": email,
            })

        request.session[SESSION_KEY]          = coordinador["id"]
        request.session["coordinador_nombre"] = coordinador["nombre"]
        request.session["coordinador_email"]  = coordinador["email"]
        logger.info("[LoginView] Sesión iniciada coordinador_id=%s", coordinador["id"])

        return redirect("eventos_frontend")


# =============================================================================
# LOGOUT
# =============================================================================

class LogoutView(View):

    async def get(self, request):
        coordinador_id = request.session.get(SESSION_KEY)
        request.session.flush()
        logger.info("[LogoutView] Sesión cerrada coordinador_id=%s", coordinador_id)
        return redirect("login")