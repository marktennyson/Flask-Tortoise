from tortoise import Tortoise as OldTortoise

import asyncio as aio
import logging as logging
from types import ModuleType
from tortoise.log import logger

import typing as t

from .models import (
    Model as Model,
    Manager as Manager,
    )
from .fields import (
    CASCADE, 
    RESTRICT, 
    SET_DEFAULT, 
    SET_NULL, 
    Field,
    BigIntField,
    BinaryField,
    BooleanField,
    CharEnumField,
    CharField,
    DateField,
    DatetimeField,
    DecimalField,
    FloatField,
    IntEnumField,
    IntField,
    JSONField,
    SmallIntField,
    TextField,
    TimeDeltaField,
    UUIDField,
    BackwardFKRelation,
    BackwardOneToOneRelation,
    ForeignKeyField,
    ForeignKeyRelation,
    ManyToManyField,
    ManyToManyRelation,
    OneToOneField,
    OneToOneRelation,
    ReverseRelation,
)
from .queryset import (
    Pagination as Pagination,
    QuerySet as QuerySet,
)

if t.TYPE_CHECKING:
    from tortoise.fields.data import CharEnumType, IntEnumType
    from flask import Flask


__all__:t.Tuple[str] = (
    "Model",
    "Manager",
    "Pagination",
    "QuerySet",
    "Tortoise",
)


class ConfigureModelAndFields(object):
    """
    This is the base class to configure the 
    `Model` and `Fields` with the db instance.
    """

    CASCADE = CASCADE
    SET_NULL = SET_NULL
    SET_DEFAULT = SET_DEFAULT
    RESTRICT = RESTRICT
    OneToOneRelation = OneToOneRelation
    ForeignKeyRelation = ForeignKeyRelation

    class Model(Model):
        ...

    class Field(Field):
        ...

    class BigIntField(BigIntField):
        ...
    
    class BinaryField(BinaryField):
        ...

    class BooleanField(BooleanField):
        ...

    @staticmethod
    def CharEnumField(
        enum_type: t.Type["CharEnumType"],
        description: t.Optional[str] = None,
        max_length: int = 0,
        **kwargs: t.Any,
    ) -> "CharEnumType":
        """
        Char Enum Field

        A field representing a character enumeration.

        **Warning**: If ``max_length`` is not specified or equals to zero, the size of represented
        char fields is automatically detected. So if later you update the enum, you need to update your
        table schema as well.

        **Note**: Valid str value of ``enum_type`` is acceptable.

        ``enum_type``:
            The enum class
        ``description``:
            The description of the field. It is set automatically if not specified to a multiline list
            of "name: value" pairs.
        ``max_length``:
            The length of the created CharField. If it is zero it is automatically detected from
            enum_type.

        """

        return CharEnumField(enum_type, description, max_length, **kwargs)
    
    class CharField(CharField):
        ...

    class DateField(DateField):
        ...

    class DatetimeField(DatetimeField):
        ...

    class DecimalField(DecimalField):
        ...

    class FloatField(FloatField):
        ...

    class IntField(IntField):
        ...

    class JSONField(JSONField):
        ...

    class SmallIntField(SmallIntField):
        ...

    class TextField(TextField):
        ...

    class TimeDeltaField(TimeDeltaField):
        ...

    class UUIDField(UUIDField):
        ...

    class BackwardFKRelation(BackwardFKRelation):
        ...

    class BackwardOneToOneRelation(BackwardOneToOneRelation):
        ...

    class ManyToManyRelation(ManyToManyRelation):
        ...

    class ReverseRelation(ReverseRelation):
        ...

    @staticmethod
    def IntEnumField(
        enum_type: t.Type["IntEnumType"],
        description: t.Optional[str] = None,
        **kwargs: t.Any,
        ) -> "IntEnumType":
        """
        Enum Field

        A field representing an integer enumeration.

        The description of the field is set automatically if not specified to a multiline list of
        "name: value" pairs.

        **Note**: Valid int value of ``enum_type`` is acceptable.

        ``enum_type``:
            The enum class
        ``description``:
            The description of the field. It is set automatically if not specified to a multiline list
            of "name: value" pairs.

        """
        return IntEnumField(enum_type, description, **kwargs)


    @staticmethod
    def OneToOneField(
        model_name: str,
        related_name: t.Union[t.Optional[str], t.Literal[False]] = None,
        on_delete: str = CASCADE,
        db_constraint: bool = True,
        **kwargs: t.Any,
    ) -> OneToOneRelation:
        """
        OneToOne relation field.

        This field represents a foreign key relation to another model.

        See :ref:`one_to_one` for usage information.

        You must provide the following:

        ``model_name``:
            The name of the related model in a :samp:`'{app}.{model}'` format.

        The following is optional:

        ``related_name``:
            The attribute name on the related model to reverse resolve the foreign key.
        ``on_delete``:
            One of:
                ``models.CASCADE``:
                    Indicate that the model should be cascade deleted if related model gets deleted.
                ``models.RESTRICT``:
                    Indicate that the related model delete will be restricted as long as a
                    foreign key points to it.
                ``models.SET_NULL``:
                    Resets the field to NULL in case the related model gets deleted.
                    Can only be set if field has ``null=True`` set.
                ``models.SET_DEFAULT``:
                    Resets the field to ``default`` value in case the related model gets deleted.
                    Can only be set is field has a ``default`` set.
        ``to_field``:
            The attribute name on the related model to establish foreign key relationship.
            If not set, pk is used
        ``db_constraint``:
            Controls whether or not a constraint should be created in the database for this foreign key.
            The default is True, and that’s almost certainly what you want; setting this to False can be very bad for data integrity.
        """

        return OneToOneField(
            model_name, related_name, on_delete, db_constraint=db_constraint, **kwargs
        )


    @staticmethod
    def ForeignKeyField(
        model_name: str,
        related_name: t.Union[t.Optional[str], t.Literal[False]] = None,
        on_delete: str = CASCADE,
        db_constraint: bool = True,
        **kwargs: t.Any,
    ) -> ForeignKeyRelation:
        """
        ForeignKey relation field.

        This field represents a foreign key relation to another model.

        See :ref:`foreign_key` for usage information.

        You must provide the following:

        ``model_name``:
            The name of the related model in a :samp:`'{app}.{model}'` format.

        The following is optional:

        ``related_name``:
            The attribute name on the related model to reverse resolve the foreign key.
        ``on_delete``:
            One of:
                ``models.CASCADE``:
                    Indicate that the model should be cascade deleted if related model gets deleted.
                ``models.RESTRICT``:
                    Indicate that the related model delete will be restricted as long as a
                    foreign key points to it.
                ``models.SET_NULL``:
                    Resets the field to NULL in case the related model gets deleted.
                    Can only be set if field has ``null=True`` set.
                ``models.SET_DEFAULT``:
                    Resets the field to ``default`` value in case the related model gets deleted.
                    Can only be set is field has a ``default`` set.
        ``to_field``:
            The attribute name on the related model to establish foreign key relationship.
            If not set, pk is used
        ``db_constraint``:
            Controls whether or not a constraint should be created in the database for this foreign key.
            The default is True, and that’s almost certainly what you want; setting this to False can be very bad for data integrity.
        """
        return ForeignKeyField(
        model_name, related_name, on_delete, db_constraint=db_constraint, **kwargs
    )

    
    @staticmethod
    def ManyToManyField(
        model_name: str,
        through: t.Optional[str] = None,
        forward_key: t.Optional[str] = None,
        backward_key: str = "",
        related_name: str = "",
        on_delete: str = CASCADE,
        db_constraint: bool = True,
        **kwargs: t.Any,
    ) -> "ManyToManyRelation":
        """
        ManyToMany relation field.

        This field represents a many-to-many between this model and another model.

        See :ref:`many_to_many` for usage information.

        You must provide the following:

        ``model_name``:
            The name of the related model in a :samp:`'{app}.{model}'` format.

        The following is optional:

        ``through``:
            The DB table that represents the through table.
            The default is normally safe.
        ``forward_key``:
            The forward lookup key on the through table.
            The default is normally safe.
        ``backward_key``:
            The backward lookup key on the through table.
            The default is normally safe.
        ``related_name``:
            The attribute name on the related model to reverse resolve the many to many.
        ``db_constraint``:
            Controls whether or not a constraint should be created in the database for this foreign key.
            The default is True, and that’s almost certainly what you want; setting this to False can be very bad for data integrity.
        ``on_delete``:
            One of:
                ``models.CASCADE``:
                    Indicate that the model should be cascade deleted if related model gets deleted.
                ``models.RESTRICT``:
                    Indicate that the related model delete will be restricted as long as a
                    foreign key points to it.
                ``models.SET_NULL``:
                    Resets the field to NULL in case the related model gets deleted.
                    Can only be set if field has ``null=True`` set.
                ``models.SET_DEFAULT``:
                    Resets the field to ``default`` value in case the related model gets deleted.
                    Can only be set is field has a ``default`` set.
        """

        return ManyToManyField(  # type: ignore
            model_name,
            through,
            forward_key,
            backward_key,
            related_name,
            on_delete=on_delete,
            db_constraint=db_constraint,
            **kwargs,
        )


class Tortoiser(OldTortoise):
    """
    base Tortoise class inherited from `tortoise.Tortoise`
    Please inherit this class and override the default 
    methods to perform the changes related 
    to the base `Tortoise` class.
    """

class ConnectTortoise(object):
    """
    intialize the tortoise orm as 
    context(`with` statement) of the instance
    of flask_tortoise.Tortoise class.

    :param initializer:
        A dictionary type data contains the 
        initial params for tortoise.Tortoise.init method.

    :for example::

        db = Tortoise(app)
        async with db.connect():
            # --do stuffs here--
            ...
    """
    def __init__(self, initializer:t.Dict[str, t.Any]) -> None:
        self.initializer = initializer
    
    async def __aenter__(self):
        await Tortoiser.init(**self.initializer)

    async def __aexit__(self, *wargs, **kwargs):
        await Tortoiser.close_connections()
        

class _Tortoise(object):
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

        self.aerich_config = {
            "connections": {"default": self.db_uri},
            "apps": {
                "models": {
                    "models": self.modules['models'],
                    "default_connection": "default",
                },
            },
        }

        return None

    def _get_kwargs_for_tortoise_initialization(self) -> t.Dict[str, t.Any]:
        kwargs = dict(
            config=self.config, 
            config_file=self.config_file, 
            db_url=self.db_uri, 
            modules=self.modules
        )
        return kwargs

    async def init_tortoise(self, initializer:t.Optional[t.Dict[str, t.Any]]=None) -> None:
        """
        initialize the tortoise orm.
        """
        kwargs = initializer or self._get_kwargs_for_tortoise_initialization()
        await Tortoiser.init(**kwargs)

    def __check_data_type(
        self, 
        pv_data:t.Any, 
        realtype:t.Union[t.Tuple[type], type], 
        var_name:str,
        required:bool=False
        ) -> None:

        if pv_data is None:
            if required is True:
                raise ValueError(f"`{var_name}` config var can't be None. Please set a {realtype.__name__} type value for it.")
            else:
                return None

        if not isinstance(pv_data, realtype):
            raise TypeError(f"`{var_name}` config var takes only {realtype.__name__ if isinstance(realtype, type) else [rt.__name__ for rt in realtype]} type data. Got: {type(pv_data).__name__}")

        return None

    def connect(self, initializer:t.Optional[t.Dict[str, t.Any]]=None) -> "ConnectTortoise":
        """
        the Tortoise-ORM connection context.

        :param initializer:
        A dictionary type data contains the 
        initial params for tortoise.Tortoise.init method.

        :for example::

            db = Tortoise(app)
            
            async with db.connect():
                # --do stuffs here--
                ...

        """
        tortoise_initializer_kwargs = initializer or self._get_kwargs_for_tortoise_initialization()
        return ConnectTortoise(tortoise_initializer_kwargs)

    def register_tortoise(self) -> None:

        @self.app.before_request
        async def init_orm() -> None: 
            await self.init_tortoise()
            logger.info("Tortoise-ORM started, %s, %s", Tortoiser._connections, Tortoiser.apps)
            if self._generate_schemas:
                logger.info("Tortoise-ORM generating schema")
                await Tortoiser.generate_schemas()

        @self.app.teardown_request
        async def close_orm(*wargs, **kwargs):
            await Tortoiser.close_connections()
            logger.info("Tortoise-ORM shutdown")

    def register_cli_interface(self):
        from .cli import tortoise 
        self.app.cli.add_command(tortoise)


class Tortoise(_Tortoise, ConfigureModelAndFields):
    """
    initialize the Tortoise class.
    :param app: 
        the Flask application
    """
    __available_db_models:list = ["aerich.models"] # add custom models here.

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
        db_uri:str = app.config.get("TORTOISE_ORM_DATABASE_URI", None)
        db_models:t.Union[str, list, tuple] = app.config.get("TORTOISE_ORM_MODELS", app.import_name)
        db_modules:t.Dict[str, t.Iterable[t.Union[str, ModuleType]]] = app.config.get("TORTOISE_ORM_MODULES", dict())
        db_config:t.Optional[dict] = app.config.get("TORTOISE_ORM_CONFIG", None)
        db_config_file:t.Optional[str] = app.config.get("TORTOISE_ORM_CONFIG_FILE", None)
        generate_schemas:bool = app.config.get("TORTOISE_ORM_GENERATE_SCHEMAS", False)

        _ = self.__check_data_type(db_uri, str, "TORTOISE_ORM_DATABASE_URI", True)
        _ = self.__check_data_type(db_models, (str, list, tuple), "TORTOISE_ORM_MODELS")
        _ = self.__check_data_type(db_modules, dict, "TORTOISE_ORM_MODULES")
        _ = self.__check_data_type(db_config, dict, "TORTOISE_ORM_CONFIG")
        _ = self.__check_data_type(db_config_file, str, "TORTOISE_ORM_CONFIG_FILE")
        _ = self.__check_data_type(generate_schemas, bool, "TORTOISE_ORM_GENERATE_SCHEMAS")

        if db_models is not None:
            if isinstance(db_models, str):
                db_models:t.List[str] = [db_models]
        
            db_models.extend(self.__available_db_models)

        if db_modules.get("models", None) is not None:
            provided_db_models:t.Optional[list] = db_modules["models"]
            provided_db_models.extend(db_models)
            db_modules["models"] = provided_db_models

        else:
            db_modules["models"] = db_models

        super(Tortoise, self).__init__(
            app,
            config=db_config, 
            config_file=db_config_file, 
            db_uri=db_uri, 
            modules=db_modules, 
            generate_schemas=generate_schemas
            )
        
        super(Tortoise, self).register_tortoise()
        super(Tortoise, self).register_cli_interface()

        app.extensions['tortoise'] = self
                
        return None


    def generate_schemas(self):
        """
        generate the database schemas 
        with application context.

        :for example::

            from app import app
            from models import db

            with app.app_context():
                db.generate_schemas()
        """
        async def generator() -> None:
            await self.init_tortoise()
            await Tortoiser.generate_schemas()
            await Tortoiser.close_connections()

        logger.setLevel(logging.DEBUG)
        loop = aio.get_event_loop()
        loop.run_until_complete(generator())

    def remove_schemas(self) -> None:
        """
        remove(drop) all the created schemas.
        :for example::

            db.remove_schemas()

        """
        async def remover():
            await self.init_tortoise()
            await Tortoiser._drop_databases()
            await Tortoiser.close_connections()
        
        logger.setLevel(logging.DEBUG)
        loop = aio.get_event_loop()
        loop.run_until_complete(remover())