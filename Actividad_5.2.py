import time
import random

N = 100000

# Generamos los datos base
datos = [random.randint(50, 500) for _ in range(N)]

# =========================
# 1. LISTA TRADICIONAL
# =========================
inicio = time.time()

lista_tradicional = []
for x in datos:
    lista_tradicional.append(x * 1.10)

total_tradicional = sum(lista_tradicional)

fin = time.time()

print("=== LISTA TRADICIONAL ===")
print("Total:", total_tradicional)
print("Tiempo:", fin - inicio)


# =========================
# 2. LIST COMPREHENSION
# =========================
inicio = time.time()

lista_comp = [x * 1.10 for x in datos]
total_comp = sum(lista_comp)

fin = time.time()

print("\n=== LIST COMPREHENSION ===")
print("Total:", total_comp)
print("Tiempo:", fin - inicio)


# =========================
# 3. GENERADOR
# =========================
inicio = time.time()

generador = (x * 1.10 for x in datos)
total_gen = sum(generador)

fin = time.time()

print("\n=== GENERADOR ===")
print("Total:", total_gen)
print("Tiempo:", fin - inicio)