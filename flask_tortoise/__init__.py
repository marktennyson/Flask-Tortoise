from tortoise import Tortoise as OldTortoise

import asyncio
import logging
from types import ModuleType
import typing as t
from tortoise.log import logger

from .models import Model as Model


if t.TYPE_CHECKING:
    from flask import Flask


class _RegisterTortoise():
    """
    register the flask app and the other configs with the tortoise instance.
    """
    def __init__(self) -> None:
        return None

    def register_tortoise(
        self,
        app: "Flask",
        config: t.Optional[dict] = None,
        config_file: t.Optional[str] = None,
        db_uri: t.Optional[str] = None,
        modules: t.Optional[t.Dict[str, t.Iterable[t.Union[str, ModuleType]]]] = None,
        generate_schemas: bool = False,
    ) -> None:
        """
        Registers ``before_first_request`` hooks to set-up the Tortoise-ORM
        inside a Flask service.
        It also registers a CLI command ``generate-schemas`` that will generate the schemas.

        You can configure using only one of ``config``, ``config_file``
        and ``(db_uri, modules)``.

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
        db_uri:
            Use a DB_URI string. See :ref:`db_uri`
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

        @app.before_first_request
        async def init_orm() -> None: 
            await Tortoise.init(config=config, config_file=config_file, db_url=db_uri, modules=modules)
            logger.info("Tortoise-ORM started, %s, %s", Tortoise._connections, Tortoise.apps)
            if _generate_schemas:
                logger.info("Tortoise-ORM generating schema")
                await Tortoise.generate_schemas()


        @app.cli.command("generate-schemas") 
        def generate_schemas() -> None: 
            """Populate DB with Tortoise-ORM schemas."""

            async def clier() -> None:
                await Tortoise.init(
                    config=config, config_file=config_file, db_url=db_uri, modules=modules
                )
                await Tortoise.generate_schemas()
                await Tortoise.close_connections()

            logger.setLevel(logging.DEBUG)
            loop = asyncio.get_event_loop()
            loop.run_until_complete(clier())

class Tortoise(OldTortoise):
    """
    base inherited class.
    """

class FlaskTortoise(_RegisterTortoise):
    """
    initialize the FlaskTortoise class.
    :param app: 
        the Flask application
    """

    def __init__(self, app:t.Optional["Flask"]=None) -> None:
        
        if app is not None:
            self.init_app(app)
        
        return None

    def init_app(self, app:"Flask") -> None:
        """
        initialize the flask.Flask app instance with 
        the flask_tortoise.FlaskTortoise instance.

        :param app: 
            the Flask application
        """
        db_uri = app.config["TORTOISE_DATABASE_URI"]
        db_models = app.config.get("TORTOISE_DATABASE_MODELS", {})
        generate_schemas:bool = app.config.get("TORTOISE_GENERATE_SCHEMAS", False)
        self.register_tortoise(app, db_uri=db_uri, modules=db_models, generate_schemas=generate_schemas)
        return None

    def get_module_name(self) -> str:
        return 