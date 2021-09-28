"""
provide the database migration system 
for tortoise orm while using it with a 
flask based application. 

This code is purely copied from `aerich.cli`.
And all the credits goes to the author of this great module.
"""

from aerich.exceptions import DowngradeError
from aerich import Command
from aerich.utils import add_src_path
from pathlib import Path
from configparser import ConfigParser
from flask.globals import current_app
from flask.cli import with_appcontext
from nc_console import Console
from functools import wraps
from tortoise import Tortoise

import os as os
import click as c
import typing as t
import asyncio as aio

__all__ = (
    'tortoise',
)

parser = ConfigParser()

CONFIG_DEFAULT_VALUES = {
    "src_folder": ".",
}

class CLIGroup(c.Group):
    """
    inherited `click.Group` class to close the 
    tortoise orm connection after showing the help message.
    """
    async def __torm_connection_closer(self):
        return await Tortoise.close_connections()

    def format_help(self, ctx, formatter):
        try:
            super(CLIGroup, self).format_help(ctx, formatter)

        finally:
            try:
                loop = aio.get_running_loop()
            except RuntimeError:
                loop = aio.get_event_loop()

            loop.run_until_complete(self.__torm_connection_closer())


class CommandGroup(c.Command):
    """
    inherited `click.Command` class to close the 
    tortoise orm connection after showing the help message.
    """
    async def __torm_connection_closer(self):
        return await Tortoise.close_connections()

    def format_help(self, ctx, formatter):
        try:
            super(CommandGroup, self).format_help(ctx, formatter)

        finally:
            try:
                loop = aio.get_running_loop()
            except RuntimeError:
                loop = aio.get_event_loop()

            loop.run_until_complete(self.__torm_connection_closer())


def complete_async_func(f):
    """
    complete the async function and close 
    the tortoise orm connection at the end.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        loop = aio.get_event_loop()

        # Close db connections at the end of all all but the cli group function
        try:
            loop.run_until_complete(f(*args, **kwargs))
        
        except Exception as e:
            
            # if any error occurs during the execution, 
            # this block will close the tortoise orm connection immediately.
            
            loop.run_until_complete(Tortoise.close_connections())
            raise e.__class__(e)

        finally:
            if f.__name__ != "tortoise":
                loop.run_until_complete(Tortoise.close_connections())

    return wrapper


@c.group(context_settings={"help_option_names": ["-h", "--help"]}, cls=CLIGroup)
@c.pass_context
@with_appcontext
@complete_async_func
async def tortoise(ctx: c.Context, config="aerich.ini", app=None, name="aerich"):
    """
    The CLI to control the tortoise-orm.
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
        tortoise_config = current_app.extensions["tortoise"].aerich_config
        app = app or list(tortoise_config.get("apps").keys())[0]
        command = Command(tortoise_config=tortoise_config, app=app, location=location)
        ctx.obj["command"] = command

        if invoked_subcommand != "init-db":
            if not Path(location, app).exists():
                raise c.UsageError("You must exec init-db first", ctx=ctx)
            await command.init()

@tortoise.command('init', help="Initialize the orm.")
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
@complete_async_func
async def db_init(ctx: c.Context, location, src_folder):
    config_file = ctx.obj["config_file"]
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


@tortoise.command('migrate', help="Generate migrate changes file.", cls=CommandGroup)
@c.option("--name", default="update", show_default=True, help="Migrate name.")
@c.pass_context
@complete_async_func
async def db_migrate(ctx: c.Context, name):
    command = ctx.obj["command"]
    ret = await command.migrate(name)
    if not ret:
        return Console.log.Error("No changes detected")
    Console.log.Success(f"Success migrate {ret}")


@tortoise.command('upgrade', help="Upgrade to specified version.", cls=CommandGroup)
@c.pass_context
@with_appcontext
@complete_async_func
async def db_upgrade(ctx: c.Context):
    command = ctx.obj["command"]
    
    migrated = await command.upgrade()
    if not migrated:
        Console.log.Error("No upgrade items found")
    else:
        for version_file in migrated:
            Console.log.Success(f"Success upgrade {version_file}")


@tortoise.command('downgrade', help="Downgrade to specified version.", cls=CommandGroup)
@c.option(
    "-v",
    "--version",
    default=-1,
    type=int,
    show_default=True,
    help="Specified version, default to last.",
)
@c.option(
    "-d",
    "--delete",
    is_flag=True,
    default=False,
    show_default=True,
    help="Delete version files at the same time.",
)
@c.pass_context
@complete_async_func
async def db_downgrade(ctx: c.Context, version: int, delete: bool):
    command = ctx.obj["command"]
    if Console.input.Boolean("Downgrade is dangerous, which maybe lose your data, are you sure"):
        try:
            files = await command.downgrade(version, delete)

        except DowngradeError as e:
            return Console.log.Error(str(e))

        for file in files:
            Console.log.Success(f"Success downgrade {file}")
    else:
        return Console.log.Error("Aborted!")


@tortoise.command("heads", help="Show current available heads in migrate location.", cls=CommandGroup)
@c.pass_context
@complete_async_func
async def db_heads(ctx: c.Context):
    command = ctx.obj["command"]
    head_list = await command.heads()
    if not head_list:
        return Console.log.Info("No available heads, try migrate first")
    for version in head_list:
        Console.log.Success(version)


@tortoise.command("history", help="List all migrate items.", cls=CommandGroup)
@c.pass_context
@complete_async_func
async def db_history(ctx: c.Context):
    command = ctx.obj["command"]
    versions = await command.history()
    if not versions:
        return Console.log.Info("No history, try migrate")
    for version in versions:
        Console.log.Info(version)


@tortoise.command("init-db", help="Generate schema and generate app migrate location.", cls=CommandGroup)
@c.option(
    "--safe",
    type=bool,
    default=True,
    help="When set to true, creates the table only when it does not already exist.",
    show_default=True,
)
@c.pass_context
@complete_async_func
async def init_db(ctx: c.Context, safe):
    command = ctx.obj["command"]
    app = command.app
    dirname = Path(command.location, app)
    try:
        await command.init_db(safe)
        Console.log.Success(f"Success create app migrate location {dirname}")
        Console.log.Success(f'Success generate schema for app "{app}"')
    except FileExistsError:
        return Console.log.Error(f"Inited {app} already, or delete {dirname} and try again.")


@tortoise.command("inspectdb", help="Introspects the database tables to standard output as TortoiseORM model.", cls=CommandGroup)
@c.option(
    "-t",
    "--table",
    help="Which tables to inspect.",
    multiple=True,
    required=False,
)
@c.pass_context
@complete_async_func
async def db_inspectdb(ctx: c.Context, table: t.List[str]):
    command = ctx.obj["command"]
    await command.inspectdb(table)