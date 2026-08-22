import {
  EstadoCaptacion,
  ResponsableTienda,
} from '../../repositories/entities';

export class TiendaResponseDto {
  id: string;
  codigoInterno: string;
  nombreComercial: string;
  responsable: ResponsableTienda;
  rut: string;
  telefono: string;
  estadoCaptacion: EstadoCaptacion;
  createdAt: Date;
  updatedAt: Date;
}