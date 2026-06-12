"""
encender.py — Levanta el servidor PactoHistórico en LAN con HTTPS
Se ejecuta con:
    python encender.py
"""

import os
import sys
import subprocess
import time
import ctypes
import threading
import atexit
import shutil

# ── Constantes ────────────────────────────────────────────────────────
PUERTO        = 8443
FIREWALL_NAME = "PactoHistorico LAN"
ASGI_APP      = "app.asgi:application"
CERT_DIR      = os.path.join(os.path.expanduser("~"), ".pactohistorico_certs")
CERT_FILE     = os.path.join(CERT_DIR, "server.crt")
KEY_FILE      = os.path.join(CERT_DIR, "server.key")

# ── Colores en consola ────────────────────────────────────────────────
class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    RED    = "\033[91m"
    CYAN   = "\033[96m"

def ok(msg):   print(f"  {C.GREEN}✓{C.RESET}  {msg}")
def info(msg): print(f"  {C.CYAN}i{C.RESET}  {msg}")
def warn(msg): print(f"  {C.YELLOW}!{C.RESET}  {msg}")
def err(msg):  print(f"  {C.RED}✗{C.RESET}  {msg}")
def header(msg):
    print(f"\n{C.BOLD}{C.CYAN}{'─'*54}{C.RESET}")
    print(f"{C.BOLD}{C.CYAN}  {msg}{C.RESET}")
    print(f"{C.BOLD}{C.CYAN}{'─'*54}{C.RESET}")

# ── Admin ─────────────────────────────────────────────────────────────
def es_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# ── Matar proceso y todos sus hijos ──────────────────────────────────
def matar_proceso_arbol(pid):
    try:
        subprocess.run(
            ["taskkill", "/F", "/T", "/PID", str(pid)],
            capture_output=True
        )
    except:
        pass

# ── Obtener IPs locales LAN ───────────────────────────────────────────
def obtener_ips_lan():
    wifi    = []
    hotspot = []
    try:
        result = subprocess.run(
            ["ipconfig"], capture_output=True, text=True, encoding="cp850"
        )
        for line in result.stdout.splitlines():
            if "IPv4" in line:
                partes = line.split(":")
                if len(partes) > 1:
                    ip = partes[-1].strip()
                    if ip.startswith("192.168.43."):
                        hotspot.append(ip)
                    elif (ip.startswith("192.168.") or
                          ip.startswith("10.")      or
                          (ip.startswith("172.") and
                           16 <= int(ip.split(".")[1]) <= 31)):
                        wifi.append(ip)
    except Exception as e:
        warn(f"No se pudo detectar la IP: {e}")
    return wifi, hotspot

# ── Firewall ──────────────────────────────────────────────────────────
def abrir_puerto():
    try:
        subprocess.run(
            ["powershell", "-Command",
             f'Remove-NetFirewallRule -DisplayName "{FIREWALL_NAME}" -ErrorAction SilentlyContinue'],
            capture_output=True
        )
        subprocess.run(
            ["powershell", "-Command",
             f'New-NetFirewallRule -DisplayName "{FIREWALL_NAME}" '
             f'-Direction Inbound -Protocol TCP -LocalPort {PUERTO} -Action Allow'],
            capture_output=True, check=True
        )
        ok(f"Puerto {PUERTO} abierto en el firewall de Windows")
    except Exception as e:
        warn(f"No se pudo abrir el firewall: {e}")

def cerrar_puerto():
    try:
        subprocess.run(
            ["powershell", "-Command",
             f'Remove-NetFirewallRule -DisplayName "{FIREWALL_NAME}" -ErrorAction SilentlyContinue'],
            capture_output=True
        )
        ok(f"Puerto {PUERTO} cerrado en el firewall")
    except:
        warn("No se pudo cerrar el firewall automáticamente")

# ── Certificados HTTPS ────────────────────────────────────────────────

def _buscar_mkcert():
    ruta = shutil.which("mkcert")
    if ruta:
        return ruta

    program_files   = os.environ.get("ProgramFiles",      r"C:\Program Files")
    program_files86 = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
    local_app       = os.environ.get("LOCALAPPDATA", "")
    userprofile     = os.environ.get("USERPROFILE",  "")

    candidatos = [
        os.path.join(program_files,   "mkcert", "mkcert.exe"),
        os.path.join(program_files86, "mkcert", "mkcert.exe"),
        os.path.join(program_files,   "FiloSottile", "mkcert", "mkcert.exe"),
        os.path.join(local_app, "Microsoft", "WinGet", "Packages",
                     "FiloSottile.mkcert_Microsoft.Winget.Source_8wekyb3d8bbwe",
                     "mkcert.exe"),
        os.path.join(local_app, "Programs", "mkcert", "mkcert.exe"),
        os.path.join(userprofile, "scoop", "shims", "mkcert.exe"),
        r"C:\ProgramData\chocolatey\bin\mkcert.exe",
        r"C:\Windows\System32\mkcert.exe",
    ]

    for c in candidatos:
        if os.path.exists(c):
            return c

    for base in [program_files, program_files86]:
        if os.path.isdir(base):
            try:
                for carpeta in os.listdir(base):
                    candidato = os.path.join(base, carpeta, "mkcert.exe")
                    if os.path.exists(candidato):
                        return candidato
            except:
                pass

    return None

def _instalar_mkcert():
    info("Intentando instalar mkcert con winget (--scope machine)...")
    try:
        resultado = subprocess.run(
            ["winget", "install", "--id", "FiloSottile.mkcert",
             "--accept-source-agreements", "--accept-package-agreements",
             "-e", "--scope", "machine"],
            capture_output=True, text=True
        )
        if resultado.returncode == 0:
            ok("mkcert instalado correctamente con winget")
            return True

        info("Reintentando con --scope user...")
        resultado2 = subprocess.run(
            ["winget", "install", "--id", "FiloSottile.mkcert",
             "--accept-source-agreements", "--accept-package-agreements",
             "-e", "--scope", "user"],
            capture_output=True, text=True
        )
        if resultado2.returncode == 0:
            ok("mkcert instalado correctamente con winget (scope user)")
            return True

        warn("winget no pudo instalar mkcert automáticamente.")
        return False
    except FileNotFoundError:
        warn("winget no está disponible en este sistema.")
        return False

def _refrescar_path():
    try:
        resultado = subprocess.run(
            ["powershell", "-Command",
             '[System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" +'
             '[System.Environment]::GetEnvironmentVariable("Path","User")'],
            capture_output=True, text=True
        )
        if resultado.returncode == 0:
            os.environ["PATH"] = resultado.stdout.strip()
    except:
        pass

def obtener_o_crear_certificados(ips_todas):
    os.makedirs(CERT_DIR, exist_ok=True)

    mkcert = _buscar_mkcert()

    if not mkcert:
        warn("mkcert no encontrado en el sistema.")
        instalado = _instalar_mkcert()
        if instalado:
            _refrescar_path()
            mkcert = _buscar_mkcert()

    if not mkcert:
        print()
        print(f"  {C.BOLD}{C.YELLOW}┌─────────────────────────────────────────────────┐{C.RESET}")
        print(f"  {C.BOLD}{C.YELLOW}│  mkcert no está instalado. Instalalo así:       │{C.RESET}")
        print(f"  {C.BOLD}{C.YELLOW}│                                                 │{C.RESET}")
        print(f"  {C.BOLD}{C.YELLOW}│  winget install --id FiloSottile.mkcert -e      │{C.RESET}")
        print(f"  {C.BOLD}{C.YELLOW}│                                                 │{C.RESET}")
        print(f"  {C.BOLD}{C.YELLOW}│  Luego cerrá y volvé a abrir esta ventana.      │{C.RESET}")
        print(f"  {C.BOLD}{C.YELLOW}└─────────────────────────────────────────────────┘{C.RESET}")
        print()
        input("  Presioná Enter para salir...")
        sys.exit(1)

    necesita_generar = not (os.path.exists(CERT_FILE) and os.path.exists(KEY_FILE))

    if not necesita_generar and ips_todas:
        try:
            resultado = subprocess.run(
                ["powershell", "-Command",
                 f'$c = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2 "{CERT_FILE}";'
                 f'$c.Extensions | Where-Object {{$_.Oid.FriendlyName -eq "Subject Alternative Name"}} | Select-Object -ExpandProperty Format($false)'],
                capture_output=True, text=True
            )
            contenido_san = resultado.stdout
            for ip in ips_todas:
                if ip not in contenido_san:
                    necesita_generar = True
                    info(f"IP {ip} no cubierta por el certificado actual — regenerando.")
                    break
        except:
            necesita_generar = True

    if necesita_generar:
        info("Generando certificado HTTPS para LAN...")
        subprocess.run([mkcert, "-install"], capture_output=True)
        hosts = ["localhost", "127.0.0.1", "::1"] + list(ips_todas)
        resultado = subprocess.run(
            [mkcert,
             "-cert-file", CERT_FILE,
             "-key-file",  KEY_FILE] + hosts,
            capture_output=True, text=True,
            cwd=CERT_DIR
        )
        if resultado.returncode != 0:
            err("Error generando el certificado:")
            print(resultado.stderr)
            sys.exit(1)
        ok(f"Certificado generado para: {', '.join(hosts)}")
    else:
        ok("Certificado HTTPS existente y válido — reutilizando")

    return CERT_FILE, KEY_FILE

# ── Rutas ─────────────────────────────────────────────────────────────
def resolver_ruta_proyecto():
    print()
    respuesta = input("  Ruta del proyecto: ").strip()
    if not respuesta:
        err("Debes ingresar la ruta del proyecto.")
        sys.exit(1)
    if not os.path.isdir(respuesta):
        err(f"La ruta '{respuesta}' no existe.")
        sys.exit(1)
    ok(f"Proyecto: {respuesta}")
    return respuesta

def resolver_ruta_venv():
    print()
    respuesta = input("  Ruta del entorno virtual: ").strip()
    if not respuesta:
        err("Debes ingresar la ruta del entorno virtual.")
        sys.exit(1)
    python_exe = os.path.join(respuesta, "Scripts", "python.exe")
    if not os.path.exists(python_exe):
        err(f"No se encontró python.exe en: {python_exe}")
        sys.exit(1)
    ok(f"Entorno virtual válido: {respuesta}")
    return python_exe

# ── Dependencias ──────────────────────────────────────────────────────
def instalar_dependencias(python_venv, ruta_proyecto):
    req = os.path.join(ruta_proyecto, "requirements.txt")
    if os.path.exists(req):
        info("Instalando/verificando dependencias...")
        subprocess.run(
            [python_venv, "-m", "pip", "install", "-r", req, "-q"],
            check=True
        )
        ok("Dependencias verificadas")
    else:
        warn("No se encontró requirements.txt — omitiendo")

# ── Navegador ─────────────────────────────────────────────────────────
def abrir_navegador():
    time.sleep(2)
    try:
        subprocess.Popen(
            ["powershell", "-Command",
             f'Start-Process "https://127.0.0.1:{PUERTO}/login/"'],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
    except:
        pass

# ── Preguntas de inicio ───────────────────────────────────────────────

def preguntar_entorno():
    print()
    print(f"  {C.BOLD}¿En qué entorno querés iniciar?{C.RESET}")
    print()
    print(f"  {C.BOLD}{C.GREEN}  [1] Producción{C.RESET}   — Base de datos local.")
    print(f"  {C.CYAN}              Sin debug, configuración estable.{C.RESET}")
    print()
    print(f"  {C.BOLD}{C.YELLOW}  [2] Desarrollo{C.RESET}   — Base de datos Railway.")
    print(f"  {C.CYAN}              Debug activo, apunta a la BD en la nube.{C.RESET}")
    print()
    while True:
        opcion = input("  Opción [1/2]: ").strip()
        if opcion == "1":
            ok("Entorno: Producción (BD local)")
            return "app.settings.production"
        elif opcion == "2":
            ok("Entorno: Desarrollo (BD Railway)")
            return "app.settings.development"
        else:
            warn("Escribí 1 o 2.")

def preguntar_modo():
    print()
    print(f"  {C.BOLD}¿En qué modo querés iniciar el servidor?{C.RESET}")
    print()
    print(f"  {C.BOLD}{C.GREEN}  [1] Uso{C.RESET}          — Sin recarga automática, más estable.")
    print()
    print(f"  {C.BOLD}{C.YELLOW}  [2] Desarrollo{C.RESET}   — Recarga automática al guardar archivos.")
    print()
    while True:
        opcion = input("  Opción [1/2]: ").strip()
        if opcion == "1":
            ok("Modo: Uso (sin --reload)")
            return "uso"
        elif opcion == "2":
            ok("Modo: Desarrollo (con --reload)")
            return "desarrollo"
        else:
            warn("Escribí 1 o 2.")

# ── Fase 1: UAC + preguntar configuración + relanzar con venv ─────────
def fase_uac():
    os.system("color")
    header("PactoHistórico · Servidor LAN")

    if not es_admin():
        script = os.path.abspath(__file__)
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable,
            f'"{script}" --fase-uac',
            None, 1
        )
        sys.exit(0)

    header("1 · Entorno")
    settings_module = preguntar_entorno()

    header("2 · Modo de inicio")
    modo = preguntar_modo()

    header("3 · Entorno virtual")
    python_venv = resolver_ruta_venv()

    header("4 · Ruta del proyecto")
    ruta_proyecto = resolver_ruta_proyecto()

    script = os.path.abspath(__file__)
    subprocess.Popen(
        ["cmd.exe", "/k",
         python_venv, script, "--fase-server",
         ruta_proyecto, python_venv, modo, settings_module]
    )
    sys.exit(0)

# ── Fase 2: servidor + ventana de control separada ────────────────────
def fase_server(ruta_proyecto, python_venv, modo="uso", settings_module="app.settings.production"):
    os.system("color")
    os.chdir(ruta_proyecto)

    etiqueta_entorno = "Producción (BD local)" if "production" in settings_module else "Desarrollo (BD Railway)"
    etiqueta_modo    = "Desarrollo  (recarga automática activa)" if modo == "desarrollo" else "Uso"

    header("PactoHistórico · Servidor LAN (HTTPS)")
    ok(f"Proyecto:  {ruta_proyecto}")
    ok(f"Python:    {python_venv}")
    ok(f"Entorno:   {etiqueta_entorno}")
    ok(f"Modo:      {etiqueta_modo}")
    ok(f"Settings:  {settings_module}")

    header("2 · Dependencias")
    instalar_dependencias(python_venv, ruta_proyecto)

    header("3 · Firewall")
    abrir_puerto()

    header("4 · Red LAN")
    wifi, hotspot = obtener_ips_lan()
    ips_todas = wifi + hotspot

    header("5 · Certificado HTTPS")
    cert_file, key_file = obtener_o_crear_certificados(ips_todas)

    header("6 · Direcciones de acceso")

    if wifi:
        print(f"\n  {C.BOLD}{C.GREEN}── Conectados al mismo WiFi/router ─────────{C.RESET}")
        for ip in wifi:
            print(f"     {C.BOLD}https://{ip}:{PUERTO}/login/{C.RESET}")
        print(f"  {C.CYAN}  → Úsala cuando todos están en el mismo WiFi de casa u oficina{C.RESET}")

    if hotspot:
        print(f"\n  {C.BOLD}{C.YELLOW}── Conectados al hotspot del celular ────────{C.RESET}")
        for ip in hotspot:
            print(f"     {C.BOLD}https://{ip}:{PUERTO}/login/{C.RESET}")
        print(f"  {C.CYAN}  → Úsala cuando otros dispositivos se conectan a los datos de este PC{C.RESET}")
        print(f"  {C.YELLOW}  ! El celular que comparte los datos NO puede acceder por esta vía{C.RESET}")

    if not wifi and not hotspot:
        warn("No se detectaron IPs LAN. Conéctate a una red WiFi o Ethernet.")

    print()
    info(f"Tu acceso local: {C.BOLD}https://127.0.0.1:{PUERTO}/login/{C.RESET}")

    print()
    print(f"  {C.BOLD}{C.CYAN}┌─────────────────────────────────────────────────────┐{C.RESET}")
    print(f"  {C.BOLD}{C.CYAN}│  Los otros dispositivos verán una advertencia de    │{C.RESET}")
    print(f"  {C.BOLD}{C.CYAN}│  seguridad la primera vez. Es normal en LAN.        │{C.RESET}")
    print(f"  {C.BOLD}{C.CYAN}│  Hacen clic en 'Avanzado' → 'Continuar al sitio'.  │{C.RESET}")
    print(f"  {C.BOLD}{C.CYAN}│  Solo se hace una vez por dispositivo.              │{C.RESET}")
    print(f"  {C.BOLD}{C.CYAN}└─────────────────────────────────────────────────────┘{C.RESET}")

    header("7 · Iniciando servidor HTTPS")
    info("Uvicorn HTTPS se abrirá en una ventana separada.")
    info("Escribe 'apagar' aquí para detener el servidor.\n")

    # ── Entorno para el proceso hijo ──────────────────────────────────
    # DJANGO_SETTINGS_MODULE se inyecta en el entorno del proceso uvicorn
    # para que Django arranque con los settings correctos.
    env = os.environ.copy()
    env["DJANGO_SETTINGS_MODULE"] = settings_module

    venv_dir     = os.path.dirname(os.path.dirname(python_venv))
    uvicorn_path = os.path.join(venv_dir, "Scripts", "uvicorn.exe")

    if os.path.exists(uvicorn_path):
        cmd_server = [uvicorn_path, ASGI_APP,
                      "--host", "0.0.0.0",
                      "--port", str(PUERTO),
                      "--ssl-certfile", cert_file,
                      "--ssl-keyfile",  key_file]
    else:
        cmd_server = [python_venv, "-m", "uvicorn", ASGI_APP,
                      "--host", "0.0.0.0",
                      "--port", str(PUERTO),
                      "--ssl-certfile", cert_file,
                      "--ssl-keyfile",  key_file]

    if modo == "desarrollo":
        cmd_server.append("--reload")

    proceso = subprocess.Popen(
        ["cmd.exe", "/k"] + cmd_server,
        cwd=ruta_proyecto,
        env=env,
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )

    atexit.register(cerrar_puerto)
    atexit.register(matar_proceso_arbol, proceso.pid)

    threading.Thread(target=abrir_navegador, daemon=True).start()

    print(f"  {C.BOLD}{C.YELLOW}┌─────────────────────────────────────────┐{C.RESET}")
    print(f"  {C.BOLD}{C.YELLOW}│  Escribe 'apagar' para detener el       │{C.RESET}")
    print(f"  {C.BOLD}{C.YELLOW}│  servidor y cerrar el puerto.           │{C.RESET}")
    print(f"  {C.BOLD}{C.YELLOW}│  O simplemente cierra esta ventana.     │{C.RESET}")
    print(f"  {C.BOLD}{C.YELLOW}└─────────────────────────────────────────┘{C.RESET}")
    print()

    while True:
        try:
            cmd = input("  > ").strip().lower()
            if cmd == "apagar":
                print()
                header("Apagando servidor...")
                matar_proceso_arbol(proceso.pid)
                ok("Servidor detenido")
                cerrar_puerto()
                atexit.unregister(cerrar_puerto)
                atexit.unregister(matar_proceso_arbol)
                print()
                print(f"  {C.BOLD}Hasta luego.{C.RESET}\n")
                input("  Presiona Enter para cerrar...")
                os._exit(0)
            else:
                info("Escribe 'apagar' para detener el servidor.")
        except (EOFError, KeyboardInterrupt):
            matar_proceso_arbol(proceso.pid)
            cerrar_puerto()
            os._exit(0)

# ── Entrada ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    args = sys.argv[1:]

    if "--fase-server" in args:
        idx             = args.index("--fase-server")
        ruta_proyecto   = args[idx + 1]
        python_venv     = args[idx + 2]
        modo            = args[idx + 3] if len(args) > idx + 3 else "uso"
        settings_module = args[idx + 4] if len(args) > idx + 4 else "app.settings.production"
        fase_server(ruta_proyecto, python_venv, modo, settings_module)
    else:
        fase_uac()