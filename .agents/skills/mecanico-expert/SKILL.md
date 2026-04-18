# Experto en Sistema de Agenda Mecánica

Skill especializada para el desarrollo y mantenimiento del sistema de gestión de taller mecánico "Mecánico Backend".

## Contexto del Proyecto
Este sistema gestiona citas para un taller con capacidad limitada, diferenciando entre servicios rápidos (minutos) y servicios largos (días).

## Reglas de Oro (Strict Rules)
1. **Validación de Capacidad**: Antes de crear o mover una `Cita`, SIEMPRE verificar la `ConfiguracionTaller.capacidad_diaria` y la tabla `OcupacionDiaria`.
2. **Horarios**: Las citas deben respetar `hora_apertura` y `hora_cierre`.
3. **Roles**: 
   - `cliente`: Solo puede ver sus citas y crear nuevas en estado `pendiente`.
   - `mecanico`: Puede gestionar estados, rechazar con motivo y ver la ocupación global.
4. **Estados de Cita**: El flujo es `pendiente` -> `aceptada`|`rechazada` -> `completada`|`cancelada`.

## Patrones de Código (NestJS + Prisma)
- Usar `PrismaService` inyectado.
- Las transacciones de base de datos son obligatorias cuando se crea una `Cita` y sus `OcupacionDiaria` correspondientes.
- Los DTOs deben usar `class-validator` para asegurar que las fechas y horas tengan el formato correcto ("HH:mm").

## Triggers
Úsame cuando:
- Se modifique la lógica de `citas.service.ts` o `disponibilidad.service.ts`.
- Se añadan nuevos modelos a `schema.prisma`.
- Se quiera implementar validaciones de seguridad en los controladores.
