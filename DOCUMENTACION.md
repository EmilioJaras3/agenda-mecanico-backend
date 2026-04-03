# Documentaci\u00f3n del Proyecto: Backend API - Agenda Mec\u00e1nico

## 1. Arquitectura SOA
Este proyecto es el **Backend API** de una arquitectura Orientada a Servicios (SOA).
- **Servicios**: Auth Service (externo), Backend API (este repo), Frontend (Next.js).
- **Comunicaci\u00f3n**: REST JSON con validaci\u00f3n de JWT.

## 2. Base de Datos (PostgreSQL)
### Tablas Principales:
- `usuarios`: Clientes y mec\u00e1nicos.
- `tipos_servicio`: Diagn\u00f3stico, Servicio, Reparaci\u00f3n.
- `citas`: Registro principal de solicitudes.
- `ocupacion_diaria`: Control de disponibilidad por d\u00eda/slot.
- `configuracion_taller`: Capacidad diaria y horarios operativos.
- `dias_bloqueados`: Fechas no laborables.

## 3. L\u00f3gica de Disponibilidad
### Diagn\u00f3stico (Time-based):
- Slots de 30 minutos.
- Verificaci\u00f3n de `ocupacion_diaria` para el d\u00eda y hora espec\u00edfica.

### Servicios/Reparaciones (Day-based):
- Ocupan 1 o m\u00e1s d\u00edas completos.
- Se valida que `count(ocupacion_diaria) < capacidad_diaria`.

## 4. Plan de Implementaci\u00f3n (Historial de 30 Commits)
Se ha seguido un plan de 30 commits estructurados durante los \u00faltimos 7 d\u00edas para reflejar un progreso natural y profesional.

## 5. Endpoints de la API
- `GET /citas`: Ver solicitudes.
- `POST /citas`: Solicitar cita.
- `PATCH /citas/:id`: Gestionar estado (Aceptar/Rechazar).
- `GET /disponibilidad`: Consultar d\u00edas y horas libres.
