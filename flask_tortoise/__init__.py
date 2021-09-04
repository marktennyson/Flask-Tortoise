import typing as t
from tortoise import Tortoise as OldTortoise

if t.TYPE_CHECKING:
    from flask import Flask


class Tortoise(OldTortoise):
    """
    base inherited class.
    """

class FlaskTortoise:
    """
    initialize the FlaskTortoise class.
    :param app: 
        the Flask application
    """
    def __init__(self, app:t.Optional["Flask"]=None) -> None:
        
        if app is not None:
            self.init_app(app)

    def init_app(self, app:"Flask") -> None:
        """
        initialize the flask.Flask app instance with 
        the flask_tortoise.FlaskTortoise instance.
        """
        db_uri = app.config["TORTOISE_DATABASE_URI"]