from sellfast import app
from flask import Flask, request, jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from sellfast.models import User, Product
from sellfast.helper import send_sms
import uuid


@app.route("/")
def index():
    return '<h1>Hello World</h1>'

@app.route('/user', methods=['GET'])
def get_all_users():

    users = User.query.all()

    output = []

    for user in users:
        user_data = {}
        # left hand side = new dict, right hand side = from database
        user_data['public_id'] = user.public_id
        user_data['name'] = user.name
        user_data['password'] = user.password
        output.append(user_data)

    return jsonify({'users' : output})

@app.route('/user/<public_id>', methods=['GET'])
def get_one_user(public_id):

    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({'message' : 'No user found!'})

    user_data = {}
    user_data['public_id'] = user.public_id
    user_data['name'] = user.name
    user_data['password'] = user.password

    return jsonify ({'user' : user_data})


@app.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()

    hashed_password = generate_password_hash(data['password'], method='sha256')

    new_user = User(
        public_id=str(uuid.uuid4()),
        name=data['name'], 
        password=hashed_password, 
        )
    db.session.add(new_user)
    db.session.commit()
   
    response = jsonify({'message' : 'New user created!'})
    send_sms()

    return response


@app.route('/user/<public_id>', methods=['DELETE'])
@token_required
def delete_user(current_user, public_id):

    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({'message' : 'No user found!'})
    
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User has been deleted!'})

