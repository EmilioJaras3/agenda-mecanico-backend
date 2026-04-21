import { IsEmail, IsString, MinLength, IsEnum, IsNotEmpty } from 'class-validator';

export enum RolUsuario {
  cliente = 'cliente',
  mecanico = 'mecanico',
}

export class LoginDto {
  @IsEmail()
  email: string;

  @IsString()
  @MinLength(6)
  contrasena: string;
}

export class RegisterDto {
  @IsString()
  @IsNotEmpty()
  nombre: string;

  @IsEmail()
  email: string;

  @IsString()
  @MinLength(6)
  contrasena: string;

  @IsString()
  @IsNotEmpty()
  telefono: string;

  @IsEnum(RolUsuario)
  rol: RolUsuario;
}
