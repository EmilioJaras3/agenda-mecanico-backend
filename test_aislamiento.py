"""
=============================================================
  PRUEBA DE AISLAMIENTO DE DATOS
  Verifica que las citas de un usuario NO se mezclan con otro
=============================================================
"""
import requests, json, time, sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE = "https://agenda-mecanico-backend-1.onrender.com"
TS = str(int(time.time()))

def h(token):
    return {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}

print("="*60)
print("  PRUEBA DE AISLAMIENTO DE DATOS")
print("="*60)

# 1. Crear dos clientes completamente distintos
print("\n[PASO 1] Registrar 2 clientes distintos...")

r1 = requests.post(f"{BASE}/auth/register", json={
    "nombre": "Alice Martinez", "email": f"alice_{TS}@test.com",
    "contrasena": "pass123", "telefono": "555-1111", "rol": "cliente"
})
token_alice = r1.json()["access_token"]
alice_id = r1.json()["user"]["id"]
print(f"   [OK] Alice registrada (ID: {alice_id})")

r2 = requests.post(f"{BASE}/auth/register", json={
    "nombre": "Bob Garcia", "email": f"bob_{TS}@test.com",
    "contrasena": "pass123", "telefono": "555-2222", "rol": "cliente"
})
token_bob = r2.json()["access_token"]
bob_id = r2.json()["user"]["id"]
print(f"   [OK] Bob registrado (ID: {bob_id})")

# 2. Alice crea 2 citas
print("\n[PASO 2] Alice crea 2 citas...")
r = requests.post(f"{BASE}/citas", headers=h(token_alice), json={
    "servicio": 1, "vehiculo_modelo": "BMW X3 de Alice",
    "descripcion": "Aceite sintetico", "fecha_preferida": "2026-08-01"
})
alice_cita_1 = r.json()["id"]
print(f"   [OK] Cita A1 creada (ID: {alice_cita_1}, cliente_id: {r.json()['cliente_id']})")

r = requests.post(f"{BASE}/citas", headers=h(token_alice), json={
    "servicio": 2, "vehiculo_modelo": "Audi A4 de Alice",
    "descripcion": "Afinacion completa", "fecha_preferida": "2026-08-15"
})
alice_cita_2 = r.json()["id"]
print(f"   [OK] Cita A2 creada (ID: {alice_cita_2}, cliente_id: {r.json()['cliente_id']})")

# 3. Bob crea 1 cita
print("\n[PASO 3] Bob crea 1 cita...")
r = requests.post(f"{BASE}/citas", headers=h(token_bob), json={
    "servicio": 3, "vehiculo_modelo": "Ford Mustang de Bob",
    "descripcion": "Frenos delanteros", "fecha_preferida": "2026-09-01"
})
bob_cita_1 = r.json()["id"]
print(f"   [OK] Cita B1 creada (ID: {bob_cita_1}, cliente_id: {r.json()['cliente_id']})")

# 4. PRUEBA CRITICA: Alice consulta sus citas
print("\n[PASO 4] Alice consulta GET /citas con SU token...")
r = requests.get(f"{BASE}/citas", headers=h(token_alice))
alice_citas = r.json()
alice_ids = [c["id"] for c in alice_citas]
print(f"   Alice ve {len(alice_citas)} citas: IDs {alice_ids}")

# Verificar que Alice solo ve lo suyo
alice_ok = all(c["cliente_id"] == alice_id for c in alice_citas)
bob_cita_en_alice = bob_cita_1 in alice_ids

print(f"   Todas pertenecen a Alice (cliente_id={alice_id})? {'SI' if alice_ok else 'NO - FALLO CRITICO'}")
print(f"   La cita de Bob (ID:{bob_cita_1}) aparece en Alice? {'SI - FALLO CRITICO' if bob_cita_en_alice else 'NO (correcto)'}")

# 5. PRUEBA CRITICA: Bob consulta sus citas
print("\n[PASO 5] Bob consulta GET /citas con SU token...")
r = requests.get(f"{BASE}/citas", headers=h(token_bob))
bob_citas = r.json()
bob_ids = [c["id"] for c in bob_citas]
print(f"   Bob ve {len(bob_citas)} citas: IDs {bob_ids}")

bob_ok = all(c["cliente_id"] == bob_id for c in bob_citas)
alice_cita_en_bob = alice_cita_1 in bob_ids or alice_cita_2 in bob_ids

print(f"   Todas pertenecen a Bob (cliente_id={bob_id})? {'SI' if bob_ok else 'NO - FALLO CRITICO'}")
print(f"   Alguna cita de Alice aparece en Bob? {'SI - FALLO CRITICO' if alice_cita_en_bob else 'NO (correcto)'}")

# 6. Mecanico ve TODO
print("\n[PASO 6] Registrar mecanico y verificar que ve TODAS...")
rm = requests.post(f"{BASE}/auth/register", json={
    "nombre": "Mec Auditor", "email": f"mec_audit_{TS}@test.com",
    "contrasena": "pass123", "telefono": "555-9999", "rol": "mecanico"
})
token_mec = rm.json()["access_token"]
r = requests.get(f"{BASE}/citas", headers=h(token_mec))
todas = r.json()
todas_ids = [c["id"] for c in todas]
mec_ve_alice = alice_cita_1 in todas_ids and alice_cita_2 in todas_ids
mec_ve_bob = bob_cita_1 in todas_ids
print(f"   Mecanico ve {len(todas)} citas totales")
print(f"   Ve las de Alice? {'SI' if mec_ve_alice else 'NO'}")
print(f"   Ve las de Bob? {'SI' if mec_ve_bob else 'NO'}")

# RESULTADO FINAL
print("\n" + "="*60)
print("  RESULTADO FINAL")
print("="*60)
if alice_ok and bob_ok and not bob_cita_en_alice and not alice_cita_en_bob and mec_ve_alice and mec_ve_bob:
    print("\n  [PASSED] AISLAMIENTO DE DATOS VERIFICADO")
    print("  - Cada cliente solo ve sus propias citas")
    print("  - No hay cruce de datos entre usuarios")
    print("  - El mecanico ve todo correctamente")
    print("  - El userId se extrae del JWT, no esta hardcodeado")
else:
    print("\n  [FAILED] HAY PROBLEMAS DE AISLAMIENTO")
    if not alice_ok: print("  - Alice ve citas que no son suyas")
    if not bob_ok: print("  - Bob ve citas que no son suyas")
    if bob_cita_en_alice: print("  - La cita de Bob aparece en las de Alice")
    if alice_cita_en_bob: print("  - La cita de Alice aparece en las de Bob")

print()
