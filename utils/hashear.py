# python utils/hashear.py,
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings.development")

import django
django.setup()

from django.contrib.auth.hashers import make_password

print("=== Generador de contraseñas hasheadas ===")
print("(Ctrl+C para salir)\n")

while True:
    try:
        password = input("Contraseña: ").strip()
        if not password:
            print("La contraseña no puede estar vacía.\n")
            continue
        hashed = make_password(password)
        print(f"Hash: {hashed}\n")
    except KeyboardInterrupt:
        print("\nSaliendo.")
        sys.exit(0)