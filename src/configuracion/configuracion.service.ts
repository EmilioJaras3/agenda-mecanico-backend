import { Injectable, NotFoundException } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';
@Injectable()
export class ConfiguracionService {
  constructor(private prisma: PrismaService) {}
  async get() { return this.prisma.configuracionTaller.findUnique({ where: { id: 1 } }); }
  async update(data: any) { return this.prisma.configuracionTaller.update({ where: { id: 1 }, data }); }
  async blockDate(data: { fecha_inicio: string, fecha_fin: string, motivo: string }) {
    return this.prisma.bloqueo.create({ 
      data: { 
        fecha_inicio: new Date(data.fecha_inicio), 
        fecha_fin: new Date(data.fecha_fin), 
        motivo: data.motivo 
      } 
    });
  }

  async getBloqueos() {
    return this.prisma.bloqueo.findMany({ orderBy: { fecha_inicio: 'asc' } });
  }

  async deleteBloqueo(id: number) {
    const bloqueo = await this.prisma.bloqueo.findUnique({ where: { id } });
    if (!bloqueo) throw new NotFoundException('Bloqueo no encontrado');
    await this.prisma.bloqueo.delete({ where: { id } });
    return { message: 'Bloqueo eliminado correctamente', id };
  }

  async updateBloqueo(id: number, data: { fecha_inicio?: string, fecha_fin?: string, motivo?: string }) {
    const bloqueo = await this.prisma.bloqueo.findUnique({ where: { id } });
    if (!bloqueo) throw new NotFoundException('Bloqueo no encontrado');
    const updateData: any = {};
    if (data.fecha_inicio) updateData.fecha_inicio = new Date(data.fecha_inicio);
    if (data.fecha_fin) updateData.fecha_fin = new Date(data.fecha_fin);
    if (data.motivo) updateData.motivo = data.motivo;
    return this.prisma.bloqueo.update({ where: { id }, data: updateData });
  }

  async getTiposServicio() {
    return this.prisma.tipoServicio.findMany();
  }

  async seed() {
    const servicios = [
      { nombre: 'Cambio de Aceite', duracion_min: 60, duracion_dias: 0, ocupa_cupo_dia: false },
      { nombre: 'Afinación Mayor', duracion_min: 0, duracion_dias: 1, ocupa_cupo_dia: true },
      { nombre: 'Frenos (Pastillas y Discos)', duracion_min: 0, duracion_dias: 1, ocupa_cupo_dia: true },
      { nombre: 'Suspensión', duracion_min: 0, duracion_dias: 2, ocupa_cupo_dia: true },
      { nombre: 'Diagnóstico General', duracion_min: 45, duracion_dias: 0, ocupa_cupo_dia: false },
      { nombre: 'Transmisión', duracion_min: 0, duracion_dias: 3, ocupa_cupo_dia: true },
      { nombre: 'Sistema Eléctrico', duracion_min: 0, duracion_dias: 1, ocupa_cupo_dia: true },
      { nombre: 'Hojalatería y Pintura', duracion_min: 0, duracion_dias: 5, ocupa_cupo_dia: true },
    ];

    for (const s of servicios) {
      await this.prisma.tipoServicio.create({ data: s }).catch(() => {});
    }

    await this.prisma.configuracionTaller.upsert({
      where: { id: 1 },
      update: {},
      create: { capacidad_diaria: 5, hora_apertura: '08:00', hora_cierre: '18:00' },
    });

    return { message: 'Seed ejecutado correctamente', servicios: await this.prisma.tipoServicio.findMany() };
  }
}
