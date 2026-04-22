import {
  Controller,
  Get,
  Post,
  Body,
  Patch,
  Param,
  UseGuards,
  Request,
} from "@nestjs/common";
import { CitasService } from "./citas.service";
import { CreateCitaDto } from "./dto/create-cita.dto";
import { JwtAuthGuard } from "../auth/jwt-auth.guard";
import { RolesGuard } from "../auth/roles.guard";
import { Roles } from "../auth/roles.decorator";

@UseGuards(JwtAuthGuard, RolesGuard)
@Controller("citas")
export class CitasController {
  constructor(private readonly citasService: CitasService) {}

  @Get()
  findAll(@Request() req: any) {
    return this.citasService.findAll(req.user);
  }

  @Post()
  create(@Request() req: any, @Body() dto: CreateCitaDto) {
    return this.citasService.create(req.user.userId, dto);
  }

  // Rutas especificas PRIMERO (antes del generico :id)
  @Patch(":id/aceptar")
  @Roles("mecanico")
  aceptar(@Param("id") id: string, @Body() body: any) {
    return this.citasService.aceptar(Number(id), body.duracionReal);
  }

  @Patch(":id/rechazar")
  @Roles("mecanico")
  rechazar(@Param("id") id: string, @Body() body: any) {
    return this.citasService.rechazar(
      Number(id),
      body.razon || "El mecánico rechazó la solicitud.",
    );
  }

  @Patch(":id/en-curso")
  @Roles("mecanico")
  enCurso(@Param("id") id: string) {
    return this.citasService.cambiarEstado(Number(id), "en_curso");
  }

  @Patch(":id/completar")
  @Roles("mecanico")
  completar(@Param("id") id: string) {
    return this.citasService.cambiarEstado(Number(id), "completada");
  }

  @Patch(":id/cancelar")
  cancelar(@Param("id") id: string) {
    return this.citasService.cancelar(Number(id));
  }

  // Ruta generica AL FINAL para no interceptar las especificas
  @Patch(":id")
  @Roles("mecanico")
  editar(@Param("id") id: string, @Body() body: any) {
    return this.citasService.editar(Number(id), body);
  }
}
