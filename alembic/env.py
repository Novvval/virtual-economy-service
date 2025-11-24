from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

from src.infrastructure.db.orm import metadata, init_mappers

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = metadata

def include_object(object, name, type_, reflected, compare_to):
    print(f"Object: {name}, Type: {type_}, Reflected: {reflected}")  # Debug output
    if type_ == "table":
        return name in ["user", "product", "inventory", "transaction"]
    return True



def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, include_object=include_object)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    init_mappers()
    run_migrations_offline()
else:
    init_mappers()
    run_migrations_online()
