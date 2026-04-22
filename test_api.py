"""
=============================================================
  Apex Forge API - Script de Pruebas Automatizadas
  El token se guarda automaticamente al hacer login/register
  y se reutiliza en TODAS las demas peticiones.
=============================================================
Instalar dependencia:  pip install requests
Ejecutar:              python test_api.py
"""

import requests
import json
import sys

# ─── CONFIGURACION ────────────────────────────────────────
BASE_URL = "https://agenda-mecanico-backend-1.onrender.com"
TOKEN = None  # Se llena automaticamente al hacer login


# ─── HELPERS ──────────────────────────────────────────────
def headers():
    """Devuelve headers con el token JWT si existe."""
    h = {"Content-Type": "application/json"}
    if TOKEN:
        h["Authorization"] = f"Bearer {TOKEN}"
    return h


def guardar_token(response):
    """Extrae y guarda el token de la respuesta automaticamente."""
    global TOKEN
    data = response.json()
    if "access_token" in data:
        TOKEN = data["access_token"]
        print(f"   🔑 Token guardado: {TOKEN[:20]}...")
    return data


def imprimir(nombre, response):
    """Imprime el resultado de un endpoint de forma bonita."""
    estado = "✅" if response.status_code < 400 else "❌"
    print(f"\n{'='*60}")
    print(f"{estado} [{response.status_code}] {nombre}")
    print(f"{'='*60}")
    try:
        print(json.dumps(response.json(), indent=2, ensure_ascii=False)[:500])
    except Exception:
        print(response.text[:500])


# ─── 1. ENDPOINTS PUBLICOS ───────────────────────────────
def test_health_check():
    r = requests.get(f"{BASE_URL}/")
    imprimir("GET / (Health Check)", r)
    return r


def test_disponibilidad():
    r = requests.get(f"{BASE_URL}/disponibilidad", params={
        "fecha": "2026-05-20",
        "tipo": 1
    })
    imprimir("GET /disponibilidad", r)
    return r


# ─── 2. AUTH ──────────────────────────────────────────────
def test_register_mecanico():
    r = requests.post(f"{BASE_URL}/auth/register", json={
        "nombre": "Admin Mecanico",
        "email": "admin@apexforge.com",
        "contrasena": "password123",
        "telefono": "555-0199",
        "rol": "mecanico"
    })
    imprimir("POST /auth/register (Mecanico)", r)
    if r.status_code in (200, 201):
        guardar_token(r)
    return r


def test_register_cliente():
    r = requests.post(f"{BASE_URL}/auth/register", json={
        "nombre": "Carlos Lopez",
        "email": "carlos@email.com",
        "contrasena": "password123",
        "telefono": "555-1234",
        "rol": "cliente"
    })
    imprimir("POST /auth/register (Cliente)", r)
    if r.status_code in (200, 201):
        guardar_token(r)
    return r


def test_login_mecanico():
    r = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "admin@apexforge.com",
        "contrasena": "password123"
    })
    imprimir("POST /auth/login (Mecanico)", r)
    if r.status_code in (200, 201):
        guardar_token(r)
    return r


def test_login_cliente():
    r = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "carlos@email.com",
        "contrasena": "password123"
    })
    imprimir("POST /auth/login (Cliente)", r)
    if r.status_code in (200, 201):
        guardar_token(r)
    return r


# ─── 3. CITAS ─────────────────────────────────────────────
def test_ver_citas():
    r = requests.get(f"{BASE_URL}/citas", headers=headers())
    imprimir("GET /citas", r)
    return r


def test_crear_cita():
    r = requests.post(f"{BASE_URL}/citas", headers=headers(), json={
        "servicio": 1,
        "vehiculo_modelo": "Porsche Taycan",
        "descripcion": "Revision de frenos regenerativos",
        "fecha_preferida": "2026-05-20"
    })
    imprimir("POST /citas (Crear Cita)", r)
    return r


def test_aceptar_cita(cita_id=1):
    r = requests.patch(f"{BASE_URL}/citas/{cita_id}/aceptar", headers=headers(), json={
        "duracionReal": 2
    })
    imprimir(f"PATCH /citas/{cita_id}/aceptar", r)
    return r


def test_rechazar_cita(cita_id=1):
    r = requests.patch(f"{BASE_URL}/citas/{cita_id}/rechazar", headers=headers(), json={
        "razon": "No hay piezas disponibles en este momento"
    })
    imprimir(f"PATCH /citas/{cita_id}/rechazar", r)
    return r


# ─── 4. CONFIGURACION ────────────────────────────────────
def test_ver_configuracion():
    r = requests.get(f"{BASE_URL}/configuracion", headers=headers())
    imprimir("GET /configuracion", r)
    return r


def test_actualizar_configuracion():
    r = requests.patch(f"{BASE_URL}/configuracion", headers=headers(), json={
        "capacidad_diaria": 8,
        "hora_apertura": "09:00",
        "hora_cierre": "19:00",
        "sabado_trabaja": False
    })
    imprimir("PATCH /configuracion", r)
    return r


def test_bloquear_fechas():
    r = requests.post(f"{BASE_URL}/configuracion/bloquear", headers=headers(), json={
        "fecha_inicio": "2026-12-24",
        "fecha_fin": "2026-12-31",
        "motivo": "Vacaciones de Navidad"
    })
    imprimir("POST /configuracion/bloquear", r)
    return r


# ─── FLUJO COMPLETO ──────────────────────────────────────
def run_all():
    print("\n" + "🚀" * 25)
    print("   APEX FORGE API - PRUEBAS COMPLETAS")
    print("🚀" * 25)
    print(f"\n📡 Apuntando a: {BASE_URL}\n")

    # --- Publicos ---
    print("\n\n" + "─" * 60)
    print("   🌐 ENDPOINTS PUBLICOS")
    print("─" * 60)
    test_health_check()

    # --- Auth: Registrar usuarios ---
    print("\n\n" + "─" * 60)
    print("   🔑 AUTH - REGISTRO")
    print("─" * 60)
    test_register_mecanico()
    test_register_cliente()

    # --- Login como mecanico para probar todo ---
    print("\n\n" + "─" * 60)
    print("   🔑 AUTH - LOGIN MECANICO (token se guarda solo)")
    print("─" * 60)
    test_login_mecanico()

    # --- Configuracion (necesita ser mecanico) ---
    print("\n\n" + "─" * 60)
    print("   🔧 CONFIGURACION (como Mecanico)")
    print("─" * 60)
    test_ver_configuracion()
    test_actualizar_configuracion()
    test_bloquear_fechas()

    # --- Login como cliente para crear cita ---
    print("\n\n" + "─" * 60)
    print("   🔑 AUTH - LOGIN CLIENTE (token se cambia solo)")
    print("─" * 60)
    test_login_cliente()

    # --- Citas como cliente ---
    print("\n\n" + "─" * 60)
    print("   🚗 CITAS (como Cliente)")
    print("─" * 60)
    test_ver_citas()
    test_crear_cita()

    # --- Login como mecanico para aprobar ---
    print("\n\n" + "─" * 60)
    print("   🔑 AUTH - LOGIN MECANICO (para aprobar/rechazar)")
    print("─" * 60)
    test_login_mecanico()

    # --- Aprobar/Rechazar ---
    print("\n\n" + "─" * 60)
    print("   🔧 GESTION DE CITAS (como Mecanico)")
    print("─" * 60)
    test_ver_citas()
    test_aceptar_cita(1)

    # --- Disponibilidad ---
    print("\n\n" + "─" * 60)
    print("   🌐 DISPONIBILIDAD")
    print("─" * 60)
    test_disponibilidad()

    print("\n\n" + "🏁" * 25)
    print("   PRUEBAS FINALIZADAS")
    print("🏁" * 25 + "\n")


if __name__ == "__main__":
    run_all()
