import pytest
from datetime import date
from app.contracts.domain.models import Contract

def test_contract_model_creation():
    contract = Contract(
        name="Contrato de prueba",
        start_date=date.today(),
        end_date=None
    )

    assert contract.name == "Contrato de prueba"
    assert contract.start_date == date.today()
    assert contract.end_date is None
    assert contract.active is True
    assert contract.id is None