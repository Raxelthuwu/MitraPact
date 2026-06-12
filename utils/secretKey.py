"""
secretKey.py — Generador de SECRET_KEY segura para Django
Se ejecuta con:
    python utils/secretKey.py
"""

# python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

import secrets
import string

def generar_secret_key():
    # Caracteres recomendados por Django para la clave secreta
    caracteres = string.ascii_letters + string.digits + "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)"
    
    # Genera una clave segura de 50 caracteres (longitud estándar de Django)
    nueva_key = "".join(secrets.choice(caracteres) for _ in range(50))
    
    print("\n" + "─" * 60)
    print(" 🔑 ¡NUEVA DJANGO SECRET KEY GENERADA CON ÉXITO!")
    print("─" * 60)
    print(f"\n{nueva_key}\n")
    print("─" * 60)
    print(" Copia esta clave y pégala en tu archivo .env o settings.py")
    print(" ¡No la compartas ni la subas a GitHub!" + "\n")

if __name__ == "__main__":
    generar_secret_key()