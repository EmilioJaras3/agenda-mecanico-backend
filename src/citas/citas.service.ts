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
    // Verificar que el tipo de servicio existe
    const tipoServicio = await this.prisma.tipoServicio.findUnique({
      where: { id: dto.servicio },
    });
    if (!tipoServicio) {
      throw new BadRequestException(
        `El tipo de servicio con id ${dto.servicio} no existe. Ejecuta POST /configuracion/seed para crear los tipos de servicio.`,
      );
    }

    // Verificar que el usuario existe
    const usuario = await this.prisma.usuario.findUnique({
      where: { id: userId },
    });
    if (!usuario) {
      throw new BadRequestException(`Usuario con id ${userId} no encontrado.`);
    }

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

    // Notificacion a Discord
    await this.notifications.sendDiscordNotification(
      "Nueva Solicitud de Cita",
      `📝 **Cliente:** ${cita.usuario.nombre}\n🚗 **Vehiculo:** ${cita.modelo_auto}\n🛠️ **Servicio:** ${cita.tipoServicio.nombre}\n📅 **Fecha:** ${dto.fecha_preferida}`,
      0x3498db,
    ).catch(() => {}); // No fallar si Discord no responde

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

  async editar(id: number, data: any) {
    const cita = await this.prisma.cita.findUnique({ where: { id } });
    if (!cita) throw new NotFoundException("Cita no encontrada");

    const updateData: any = {};
    if (data.fecha_preferida) updateData.fecha_inicio = new Date(data.fecha_preferida);
    if (data.fecha_inicio) updateData.fecha_inicio = new Date(data.fecha_inicio);
    if (data.fecha_fin) updateData.fecha_fin = new Date(data.fecha_fin);
    if (data.descripcion) updateData.descripcion_problema = data.descripcion;
    if (data.descripcion_problema) updateData.descripcion_problema = data.descripcion_problema;
    if (data.estado) {
      const estadosValidos = ["pendiente", "aceptada", "en_curso", "completada", "cancelada"];
      if (!estadosValidos.includes(data.estado)) {
        throw new BadRequestException(`Estado invalido. Validos: ${estadosValidos.join(", ")}`);
      }
      updateData.estado = data.estado;
    }

    return this.prisma.cita.update({ where: { id }, data: updateData });
  }

  async cambiarEstado(id: number, nuevoEstado: string) {
    const cita = await this.prisma.cita.findUnique({ where: { id } });
    if (!cita) throw new NotFoundException("Cita no encontrada");

    const transiciones: Record<string, string[]> = {
      pendiente: ["aceptada", "rechazada", "cancelada"],
      aceptada: ["en_curso", "cancelada"],
      en_curso: ["completada", "cancelada"],
      completada: [],
      cancelada: [],
      rechazada: [],
    };

    const permitidos = transiciones[cita.estado] || [];
    if (!permitidos.includes(nuevoEstado)) {
      throw new BadRequestException(
        `No se puede cambiar de '${cita.estado}' a '${nuevoEstado}'. Transiciones permitidas: ${permitidos.join(", ") || "ninguna"}`,
      );
    }

    return this.prisma.cita.update({ where: { id }, data: { estado: nuevoEstado as any } });
  }
}

