import { Type } from 'class-transformer';
import {
  IsEnum,
  IsOptional,
  IsString,
  MaxLength,
  ValidateNested,
} from 'class-validator';
import { EstadoCaptacion } from '../../repositories/entities';
import { ResponsableTiendaDto } from './create-tienda.dto';

export class UpdateTiendaDto {
  @IsOptional()
  @IsString()
  @MaxLength(100)
  codigoInterno?: string;

  @IsOptional()
  @IsString()
  @MaxLength(255)
  nombreComercial?: string;

  @IsOptional()
  @ValidateNested()
  @Type(() => ResponsableTiendaDto)
  responsable?: ResponsableTiendaDto;

  @IsOptional()
  @IsString()
  @MaxLength(50)
  rut?: string;

  @IsOptional()
  @IsString()
  @MaxLength(50)
  telefono?: string;

  @IsOptional()
  @IsEnum(EstadoCaptacion)
  estadoCaptacion?: EstadoCaptacion;
}