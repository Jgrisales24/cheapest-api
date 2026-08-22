import { Type } from 'class-transformer';
import {
  IsEnum,
  IsString,
  MaxLength,
  ValidateNested,
} from 'class-validator';
import { EstadoCaptacion, Perfil } from '../../repositories/entities';

export class ResponsableTiendaDto {
  @IsString()
  @MaxLength(255)
  nombre: string;

  @IsString()
  @MaxLength(50)
  telefono: string;

  @IsEnum(Perfil)
  perfil: Perfil;
}

export class CreateTiendaDto {
  @IsString()
  @MaxLength(100)
  codigoInterno: string;

  @IsString()
  @MaxLength(255)
  nombreComercial: string;

  @ValidateNested()
  @Type(() => ResponsableTiendaDto)
  responsable: ResponsableTiendaDto;

  @IsString()
  @MaxLength(50)
  rut: string;

  @IsString()
  @MaxLength(50)
  telefono: string;

  @IsEnum(EstadoCaptacion)
  estadoCaptacion: EstadoCaptacion;
}