# Command Line Interface

## :smile: Introduction

This document describes how to use the command line to make migrations while using __Flask-Tortoise__.
Internally it's using __Aerich__ module to provide the migration support. Special thanks to the author of __Aerich__ module.

## Quick Start

__Flask-Tortoise__ module is connected to the `flask.Flask.cli` click-group. So you can use the command line as same as the other flask extensions. 

```bash
$ flask tortoise --help


Usage: flask tortoise [OPTIONS] COMMAND [ARGS]...

  the default command line interface to manage the version of the tortoise
  orm.

Options:
  -h, --help  Show this message and exit.

Commands:
  downgrade  Downgrade to specified version.
  heads      Show current available heads in migrate location.
  history    List all migrate items.
  init       Initialize the orm.
  init-db    Generate schema and generate app migrate location.
  inspectdb  Introspects the database tables to standard output as...
  migrate    Generate migrate changes file.
  upgrade    Upgrade to specified version.
```

## Usage

#### Initialization

```bash
$ flask tortoise init --help


Usage: flask tortoise init [OPTIONS]

  Init config file and generate root migrate location.

Options:
  -t, --tortoise-orm TEXT  Tortoise-ORM config module dict variable, like settings.TORTOISE_ORM.
                           [required]
  --location TEXT          Migrate store location.  [default: ./migrations]
  -h, --help               Show this message and exit.
```

#### Init DB

```bash
$ flask tortoise init-db


Success create app migrate location ./migrations/models
Success generate schema for app "models"
```
:bulb: __Note:__ If your models not present at the `__main__` file then you must need to pass the models file name at the app config: `TORTOISE_DATABASE_MODLES`.

#### Update models and make migrate
```bash
$ flask tortoise migrate --name drop_column


Success migrate 1_202029051520102929_drop_column.sql
```
Format of migrate filename is {version_num}_{datetime}_{name|update}.sql.

And if it guess you are renaming a column, it will ask Rename {old_column} to {new_column} [True], you can choice True to rename column without column drop, or choice False to drop column then create.

If you use MySQL, only MySQL8.0+ support rename..to syntax.

#### Upgrade to latest version
```bash
$ flask tortoise upgrade


Success upgrade 1_202029051520102929_drop_column.sql
```
Now your db is migrated to latest.

#### Downgrade to specified version
```bash
$ flask tortoise downgrade --help


Usage: flask tortoise downgrade [OPTIONS]

  Downgrade to specified version.

Options:
  -v, --version INTEGER  Specified version, default to last.  [default: -1]
  -d, --delete           Delete version files at the same time.  [default:
                         False]
  -h, --help             Show this message and exit.
```
```bash
$ flask tortoise downgrade


Success downgrade 1_202029051520102929_drop_column.sql
```
Now your db rollback to specified version.

#### Show history

```bash
$ flask tortoise history


1_202029051520102929_drop_column.sql
```

#### Show heads to be migrated
```bash
$ aerich heads


1_202029051520102929_drop_column.sql
```