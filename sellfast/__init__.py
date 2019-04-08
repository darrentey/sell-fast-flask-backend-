from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin


app = Flask(__name__)

cors = CORS(app, resources={r"/*":{"origins":"*"}})
app.config['SECRET_KEY'] = 'thisissecret'

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://whasfcwduprrmg:da9360d68e47379e46010f6bf5a87467af38c8bcc090fef8bb3d86688dc2ee0f@ec2-23-21-136-232.compute-1.amazonaws.com:5432/dbepq4s7mmbcns'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from sellfast import routes
