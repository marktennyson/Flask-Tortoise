from flask import Flask
from flask_tortoise import Tortoise, fields


def create_app():
    app = Flask(__name__)
    app.config['TORTOISE_ORM_DATABASE_URI'] = 'sqlite://db.sqlite3'
    return app
    
app = create_app()
db = Tortoise(app)

class User(db.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    is_active = fields.BooleanField(default=True)


@app.get('/')
def index():
    return "hello"



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)