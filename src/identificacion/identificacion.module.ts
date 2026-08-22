import { Module } from '@nestjs/common';
import { DatabaseModule } from '../datasources/database.module';
import { TiendaController } from './controllers';
import { TiendaRepository } from './repositories';
import { repositoryProviders } from './repositories/repository.providers';
import { TiendaService } from './services';

@Module({
  imports: [DatabaseModule],
  controllers: [TiendaController],
  providers: [
    ...repositoryProviders,
    TiendaRepository,
    TiendaService,
  ],
  exports: [TiendaService],
})
export class IdentificacionModule {}