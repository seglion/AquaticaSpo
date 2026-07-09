import pytest
from app.ports.infrastructure.infrastructure import PortRepository
from app.ports.domain.models import Port

@pytest.mark.asyncio
async def test_add_and_get_by_id(session):
    repo = PortRepository(session)

    port_in = Port( name="TestPort", country="TestLand", latitude=12.34, longitude=56.78)
    saved = await repo.create_port(port_in.name, port_in.country, port_in.latitude, port_in.longitude)
    assert saved.id is not None
    assert saved.name == "TestPort"

    fetched = await repo.get_port_by_id(saved.id)
    assert fetched is not None
    assert fetched.id == saved.id

@pytest.mark.asyncio
async def test_list_ports_returns_all(session):
    repo = PortRepository(session)

    # Inserto tres puertos de prueba
    inputs = [
        ("Port A", "Country A", 1.1, 2.2),
        ("Port B", "Country B", 3.3, 4.4),
        ("Port C", "Country C", 5.5, 6.6),
    ]
    saved_ports = []
    for name, country, lat, lon in inputs:
        p = await repo.create_port(name, country, lat, lon)
        saved_ports.append(p)

    # Ahora listamos
    all_ports = await repo.list_ports()

    # Compruebo que los IDs de los insertados están en el listado
    returned_ids = {p.id for p in all_ports}
    expected_ids = {p.id for p in saved_ports}
    assert expected_ids.issubset(returned_ids)

    # Y que todos son instancias de Port
    assert all(isinstance(p, Port) for p in all_ports)