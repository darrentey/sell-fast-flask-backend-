from sellfast import app
from sellfast.models import User, Product

@app.route("/")
def index():
    return '<h1>Hello World</h1>'