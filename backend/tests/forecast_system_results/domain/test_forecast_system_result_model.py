# tests/unit/domain/test_forecast_system_result_model.py

import pytest
from datetime import datetime, timezone
from typing import Any, Optional

# Importa el modelo de dominio que estamos probando
from app.forecast_system_results.domain.models import ForecastSystemResult

class TestForecastSystemResultModel:

    @pytest.fixture
    def sample_result_data_point(self) -> dict[str, Any]:
        """Datos de ejemplo para un resultado de tipo 'punto'."""
        return {
            "type": "point",
            "date": "2025-07-07T10:00:00Z",
            "Hs": 2.5,
            "Tp": 8.2,
            "Dir": 180,
            "Nivel": 1.5,
            "Rebase": 0.1
        }

    @pytest.fixture
    def sample_result_data_area(self) -> dict[str, Any]:
        """Datos de ejemplo para un resultado de tipo 'área'."""
        return {
            "type": "area",
            "date": "2025-07-07T10:00:00Z",
            "Hs": 1.8,
            "Tp": 7.1,
            "Nivel": 1.2
        }

    def test_forecast_system_result_creation_minimal(self):
        """
        Verifica la creación básica de un ForecastSystemResult con los campos mínimos.
        """
        now = datetime.now(timezone.utc).replace(microsecond=0) # Usar timezone.utc para consistencia
        result_data = {"key": "value"} # Datos simples para test básico

        result = ForecastSystemResult(
            id=None,
            forecast_zone_id=1,
            execution_date=now,
            result_data=result_data
        )

        assert result.id is None
        assert result.forecast_zone_id == 1
        assert result.execution_date == now
        assert result.result_data == result_data

    def test_forecast_system_result_creation_with_id(self):
        """
        Verifica la creación de un ForecastSystemResult con un ID predefinido.
        """
        now = datetime.now(timezone.utc).replace(microsecond=0)
        result_data = {"status": "completed"}

        result = ForecastSystemResult(
            id=100,
            forecast_zone_id=5,
            execution_date=now,
            result_data=result_data
        )

        assert result.id == 100
        assert result.forecast_zone_id == 5
        assert result.execution_date == now
        assert result.result_data == result_data

    def test_forecast_system_result_data_point_structure(self, sample_result_data_point):
        """
        Verifica que el modelo puede almacenar datos de resultado de 'punto' correctamente.
        """
        now = datetime.now(timezone.utc).replace(microsecond=0)

        result = ForecastSystemResult(
            id=1,
            forecast_zone_id=10,
            execution_date=now,
            result_data=sample_result_data_point
        )

        assert result.result_data["type"] == "point"
        assert result.result_data["Hs"] == 2.5
        assert "Dir" in result.result_data
        assert result.result_data["Rebase"] == 0.1 # Verifica campo opcional

    def test_forecast_system_result_data_area_structure(self, sample_result_data_area):
        """
        Verifica que el modelo puede almacenar datos de resultado de 'área' correctamente.
        """
        now = datetime.now(timezone.utc).replace(microsecond=0)

        result = ForecastSystemResult(
            id=2,
            forecast_zone_id=20,
            execution_date=now,
            result_data=sample_result_data_area
        )

        assert result.result_data["type"] == "area"
        assert result.result_data["Hs"] == 1.8
        assert "Dir" not in result.result_data # Verifica ausencia de campo específico de punto

    def test_forecast_system_result_equality(self):
        """
        Verifica que dos instancias con los mismos atributos son consideradas iguales.
        Los dataclasses generan automáticamente __eq__.
        """
        now = datetime.now(timezone.utc).replace(microsecond=0)
        data = {"metric": 123}

        result1 = ForecastSystemResult(id=1, forecast_zone_id=1, execution_date=now, result_data=data)
        result2 = ForecastSystemResult(id=1, forecast_zone_id=1, execution_date=now, result_data=data)

        assert result1 == result2

    def test_forecast_system_result_inequality(self):
        """
        Verifica que dos instancias con atributos diferentes no son consideradas iguales.
        """
        now = datetime.now(timezone.utc).replace(microsecond=0)
        data1 = {"metric": 123}
        data2 = {"metric": 456}

        result1 = ForecastSystemResult(id=1, forecast_zone_id=1, execution_date=now, result_data=data1)
        result2 = ForecastSystemResult(id=2, forecast_zone_id=1, execution_date=now, result_data=data2)

        assert result1 != result2

    def test_forecast_system_result_attribute_assignment(self):
        """
        Verifica que los atributos de un ForecastSystemResult se pueden modificar.
        """
        result = ForecastSystemResult(id=1, forecast_zone_id=1, execution_date=datetime.now(), result_data={})

        new_date = datetime.now(timezone.utc).replace(microsecond=0)
        new_data = {"updated": True}
        
        result.forecast_zone_id = 2
        result.execution_date = new_date
        result.result_data = new_data

        assert result.forecast_zone_id == 2
        assert result.execution_date == new_date
        assert result.result_data == new_data