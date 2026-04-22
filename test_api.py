"""
=============================================================
  APEX FORGE - TEST COMPLETO AUTOMATIZADO
  Solo ejecuta: python test_api.py
  NO TOCAS NADA. Todo se hace solo.
=============================================================
"""
import requests, json, sys

BASE = "https://agenda-mecanico-backend-1.onrender.com"
OK = "✅"
FAIL = "❌"
TOKEN = None

def h():
    return {"Content-Type": "application/json", "Authorization": f"Bearer {TOKEN}"}

def show(name, r):
    s = OK if r.status_code < 400 else FAIL
    print(f"\n{'='*60}")
    print(f"{s} [{r.status_code}] {name}")
    print(f"{'='*60}")
    try:
        print(json.dumps(r.json(), indent=2, ensure_ascii=False)[:600])
    except:
        print(r.text[:300])
    return r

def login(email, passw, label):
    global TOKEN
    r = requests.post(f"{BASE}/auth/login", json={"email": email, "contrasena": passw})
    if r.status_code in (200, 201):
        TOKEN = r.json()["access_token"]
        print(f"\n🔑 {label} - Token guardado: {TOKEN[:20]}...")
    else:
        show(f"Login {label}", r)
    return r

def register(nombre, email, passw, tel, rol):
    r = requests.post(f"{BASE}/auth/register", json={
        "nombre": nombre, "email": email, "contrasena": passw, "telefono": tel, "rol": rol
    })
    return r

# ══════════════════════════════════════════════════════════
print("\n" + "🚀" * 20)
print("   APEX FORGE - PRUEBA COMPLETA AUTOMATICA")
print("🚀" * 20)
print(f"\n📡 URL: {BASE}\n")

# ── 1. HEALTH CHECK ──────────────────────────────────────
print("\n" + "─"*60)
print("   🌐 HEALTH CHECK")
print("─"*60)
show("GET /", requests.get(f"{BASE}/"))

# ── 2. REGISTRAR USUARIOS (si no existen) ────────────────
print("\n" + "─"*60)
print("   📝 REGISTRO DE USUARIOS")
print("─"*60)
r = register("Mecanico Admin", "mecanico_test@apex.com", "test123456", "555-0001", "mecanico")
show("Register Mecanico", r)
r = register("Cliente Test", "cliente_test@apex.com", "test123456", "555-0002", "cliente")
show("Register Cliente", r)

# ── 3. LOGIN MECANICO → SEED ─────────────────────────────
print("\n" + "─"*60)
print("   🔧 LOGIN MECANICO + SEED")
print("─"*60)
login("mecanico_test@apex.com", "test123456", "MECANICO")
show("POST /configuracion/seed", requests.post(f"{BASE}/configuracion/seed", headers=h()))

# ── 4. VER TIPOS DE SERVICIO ─────────────────────────────
print("\n" + "─"*60)
print("   📋 TIPOS DE SERVICIO")
print("─"*60)
show("GET /configuracion/tipos-servicio", requests.get(f"{BASE}/configuracion/tipos-servicio", headers=h()))

# ── 5. VER CONFIGURACION ─────────────────────────────────
print("\n" + "─"*60)
print("   ⚙️  CONFIGURACION DEL TALLER")
print("─"*60)
show("GET /configuracion", requests.get(f"{BASE}/configuracion", headers=h()))

# ── 6. ACTUALIZAR CONFIGURACION ──────────────────────────
show("PATCH /configuracion", requests.patch(f"{BASE}/configuracion", headers=h(), json={
    "capacidad_diaria": 8, "hora_apertura": "09:00", "hora_cierre": "19:00"
}))

# ── 7. BLOQUEAR FECHAS ───────────────────────────────────
print("\n" + "─"*60)
print("   🚫 BLOQUEAR FECHAS")
print("─"*60)
show("POST /configuracion/bloquear", requests.post(f"{BASE}/configuracion/bloquear", headers=h(), json={
    "fecha_inicio": "2026-12-24", "fecha_fin": "2026-12-31", "motivo": "Vacaciones Navidad"
}))

# ── 8. LOGIN CLIENTE → CREAR CITA ────────────────────────
print("\n" + "─"*60)
print("   🚗 LOGIN CLIENTE + CREAR CITA")
print("─"*60)
login("cliente_test@apex.com", "test123456", "CLIENTE")

r_cita = requests.post(f"{BASE}/citas", headers=h(), json={
    "servicio": 1, "vehiculo_modelo": "Honda Civic 2024",
    "descripcion": "Cambio de aceite y filtro", "fecha_preferida": "2026-06-15"
})
show("POST /citas (Crear Cita)", r_cita)

# Guardar el ID de la cita creada
cita_id = None
if r_cita.status_code in (200, 201):
    cita_id = r_cita.json().get("id")
    print(f"\n   📌 Cita creada con ID: {cita_id}")

# ── 9. VER MIS CITAS (como cliente) ──────────────────────
print("\n" + "─"*60)
print("   👀 VER MIS CITAS (Cliente)")
print("─"*60)
show("GET /citas (solo mis citas)", requests.get(f"{BASE}/citas", headers=h()))

# ── 10. LOGIN MECANICO → VER TODAS → ACEPTAR ─────────────
print("\n" + "─"*60)
print("   🔧 LOGIN MECANICO + GESTIONAR CITAS")
print("─"*60)
login("mecanico_test@apex.com", "test123456", "MECANICO")

show("GET /citas (TODAS)", requests.get(f"{BASE}/citas", headers=h()))

if cita_id:
    show(f"PATCH /citas/{cita_id}/aceptar", requests.patch(
        f"{BASE}/citas/{cita_id}/aceptar", headers=h(), json={"duracionReal": 2}
    ))

# ── 11. CREAR OTRA CITA Y RECHAZARLA ─────────────────────
print("\n" + "─"*60)
print("   ❌ CREAR CITA + RECHAZAR")
print("─"*60)
login("cliente_test@apex.com", "test123456", "CLIENTE")

r_cita2 = requests.post(f"{BASE}/citas", headers=h(), json={
    "servicio": 3, "vehiculo_modelo": "Toyota Corolla 2022",
    "descripcion": "Ruido en los frenos traseros", "fecha_preferida": "2026-07-01"
})
show("POST /citas (Cita para rechazar)", r_cita2)

cita_id2 = None
if r_cita2.status_code in (200, 201):
    cita_id2 = r_cita2.json().get("id")

login("mecanico_test@apex.com", "test123456", "MECANICO")

if cita_id2:
    show(f"PATCH /citas/{cita_id2}/rechazar", requests.patch(
        f"{BASE}/citas/{cita_id2}/rechazar", headers=h(),
        json={"razon": "No hay piezas disponibles en este momento"}
    ))

# ── 12. DISPONIBILIDAD ───────────────────────────────────
print("\n" + "─"*60)
print("   📅 DISPONIBILIDAD")
print("─"*60)
show("GET /disponibilidad", requests.get(f"{BASE}/disponibilidad", params={"fecha": "2026-06-15", "tipo": 1}))

# ── RESUMEN ───────────────────────────────────────────────
print("\n\n" + "🏁" * 20)
print("   TODAS LAS PRUEBAS FINALIZADAS")
print("🏁" * 20)
print(f"""
📊 Endpoints probados:
   1.  GET  /                          (Health Check)
   2.  POST /auth/register             (Mecanico)
   3.  POST /auth/register             (Cliente)
   4.  POST /auth/login                (Mecanico)
   5.  POST /auth/login                (Cliente)
   6.  POST /configuracion/seed        (Poblar DB)
   7.  GET  /configuracion/tipos-servicio
   8.  GET  /configuracion             (Ver config)
   9.  PATCH /configuracion            (Actualizar)
   10. POST /configuracion/bloquear    (Bloquear fechas)
   11. POST /citas                     (Crear cita)
   12. GET  /citas                     (Ver citas cliente)
   13. GET  /citas                     (Ver todas mecanico)
   14. PATCH /citas/:id/aceptar        (Aprobar)
   15. POST /citas                     (Otra cita)
   16. PATCH /citas/:id/rechazar       (Rechazar)
   17. GET  /disponibilidad            (Consultar)
""")
