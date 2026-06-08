import os
import asyncio
from django.core.asgi import get_asgi_application
from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings.development')

django_application = ASGIStaticFilesHandler(get_asgi_application())

async def application(scope, receive, send):
    if scope['type'] == 'lifespan':
        await _manejarLifespan(scope, receive, send)
        return
    await django_application(scope, receive, send)

async def _manejarLifespan(scope, receive, send):
    while True:
        mensaje = await receive()

        if mensaje['type'] == 'lifespan.startup':
            try:
                from Backend.moduloBusquedaSemantica.services import ClasificacionService
                _svc = ClasificacionService()
                asyncio.create_task(_svc.iniciar())
                await send({'type': 'lifespan.startup.complete'})
            except Exception as e:
                await send({'type': 'lifespan.startup.failed', 'message': str(e)})
                return

        elif mensaje['type'] == 'lifespan.shutdown':
            await send({'type': 'lifespan.shutdown.complete'})
            return