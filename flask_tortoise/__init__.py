from tortoise import Tortoise as OldTortoise, fields

import asyncio
import logging
from inspect import getmembers
from types import ModuleType
from tortoise.log import logger

import typing as t
import click as c

from .models import Model as Model

if t.TYPE_CHECKING:
    from flask import Flask



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

        return None

    async def __init_tortoise(self) -> None:
        await NewTortoise.init(
            config=self.config, 
            config_file=self.config_file, 
            db_url=self.db_uri, 
            modules=self.modules
            )

    def __check_data_type(
        self, 
        pv_data:t.Any, 
        realtype:t.Union[t.Tuple[t.Type], t.Type], 
        var_name:str
        ) -> None:

        if pv_data is None:
            return None

        if not isinstance(pv_data, realtype):
            raise TypeError(f"`{var_name}` config var takes only {realtype.__name__} type data. Got: {type(pv_data).__name__}")

        return None

    def register_tortoise(self) -> None:

        @self.app.before_first_request
        async def init_orm() -> None: 
            await self.__init_tortoise()
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

    def __init__(self, app:t.Optional["Flask"]=None) -> None:\

        self.__available_db_models:list = [] # need to add aeirich models here
        
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
        db_uri:str = app.config["TORTOISE_DATABASE_URI"]
        db_models:t.Union[str, list, tuple, None] = app.config.get("TORTOISE_DATABASE_MODELS", None)
        db_modules:t.Dict[str, t.Iterable[t.Union[str, ModuleType]]] = app.config.get("TORTOISE_DATABASE_MODULES", dict())
        db_config:t.Optional[dict] = app.config.get("TORTOISE_DATABASE_CONFIG", None)
        db_config_file:t.Optional[str] = app.config.get("TORTOISE_DATABASE_CONFIG_FILE", None)
        generate_schemas:bool = app.config.get("TORTOISE_GENERATE_SCHEMAS", False)

        _ = self.__check_data_type(db_uri, str, "TORTOISE_DATABASE_URI")
        _ = self.__check_data_type(db_models, (str, list, tuple), "TORTOISE_DATABASE_MODELS")
        _ = self.__check_data_type(db_modules, dict, "TORTOISE_DATABASE_MODULES")
        _ = self.__check_data_type(db_config, dict, "TORTOISE_DATABASE_CONFIG")
        _ = self.__check_data_type(db_config_file, str, "TORTOISE_DATABASE_CONFIG_FILE")
        _ = self.__check_data_type(generate_schemas, bool, "TORTOISE_GENERATE_SCHEMAS")

        if db_models is not None:
            if isinstance(db_models, str):
                db_models = [db_models]
        
            db_models.extend(self.__available_db_models)

        if db_modules.get("models", None) is not None:
            provided_db_models:t.Optional[list] = db_modules["models"]
            provided_db_models.extend(db_models)
            db_modules["models"] = provided_db_models

        else:
            if len(db_models) < len(self.__available_db_models)+1: 
                db_models.append("__main__")

            db_modules.update({"models": db_models})

        super(Tortoise, self).__init__(
            app,
            config=db_config, 
            config_file=db_config_file, 
            db_uri=db_uri, 
            modules=db_modules, 
            generate_schemas=generate_schemas
            )

        super(Tortoise, self).register_tortoise()

        app.extensions['db'] = self

        _cli = _Cli()

        for member in getmembers(_cli):
            if isinstance(member[1], c.Command):
                app.cli.add_command(member[1])
                
        return None