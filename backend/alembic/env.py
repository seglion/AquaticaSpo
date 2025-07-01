import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# añade tu carpeta 'app' al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# importa tu Settings y tu Base
from app.shared.config import settings
from app.ports.infrastructure.base import Base
from app.users.infrastructure.base import Base as userBase 
# metadata de tu ORM
from sqlalchemy import MetaData

target_metadata = [Base.metadata, userBase.metadata]

# carga config de alembic.ini
config = context.config
# inyecta URL desde .env
config.set_main_option('sqlalchemy.url', settings.database_url.replace("+asyncpg", ""))

# logging
fileConfig(config.config_file_name)

# función que filtra objetos a migrar
def include_object(object_, name, type_, reflected, compare_to):
    if type_ == "table" and name in ("spatial_ref_sys", "geometry_columns", "geography_columns"):
        return False
    return True

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
            connection=connection,
    target_metadata=target_metadata,
    include_object=include_object
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
                connection=connection,
    target_metadata=target_metadata,
    include_object=include_object
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()