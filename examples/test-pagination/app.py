from flask import Flask, jsonify, render_template
from models import *

app = Flask(__name__)

app.config['TORTOISE_DATABASE_URI'] = 'sqlite://db.sqlite3'
app.config['TORTOISE_DATABASE_MODELS'] = "models"

db.init_app(app)

@app.get('/')
async def index():
    posts = await Posts.all()
    return jsonify([dict(id=post.id, name=post.name, body=post.body) for post in posts])

@app.get("/api-1")
async def view():
    page=1
    per_page=10
    posts = await Posts.paginate(page=1, per_page=per_page)
    data = await posts.items
    # data = await posts.items
    # print ("posts.items:", posts)
    # return "none"
    return render_template('view.html',posts=posts, data=data)


def generate_data():
    async def executor():
        with await db.connect():
            for i in range(0, 1000):
                name = f"Post-{i}"
                body = f"This is the post body, NO: {i}"
                _ = await Posts.create(name=name, body=body)
    
    import asyncio as aio
    loop=aio.get_event_loop()
    loop.run_until_complete(executor())
    


if __name__ == '__main__':
    app.run(debug=True, port=5050)