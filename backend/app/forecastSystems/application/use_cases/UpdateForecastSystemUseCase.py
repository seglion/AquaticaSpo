# app/forecast_systems/application/use_cases/UpdateForecastSystemUseCase.py

from typing import Optional

from app.forecastSystems.domain.models import ForecastSystem
from app.forecastSystems.application.repositories import ForecastSystemRepositoryABC
from app.users.domain.models import User # Asumiendo que tienes un modelo User en tu dominio

class UpdateForecastSystemUseCase:
    """
    Caso de uso para actualizar un sistema de previsión existente.
    """
    def __init__(self, repo: ForecastSystemRepositoryABC):
        self.repo = repo

    async def execute(self, updated_system_data: ForecastSystem, requester: User) -> Optional[ForecastSystem]:
        """
        Ejecuta la actualización de un sistema de previsión.

        Args:
            updated_system_data (ForecastSystem): Los datos actualizados del sistema de previsión.
                                                  Debe incluir el ID del sistema a actualizar.
            requester (User): El usuario que solicita la actualización.

        Returns:
            Optional[ForecastSystem]: El objeto ForecastSystem actualizado si se encuentra, o None si no existe.

        Raises:
            ValueError: Si el ID del sistema no está presente en los datos.
            PermissionError: Si el usuario no tiene permisos para actualizar sistemas.
            # Nota: La validación de unicidad del nombre (si se actualiza el nombre a uno existente)
            # se espera que sea manejada por la capa de infraestructura (DB UNIQUE constraint)
            # y la excepción correspondiente (ej. IntegrityError) será capturada en el router de la API.
        """
        # --- Restricción 1: Permisos del usuario ---
        # Solo los usuarios administradores deberían poder actualizar ForecastSystems.
        if not requester.is_admin:
            raise PermissionError("Solo los administradores pueden actualizar sistemas de previsión.")

        # --- Restricción 2: ID del sistema requerido ---
        # El ID es fundamental para saber qué sistema actualizar.
        if updated_system_data.id is None:
            raise ValueError("El ID del sistema de previsión es necesario para la actualización.")

        # --- Restricción 3: Existencia del sistema a actualizar ---
        # Aunque el repositorio puede devolver None, es buena práctica verificar
        # si el sistema realmente existe antes de intentar la actualización.
        # Esto evita que se envíe una actualización a un ID inexistente.
        existing_system = await self.repo.getForecastSystemById(updated_system_data.id)
        if existing_system is None:
            return None # O raise ValueError("Sistema de previsión no encontrado para actualizar.")

        # --- Restricción 4: Unicidad del nombre (si se cambia) ---
        # Si el nombre se está cambiando y ya existe, la DB lo manejará.
        # Si quisieras una validación más explícita aquí, necesitarías comparar
        # el nuevo nombre con los existentes, excluyendo el propio sistema que se actualiza.
        # Por ahora, confiamos en la restricción UNIQUE de la DB.

        # Actualizar el sistema de previsión a través del repositorio
        updated_system = await self.repo.updateForecastSystem(updated_system_data)
        
        return updated_system