"""
=============================================================
  TEST DE ENDPOINTS NUEVOS
  - Edicion de citas (PATCH /citas/:id)
  - Estados: en_curso, completar, cancelar
  - CRUD de bloqueos (GET, PATCH, DELETE)
=============================================================
"""
import requests, json, time, sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE = "http://localhost:3000"
TOKEN = None
TS = str(int(time.time()))

def h():
    return {"Content-Type": "application/json", "Authorization": f"Bearer {TOKEN}"}

def show(name, r):
    icon = "[OK]" if r.status_code < 400 else "[FAIL]"
    print(f"\n{'='*60}")
    print(f"{icon} [{r.status_code}] {name}")
    print(f"{'='*60}")
    try:
        print(json.dumps(r.json(), indent=2, ensure_ascii=False)[:500])
    except:
        print(r.text[:300])
    return r

def login(email, passw, label):
    global TOKEN
    r = requests.post(f"{BASE}/auth/login", json={"email": email, "contrasena": passw})
    if r.status_code in (200, 201):
        TOKEN = r.json()["access_token"]
        print(f"\n[KEY] {label} - Token OK")
    return r

MEC_EMAIL = f"mec_new_{TS}@apex.com"
CLI_EMAIL = f"cli_new_{TS}@apex.com"
PASS = "test123456"

print("\n" + "="*60)
print("   TEST DE ENDPOINTS NUEVOS")
print("="*60)

# -- Setup: Registrar usuarios --
print("\n--- SETUP ---")
requests.post(f"{BASE}/auth/register", json={
    "nombre": "Mec Nuevo", "email": MEC_EMAIL,
    "contrasena": PASS, "telefono": "555-9001", "rol": "mecanico"
})
requests.post(f"{BASE}/auth/register", json={
    "nombre": "Cli Nuevo", "email": CLI_EMAIL,
    "contrasena": PASS, "telefono": "555-9002", "rol": "cliente"
})
login(MEC_EMAIL, PASS, "MECANICO")
requests.post(f"{BASE}/configuracion/seed", headers=h())
print("   Setup completado")

# ============================================================
# 1. FLUJO COMPLETO DE ESTADOS DE CITA
# ============================================================
print("\n" + "-"*60)
print("   1. FLUJO DE ESTADOS: pendiente -> aceptada -> en_curso -> completada")
print("-"*60)

# Cliente crea cita
login(CLI_EMAIL, PASS, "CLIENTE")
r = requests.post(f"{BASE}/citas", headers=h(), json={
    "servicio": 2, "vehiculo_modelo": "Tesla Model 3",
    "descripcion": "Afinacion completa", "fecha_preferida": "2026-08-20"
})
cita_id = r.json()["id"]
show(f"POST /citas (crear, ID:{cita_id})", r)

# Mecanico gestiona
login(MEC_EMAIL, PASS, "MECANICO")

show(f"PATCH /citas/{cita_id}/aceptar", requests.patch(
    f"{BASE}/citas/{cita_id}/aceptar", headers=h(), json={"duracionReal": 1}
))

show(f"PATCH /citas/{cita_id}/en-curso", requests.patch(
    f"{BASE}/citas/{cita_id}/en-curso", headers=h()
))

show(f"PATCH /citas/{cita_id}/completar", requests.patch(
    f"{BASE}/citas/{cita_id}/completar", headers=h()
))

# ============================================================
# 2. EDICION DE CITA (PATCH /citas/:id)
# ============================================================
print("\n" + "-"*60)
print("   2. EDICION DE CITA (cambiar fecha y descripcion)")
print("-"*60)

# Crear otra cita para editar
login(CLI_EMAIL, PASS, "CLIENTE")
r = requests.post(f"{BASE}/citas", headers=h(), json={
    "servicio": 1, "vehiculo_modelo": "BMW X5",
    "descripcion": "Cambio de aceite", "fecha_preferida": "2026-09-01"
})
cita_edit_id = r.json()["id"]
show(f"POST /citas (crear para editar, ID:{cita_edit_id})", r)

login(MEC_EMAIL, PASS, "MECANICO")
show(f"PATCH /citas/{cita_edit_id} (editar fecha+desc)", requests.patch(
    f"{BASE}/citas/{cita_edit_id}", headers=h(), json={
        "fecha_preferida": "2026-09-15",
        "descripcion": "Cambio de aceite sintetico premium"
    }
))

# ============================================================
# 3. CANCELAR CITA
# ============================================================
print("\n" + "-"*60)
print("   3. CANCELAR CITA")
print("-"*60)

show(f"PATCH /citas/{cita_edit_id}/cancelar", requests.patch(
    f"{BASE}/citas/{cita_edit_id}/cancelar", headers=h()
))

# ============================================================
# 4. TRANSICION INVALIDA (debe fallar)
# ============================================================
print("\n" + "-"*60)
print("   4. TRANSICION INVALIDA (completada -> en_curso = debe fallar)")
print("-"*60)

show(f"PATCH /citas/{cita_id}/en-curso (ya completada)", requests.patch(
    f"{BASE}/citas/{cita_id}/en-curso", headers=h()
))

# ============================================================
# 5. CRUD DE BLOQUEOS
# ============================================================
print("\n" + "-"*60)
print("   5. CRUD COMPLETO DE BLOQUEOS")
print("-"*60)

# Crear bloqueo
r = requests.post(f"{BASE}/configuracion/bloquear", headers=h(), json={
    "fecha_inicio": "2026-11-01", "fecha_fin": "2026-11-03", "motivo": "Mantenimiento del taller"
})
bloqueo_id = r.json().get("id")
show(f"POST /configuracion/bloquear (crear, ID:{bloqueo_id})", r)

# Listar bloqueos
show("GET /configuracion/bloqueos (listar)", requests.get(
    f"{BASE}/configuracion/bloqueos", headers=h()
))

# Editar bloqueo
show(f"PATCH /configuracion/bloqueos/{bloqueo_id} (editar)", requests.patch(
    f"{BASE}/configuracion/bloqueos/{bloqueo_id}", headers=h(), json={
        "fecha_fin": "2026-11-05",
        "motivo": "Mantenimiento extendido del taller"
    }
))

# Eliminar bloqueo
show(f"DELETE /configuracion/bloqueos/{bloqueo_id} (eliminar)", requests.delete(
    f"{BASE}/configuracion/bloqueos/{bloqueo_id}", headers=h()
))

# Verificar que ya no existe
show("GET /configuracion/bloqueos (verificar eliminacion)", requests.get(
    f"{BASE}/configuracion/bloqueos", headers=h()
))

# ============================================================
# RESUMEN
# ============================================================
print("\n\n" + "="*60)
print("   RESUMEN DE ENDPOINTS NUEVOS PROBADOS")
print("="*60)
print("""
   1. PATCH /citas/:id/en-curso     -> Marcar en curso
   2. PATCH /citas/:id/completar    -> Marcar completada
   3. PATCH /citas/:id              -> Editar fecha/desc
   4. PATCH /citas/:id/cancelar     -> Cancelar cita
   5. Transicion invalida           -> Error controlado
   6. POST  /configuracion/bloquear -> Crear bloqueo
   7. GET   /configuracion/bloqueos -> Listar bloqueos
   8. PATCH /configuracion/bloqueos/:id -> Editar bloqueo
   9. DELETE /configuracion/bloqueos/:id -> Eliminar bloqueo
""")
