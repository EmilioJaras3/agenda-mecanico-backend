# 🚀 Guía de Integración: Frontend -> Backend (Apex Forge)

Esta guía explica cómo conectar el frontend con el backend securizado del sistema de taller mecánico.

## 1. Conectividad Base
- **Base URL**: `http://localhost:10000`
- **Configuración Sugerida (Axios)**:
  ```javascript
  const api = axios.create({
    baseURL: 'http://localhost:10000',
    headers: { 'Content-Type': 'application/json' }
  });
  ```

## 2. Autenticación (Flujo JWT)
Todas las rutas (excepto login/register) están protegidas por un `JwtAuthGuard`.

### Flujo de Login/Registro
1. Consumir `POST /auth/register` (para nuevos usuarios) o `POST /auth/login`.
2. El backend responderá con:
   ```json
   {
     "user": { "id": 1, "nombre": "...", "rol": "mecanico" },
     "access_token": "eyJhbGciOiJIUzI1Ni..."
   }
   ```
3. **Persistencia**: Debes guardar el `access_token` en `localStorage` o una Cookie.
4. **Envío**: En todas las peticiones siguientes, añade el token en el encabezado de la siguiente manera:
   `Authorization: Bearer <tu_token>`

## 3. Endpoints de Negocio

### Gestión de Citas
- **Listar Citas** (`GET /citas`): Retorna el historial.
- **Crear Cita** (`POST /citas`): 
  - Cuerpo: `{ "cliente_id": 1, "tipo_servicio_id": 1, "modelo_auto": "Jaguar F-Type", "descripcion_problema": "Ruido en motor", "fecha_inicio": "2024-06-12" }`
- **Confirmar Cita** (`PATCH /citas/:id/aceptar`): 
  - **Uso**: Exclusivo para usuarios con rol `mecanico`.
  - **Efecto**: Calcula la fecha de fin automáticamente y dispara la notificación a Discord.

## 4. Estados de Cita
La interfaz debe estar preparada para representar estos valores del campo `estado`:
- `pendiente`: Recién llegada. Mostrar en Amarillo/Naranja.
- `aceptada`: Lista para trabajar. Mostrar en Verde.
- `rechazada`: No se pudo agendar. Mostrar en Rojo.
- `cancelada`: El cliente desistió.

---

## 5. Pruebas Rápidas
Se ha incluido una colección de Postman en la raíz del proyecto para que puedas importar y probar los flujos sin escribir código aún:
`ApexForge_API.postman_collection.json`
