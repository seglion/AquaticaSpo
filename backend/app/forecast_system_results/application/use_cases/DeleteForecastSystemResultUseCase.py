from app.forecast_system_results.application.repositories import ForecastSystemResultRepositoryABC
from app.users.domain.models import User # Para manejar permisos

class DeleteForecastSystemResultUseCase:
    """
    Caso de uso para eliminar un resultado de previsión por su ID.
    Solo accesible para administradores.
    """
    def __init__(self, result_repo: ForecastSystemResultRepositoryABC):
        self.result_repo = result_repo

    async def execute(self, result_id: int, requester: User) -> bool:
        # 1. Validación de permisos
        if not requester.is_admin:
            raise PermissionError("Solo los administradores pueden eliminar resultados de previsión.")

        # 2. Intentar eliminar el resultado
        deleted = await self.result_repo.delete_forecast_system_result(result_id)
        if not deleted:
            # Si el repositorio devuelve False, significa que no se encontró el ID.
            raise ValueError(f"Resultado de previsión con ID {result_id} no encontrado para eliminar.")
        
        return deleted