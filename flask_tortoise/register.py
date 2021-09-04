import asyncio
import logging
from types import ModuleType
import typing as t

from tortoise import Tortoise
from tortoise.log import logger

if t.TYPE_CHECKING:
    from flask import Flask


def register_tortoise(
    app: "Flask",
    config: t.Optional[dict] = None,
    config_file: t.Optional[str] = None,
    db_url: t.Optional[str] = None,
    modules: t.Optional[t.Dict[str, t.Iterable[t.Union[str, ModuleType]]]] = None,
    generate_schemas: bool = False,
) -> None:
    """
    Registers ``before_serving`` and ``after_serving`` hooks to set-up and tear-down Tortoise-ORM
    inside a Flask service.
    It also registers a CLI command ``generate_schemas`` that will generate the schemas.

    You can configure using only one of ``config``, ``config_file``
    and ``(db_url, modules)``.

    Parameters
    ----------
    app:
        Flask app.
    config:
        Dict containing config:

        Example
        -------

        .. code-block:: python3

            {
                'connections': {
                    # Dict format for connection
                    'default': {
                        'engine': 'tortoise.backends.asyncpg',
                        'credentials': {
                            'host': 'localhost',
                            'port': '5432',
                            'user': 'tortoise',
                            'password': 'qwerty123',
                            'database': 'test',
                        }
                    },
                    # Using a DB_URL string
                    'default': 'postgres://postgres:qwerty123@localhost:5432/events'
                },
                'apps': {
                    'models': {
                        'models': ['__main__'],
                        # If no default_connection specified, defaults to 'default'
                        'default_connection': 'default',
                    }
                }
            }

    config_file:
        Path to .json or .yml (if PyYAML installed) file containing config with
        same format as above.
    db_url:
        Use a DB_URL string. See :ref:`db_url`
    modules:
        Dictionary of ``key``: [``list_of_modules``] that defined "apps" and modules that
        should be discovered for models.
    generate_schemas:
        True to generate schema immediately. Only useful for dev environments
        or SQLite ``:memory:`` databases

    Raises
    ------
    ConfigurationError
        For any configuration error
    """
    _generate_schemas = generate_schemas

    @app.before_request
    async def init_orm() -> None: 
        await Tortoise.init(config=config, config_file=config_file, db_url=db_url, modules=modules)
        logger.info("Tortoise-ORM started, %s, %s", Tortoise._connections, Tortoise.apps)
        if _generate_schemas:
            logger.info("Tortoise-ORM generating schema")
            await Tortoise.generate_schemas()

    @app.teardown_appcontext
    async def close_orm(*args, **kwargs) -> None: 
        await Tortoise.close_connections()
        logger.info("Tortoise-ORM shutdown")

    @app.cli.command("generate-schemas") 
    def generate_schemas() -> None: 
        """Populate DB with Tortoise-ORM schemas."""

        async def inner() -> None:
            await Tortoise.init(
                config=config, config_file=config_file, db_url=db_url, modules=modules
            )
            await Tortoise.generate_schemas()
            await Tortoise.close_connections()

        logger.setLevel(logging.DEBUG)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(inner())
