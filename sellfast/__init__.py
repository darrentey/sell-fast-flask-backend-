from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin


app = Flask(__name__)

cors = CORS(app, resources={r"/*":{"origins":"*"}})
app.config['SECRET_KEY'] = 'thisissecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://localhost:5432/backend_sellfast'
db = SQLAlchemy(app)

from sellfast import routes