import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings.development")
import django
django.setup()
from django.contrib.auth.hashers import check_password

print("=== Verificador de contraseñas ===")
hash_guardado = input("Hash guardado en BD: ").strip()

while True:
    try:
        password = input("Contraseña a probar: ").strip()
        if not password:
            continue
        if check_password(password, hash_guardado):
            print("✓ Contraseña CORRECTA\n")
        else:
            print("✗ Contraseña incorrecta\n")
    except KeyboardInterrupt:
        print("\nSaliendo.")
        sys.exit(0)