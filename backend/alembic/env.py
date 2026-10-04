"""Alembic tracks API revisions only. Django owns all store schema migrations."""

from logging.config import fileConfig

from alembic import context
from app.config import get_settings
from sqlalchemy import create_engine, pool

config = context.config
if config.config_file_name:
    fileConfig(config.config_file_name)
if getattr(config.cmd_opts, "autogenerate", False):
    raise RuntimeError(
        "Store tables are Django-owned. Use Django makemigrations; Alembic autogenerate is disabled."
    )


def offline():
    context.configure(
        url=get_settings().database_url,
        target_metadata=None,
        literal_binds=True,
        version_table="api_alembic_version",
    )
    with context.begin_transaction():
        context.run_migrations()


def online():
    engine = create_engine(get_settings().database_url, poolclass=pool.NullPool)
    try:
        with engine.connect() as connection:
            context.configure(
                connection=connection, target_metadata=None, version_table="api_alembic_version"
            )
            with context.begin_transaction():
                context.run_migrations()
    finally:
        engine.dispose()


if context.is_offline_mode():
    offline()
else:
    online()
