import { Controller, Get, Patch, Post, Body, UseGuards } from '@nestjs/common';
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

  @Post('seed') @Roles('mecanico') seed() {
    return this.configService.seed();
  }

  @Get('tipos-servicio') getTiposServicio() {
    return this.configService.getTiposServicio();
  }
}
