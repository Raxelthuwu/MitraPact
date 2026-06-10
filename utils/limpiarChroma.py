 # python utils/limpiarChroma.py

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings.development")

import django
django.setup()

import chromadb
from django.conf import settings

client = chromadb.PersistentClient(path=str(settings.CHROMA_PERSIST_DIR))

colecciones = ['fragmentos_vec', 'opiniones_vec', 'argumentos_vec']

for nombre in colecciones:
    try:
        col = client.get_collection(nombre)
        total = col.count()
        print(f"[{nombre}] {total} vectores encontrados — eliminando colección...")
        client.delete_collection(nombre)
        print(f"[{nombre}] Colección eliminada.")
    except Exception as e:
        print(f"[{nombre}] No existe o error: {e}")

print("\nChromaDB limpio. Reindexar documentos desde el formulario.") 

""" 


# utils/limpiarChroma.py

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings.development")

import django
django.setup()

import chromadb
from django.conf import settings
from django.db import connection

client = chromadb.PersistentClient(path=str(settings.CHROMA_PERSIST_DIR))

# Obtener IDs válidos de PostgreSQL
with connection.cursor() as cur:
    cur.execute("SELECT id::text FROM busqueda_semantica.documento")
    ids_validos = {row[0] for row in cur.fetchall()}

print(f"Documentos válidos en PostgreSQL: {ids_validos}")

col = client.get_collection('fragmentos_vec')
total = col.count()
print(f"Total vectores en ChromaDB: {total}")

# Obtener todos los IDs de ChromaDB
result = col.get(include=[])
ids_chroma = result['ids']

# Filtrar los huérfanos — cuyo prefijo no está en PostgreSQL
huerfanos = [
    vid for vid in ids_chroma
    if vid.split('_')[0] not in ids_validos
]

print(f"Vectores huérfanos: {len(huerfanos)}")

if huerfanos:
    col.delete(ids=huerfanos)
    print("Huérfanos eliminados.")
else:
    print("No hay huérfanos.") """