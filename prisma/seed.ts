import { PrismaClient } from '@prisma/client';
const prisma = new PrismaClient();

async function main() {
  // Crear tipos de servicio base
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
    await prisma.tipoServicio.upsert({
      where: { id: servicios.indexOf(s) + 1 },
      update: s,
      create: s,
    });
  }
  console.log('✅ Tipos de servicio creados');

  // Crear configuración del taller (si no existe)
  await prisma.configuracionTaller.upsert({
    where: { id: 1 },
    update: {},
    create: {
      capacidad_diaria: 5,
      hora_apertura: '08:00',
      hora_cierre: '18:00',
    },
  });
  console.log('✅ Configuración del taller creada');
}

main()
  .catch((e) => { console.error(e); process.exit(1); })
  .finally(() => prisma.$disconnect());
