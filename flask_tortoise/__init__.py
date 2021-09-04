from tortoise import Tortoise as OldTortoise, fields
from tortoise.models import Model as OldModel

import asyncio
import logging
from inspect import getmembers, isfunction
from types import ModuleType
from tortoise.log import logger

import typing as t
import click as c

if t.TYPE_CHECKING:
    from flask import Flask


class Model(OldModel):
    """
    the base Model class inherited from `tortoise.models.Model`
    """

class Fields():
    def __init__(self) -> None:
        members:t.List[t.Tuple[str, t.Any]] = getmembers(fields)
        for member in members:
            setattr(self, member[0], member[1])
        return None

class ConfigureBase(object):
    class Model(Model):
        ...
    
    fields:"Fields" = Fields()
    
class NewTortoise(OldTortoise):
    """
    base Tortoise class inherited from `tortoise.Tortoise`
    """

class _Cli:
    """
    attach the cli interface with 
    flask app for tortoise orm.
    """
    @c.command('generate-schemas')
    def generate_schemas() -> None: 
        """Populate DB with Tortoise-ORM schemas."""

        async def clier() -> None:
            await NewTortoise.generate_schemas()
            await NewTortoise.close_connections()

        logger.setLevel(logging.DEBUG)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(clier())

class _Tortoise():
    """
    register the flask app and the other configs with the tortoise instance.
    """
    def __init__(
        self,
        app:"Flask",
        config: t.Optional[dict] = None,
        config_file: t.Optional[str] = None,
        db_uri: t.Optional[str] = None,
        modules: t.Optional[t.Dict[str, t.Iterable[t.Union[str, ModuleType]]]] = None,
        generate_schemas: bool = False,
        ) -> None:

        self.app = app
        self.config = config
        self.config_file = config_file
        self.db_uri = db_uri
        self.modules = modules
        self._generate_schemas:bool = generate_schemas
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.__init_tortoise())
        return None

    async def __init_tortoise(self) -> None:
        await NewTortoise.init(
            config=self.config, 
            config_file=self.config_file, 
            db_url=self.db_uri, 
            modules=self.modules
            )

    def register_tortoise(self) -> None:

        @self.app.before_first_request
        async def init_orm() -> None: 
            logger.info("Tortoise-ORM started, %s, %s", NewTortoise._connections, NewTortoise.apps)
            if self._generate_schemas:
                logger.info("Tortoise-ORM generating schema")
                await NewTortoise.generate_schemas()


class Tortoise(_Tortoise, ConfigureBase):
    """
    initialize the Tortoise class.
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
        the flask_tortoise.Tortoise instance.

        :param app: 
            the Flask application
        """
        db_uri = app.config["TORTOISE_DATABASE_URI"]
        db_modules = app.config.get("TORTOISE_DATABASE_MODULES", {"models": ["__main__"]})
        generate_schemas:bool = app.config.get("TORTOISE_GENERATE_SCHEMAS", False)

        super(Tortoise, self).__init__(app, db_uri=db_uri, modules=db_modules, generate_schemas=generate_schemas)
        super(Tortoise, self).register_tortoise()

        app.extensions['db'] = self

        _cli = _Cli()

        for member in getmembers(_cli):
            if isinstance(member[1], c.Command):
                app.cli.add_command(member[1])
                
        return None