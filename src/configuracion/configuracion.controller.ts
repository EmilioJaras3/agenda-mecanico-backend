import { Controller, Get, Patch, Post, Delete, Body, Param, UseGuards } from '@nestjs/common';
import { ConfiguracionService } from './configuracion.service';
import { JwtAuthGuard } from '../auth/jwt-auth.guard';
import { RolesGuard } from '../auth/roles.guard';
import { Roles } from '../auth/roles.decorator';
@Controller('configuracion')
@UseGuards(JwtAuthGuard, RolesGuard)
export class ConfiguracionController {
  constructor(private readonly configService: ConfiguracionService) {}
  @Get() @Roles('mecanico') get() { return this.configService.get(); }
  @Patch() @Roles('mecanico') update(@Body() data: any) { return this.configService.update(data); }
  @Post('bloquear') @Roles('mecanico') block(@Body() data: { fecha_inicio: string, fecha_fin: string, motivo: string }) {
    return this.configService.blockDate(data);
  }

  @Get('bloqueos') @Roles('mecanico') getBloqueos() {
    return this.configService.getBloqueos();
  }

  @Delete('bloqueos/:id') @Roles('mecanico') deleteBloqueo(@Param('id') id: string) {
    return this.configService.deleteBloqueo(Number(id));
  }

  @Patch('bloqueos/:id') @Roles('mecanico') updateBloqueo(
    @Param('id') id: string,
    @Body() data: { fecha_inicio?: string, fecha_fin?: string, motivo?: string }
  ) {
    return this.configService.updateBloqueo(Number(id), data);
  }

  @Post('seed') @Roles('mecanico') seed() {
    return this.configService.seed();
  }

  @Get('tipos-servicio') getTiposServicio() {
    return this.configService.getTiposServicio();
  }
}
