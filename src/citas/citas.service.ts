import {
  Injectable,
  BadRequestException,
  NotFoundException,
} from "@nestjs/common";
import { PrismaService } from "../prisma/prisma.service";
import { CreateCitaDto } from "./dto/create-cita.dto";
import { NotificationsService } from "../notifications/notifications.service";

@Injectable()
export class CitasService {
  constructor(
    private prisma: PrismaService,
    private notifications: NotificationsService,
  ) {}

  async findAll(user: any) {
    if (user.rol === "cliente") {
      return this.prisma.cita.findMany({
        where: { cliente_id: user.userId },
        include: { usuario: true, tipoServicio: true },
      });
    }
    return this.prisma.cita.findMany({
      include: { usuario: true, tipoServicio: true },
    });
  }

  async create(userId: number, dto: CreateCitaDto) {
    const cita = await this.prisma.cita.create({
      data: {
        cliente_id: userId,
        tipo_servicio_id: dto.servicio,
        modelo_auto: dto.vehiculo_modelo,
        descripcion_problema: dto.descripcion,
        fecha_inicio: new Date(dto.fecha_preferida),
        hora_inicio: dto.hora_inicio,
        estado: "pendiente",
      },
      include: { tipoServicio: true, usuario: true },
    });

    // NotificaciÃ³n a Discord
    await this.notifications.sendDiscordNotification(
      "Nueva Solicitud de Cita",
      `ðŸ“  **Cliente:** ${cita.usuario.nombre}\nðŸš— **VehÃ­culo:** ${cita.modelo_auto}\nðŸ› ï¸  **Servicio:** ${cita.tipoServicio.nombre}\nðŸ“… **Fecha:** ${dto.fecha_preferida}`,
      0x3498db, // Azul
    );

    return cita;
  }

  async aceptar(id: number, duracionReal?: number) {
    const cita = await this.prisma.cita.findUnique({
      where: { id },
      include: { tipoServicio: true, usuario: true },
    });

    if (!cita) throw new NotFoundException("Cita no encontrada");
    if (cita.estado !== "pendiente")
      throw new BadRequestException("Solo se pueden aceptar citas pendientes");

    const duracion = duracionReal || cita.tipoServicio.duracion_dias;
    const fechaFin = new Date(cita.fecha_inicio);
    if (duracion > 0) fechaFin.setDate(fechaFin.getDate() + duracion - 1);

    const result = await this.prisma.$transaction(async (tx) => {
      const updated = await tx.cita.update({
        where: { id },
        data: {
          estado: "aceptada",
          fecha_fin: fechaFin,
          duracion_dias_real: duracion,
        },
      });

      if (cita.tipoServicio.ocupa_cupo_dia) {
        for (let i = 0; i < duracion; i++) {
          const f = new Date(cita.fecha_inicio);
          f.setDate(f.getDate() + i);
          await tx.ocupacionDiaria.create({
            data: { cita_id: id, fecha: f, ocupa_cupo: true },
          });
        }
      } else {
        await tx.ocupacionDiaria.create({
          data: {
            cita_id: id,
            fecha: cita.fecha_inicio,
            ocupa_cupo: false,
            hora_inicio: cita.hora_inicio,
          },
        });
      }
      return updated;
    });

    // NotificaciÃ³n de aprobaciÃ³n
    await this.notifications.sendDiscordNotification(
      "Cita Aceptada",
      `âœ… La cita para **${cita.usuario.nombre}** (${cita.modelo_auto}) ha sido confirmada.\nðŸ“… FinalizaciÃ³n estimada: ${fechaFin.toLocaleDateString()}`,
      0x2ecc71, // Verde
    );

    return result;
  }

  async rechazar(id: number, razon: string) {
    const cita = await this.prisma.cita.findUnique({
      where: { id },
      include: { usuario: true },
    });
    if (!cita || cita.estado !== "pendiente")
      throw new BadRequestException("No se puede rechazar esta cita");

    const updated = await this.prisma.cita.update({
      where: { id },
      data: { estado: "rechazada", razon_rechazo: razon },
    });

    await this.notifications.sendDiscordNotification(
      "Cita Rechazada",
      `âŒ Cita de **${cita.usuario.nombre}** rechazada.\nðŸ“ **RazÃ³n:** ${razon}`,
      0xe74c3c, // Rojo
    );

    return updated;
  }

  async cancelar(id: number) {
    return this.prisma.$transaction(async (tx) => {
      const cita = await tx.cita.findUnique({ where: { id } });
      if (!cita) throw new NotFoundException("Cita no encontrada");

      await tx.ocupacionDiaria.deleteMany({ where: { cita_id: id } });
      const updated = await tx.cita.update({
        where: { id },
        data: { estado: "cancelada" },
      });

      return updated;
    });
  }
}
