import {
  Column,
  CreateDateColumn,
  Entity,
  PrimaryGeneratedColumn,
  UpdateDateColumn,
} from 'typeorm';

export enum Perfil {
  TENDERO = 'tendero',
  CAJERO = 'cajero',
  VENDEDOR = 'vendedor',
  OPERADOR = 'operador',
  SUPERVISOR = 'supervisor',
}

export enum EstadoCaptacion {
  PROSPECTO_CREADO = 'prospectoCreado',
  VISITA_1_REALIZADA = 'visita1Realizada',
  DOCUMENTOS_RECIBIDOS = 'documentosRecibidos',
  VISITA_2_REALIZADA = 'visita2Realizada',
  RUT_VALIDADO = 'rutValidado',
  HABILITADO_BASICO = 'habilitadoBasico',
  HABILITADO_AVANZADO = 'habilitadoAvanzado',
}

export interface ResponsableTienda {
  nombre: string;
  telefono: string;
  perfil: Perfil;
}

@Entity('tiendas')
export class Tienda {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column('varchar', { length: 100 })
  codigoInterno: string;

  @Column('varchar', { length: 255 })
  nombreComercial: string;

  @Column('jsonb')
  responsable: ResponsableTienda;

  @Column('varchar', { length: 50 })
  rut: string;

  @Column('varchar', { length: 50 })
  telefono: string;

  @Column({
    type: 'enum',
    enum: EstadoCaptacion,
  })
  estadoCaptacion: EstadoCaptacion;

  @CreateDateColumn()
  createdAt: Date;

  @UpdateDateColumn()
  updatedAt: Date;
}