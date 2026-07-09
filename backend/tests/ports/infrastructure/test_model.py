import pytest
from sqlalchemy import inspect
from app.ports.infrastructure.models import PortORM


def test_has_tablename():
        # Verificar nombre de tabla
    assert PortORM.__tablename__ == 'ports'

def test_has_columns():
    mapper = inspect(PortORM)
    columns = {col.key: col for col in mapper.attrs}
    
    assert 'id' in columns
    assert 'name' in columns
    assert 'country' in columns
    assert 'longitude' in columns
    assert 'latitude' in columns

def test_type_columns():
    mapper = inspect(PortORM)
    columns = {col.key: col for col in mapper.attrs}
    
    id_col = columns['id'].columns[0]
    assert str(id_col.type) == 'INTEGER'
    assert id_col.primary_key is True

    # name, country son Strings y no nulos
    name_col = columns['name'].columns[0]
    assert str(name_col.type) == 'VARCHAR'
    assert name_col.nullable is False

    country_col = columns['country'].columns[0]
    assert str(country_col.type) == 'VARCHAR'
    assert country_col.nullable is False

    # latitude, longitude son Float y no nulos
    lat_col = columns['latitude'].columns[0]
    assert str(lat_col.type) == 'FLOAT'
    assert lat_col.nullable is False

    lon_col = columns['longitude'].columns[0]
    assert str(lon_col.type) == 'FLOAT'
    assert lon_col.nullable is False