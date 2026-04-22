# ðŸš€ GuÃ­a de IntegraciÃ³n: Frontend -> Backend (Apex Forge)

Esta guÃ­a explica cÃ³mo conectar el frontend con el backend securizado del sistema de taller mecÃ¡nico.

## 1. Conectividad Base
- **Base URL**: `https://agenda-mecanico-backend-1.onrender.com`
- **ConfiguraciÃ³n Sugerida (Axios)**:
  ```javascript
  const api = axios.create({
    baseURL: 'https://agenda-mecanico-backend-1.onrender.com',
    headers: { 'Content-Type': 'application/json' }
  });
  ```

## 2. AutenticaciÃ³n (Flujo JWT)
Todas las rutas (excepto login/register) estÃ¡n protegidas por un `JwtAuthGuard`.

### Flujo de Login/Registro
1. Consumir `POST /auth/register` (para nuevos usuarios) o `POST /auth/login`.
2. El backend responderÃ¡ con:
   ```json
   {
     "user": { "id": 1, "nombre": "...", "rol": "mecanico" },
     "access_token": "eyJhbGciOiJIUzI1Ni..."
   }
   ```
3. **Persistencia**: Debes guardar el `access_token` en `localStorage` o una Cookie.
4. **EnvÃ­o**: En todas las peticiones siguientes, aÃ±ade el token en el encabezado de la siguiente manera:
   `Authorization: Bearer <tu_token>`

## 3. Endpoints de Negocio

### GestiÃ³n de Citas
- **Listar Citas** (`GET /citas`): Retorna el historial.
- **Crear Cita** (`POST /citas`): 
  - Cuerpo: `{ "cliente_id": 1, "tipo_servicio_id": 1, "modelo_auto": "Jaguar F-Type", "descripcion_problema": "Ruido en motor", "fecha_inicio": "2024-06-12" }`
- **Confirmar Cita** (`PATCH /citas/:id/aceptar`): 
  - **Uso**: Exclusivo para usuarios con rol `mecanico`.
  - **Efecto**: Calcula la fecha de fin automÃ¡ticamente y dispara la notificaciÃ³n a Discord.

## 4. Estados de Cita
La interfaz debe estar preparada para representar estos valores del campo `estado`:
- `pendiente`: ReciÃ©n llegada. Mostrar en Amarillo/Naranja.
- `aceptada`: Lista para trabajar. Mostrar en Verde.
- `rechazada`: No se pudo agendar. Mostrar en Rojo.
- `cancelada`: El cliente desistiÃ³.

---

## 5. Pruebas RÃ¡pidas
Se ha incluido una colecciÃ³n de Postman en la raÃ­z del proyecto para que puedas importar y probar los flujos sin escribir cÃ³digo aÃºn:
`ApexForge_API.postman_collection.json`
