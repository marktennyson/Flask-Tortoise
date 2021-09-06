"""
provide the database migration system 
for tortoise orm while using it with a 
flask based application. 

This code is purely copied from `aerich.cli.py`.
And all the credits goes to the author of this greate module.
"""


from aerich.cli import CONFIG_DEFAULT_VALUES, coro, parser
from aerich.utils import add_src_path
from pathlib import Path
from flask.globals import current_app
from flask.cli import with_appcontext
from nc_console import Console

import os as os
import click as c
import typing as t

__all__ = (
    'db_init',
)

TORTOISE_ORM_CONFIG:t.Dict[str, t.Any] = {}

@c.group(context_settings={"help_option_names": ["-h", "--help"]})
@c.pass_context
@coro
async def tortoise(ctx: c.Context, config="aerich.ini", app=None, name="aerich"):
    """
    the default command line interface to manage the version of the tortoise orm.
    """
    ctx.ensure_object(dict)
    ctx.obj["config_file"] = config
    ctx.obj["name"] = name

    invoked_subcommand = ctx.invoked_subcommand
    if invoked_subcommand != "init":

        if not Path(config).exists():
            raise c.UsageError("You must exec init first", ctx=ctx)

        parser.read(config)

        location = parser[name]["location"]
        # tortoise_orm = parser[name]["tortoise_orm"]
        src_folder = parser[name].get("src_folder", CONFIG_DEFAULT_VALUES["src_folder"])
        add_src_path(src_folder)
        tortoise_config = TORTOISE_ORM_CONFIG
        app = app or list(tortoise_config.get("apps").keys())[0]
        command = c.Command(tortoise_config=tortoise_config, app=app, location=location)
        ctx.obj["command"] = command

        if invoked_subcommand != "init-db":
            if not Path(location, app).exists():
                raise c.UsageError("You must exec init-db first", ctx=ctx)
            await command.init()

@tortoise.command('init', help='Init config file and generate root migrate location.')
@c.option(
"-t",
"--tortoise-orm",
# required=True,
help="Tortoise-ORM config module dict variable, like settings.TORTOISE_ORM.",
)
@c.option(
"--location",
default="./migrations",
show_default=True,
help="Migrate store location.",
)
@c.option(
"-s",
"--src_folder",
default=CONFIG_DEFAULT_VALUES["src_folder"],
show_default=False,
help="Folder of the source, relative to the project root.",
)
@c.pass_context
@with_appcontext
@coro
async def db_init(ctx: c.Context, tortoise_orm, location, src_folder):
    config_file = ctx.obj["config_file"]
    global TORTOISE_ORM_CONFIG
    TORTOISE_ORM_CONFIG = current_app.extensions['tortoise'].aerich_config
    name = ctx.obj["name"]
    if Path(config_file).exists():
        return Console.log.Error("Configuration file already created")

    if os.path.isabs(src_folder):
        src_folder = os.path.relpath(os.getcwd(), src_folder)
    # Add ./ so it's clear that this is relative path
    if not src_folder.startswith("./"):
        src_folder = "./" + src_folder

    # check that we can find the configuration, if not we can fail before the config file gets created
    add_src_path(src_folder)
    # get_tortoise_config(ctx, tortoise_orm)

    parser.add_section(name)
    # parser.set(name, "tortoise_orm", "tortoise_orm")
    parser.set(name, "location", location)
    parser.set(name, "src_folder", src_folder)

    with open(config_file, "w", encoding="utf-8") as f:
        parser.write(f)

    Path(location).mkdir(parents=True, exist_ok=True)

    Console.log.Success(f"Successfully created the migrate folder: {location}")
    Console.log.Success(f"Successfully generated the config file: {config_file}")