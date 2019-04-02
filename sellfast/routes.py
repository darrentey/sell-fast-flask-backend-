from sellfast import app
from flask import Flask, request, jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from sellfast.models import User, Product
from sellfast.helper import send_sms
from sellfast import db
import uuid
import datetime
import jwt
from functools import wraps

# to work with the token
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # to pass the token
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message' : 'Token is missing!'})

        # if the token is there
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'message' : 'Token is invalid!'})

        # token is valid and have a user
        return f(current_user, *args, **kwargs)

    return decorated

@app.route("/")
def index():
    return '<h1>Hello World</h1>'

# USERS
@app.route('/user', methods=['GET'])
@token_required
def get_all_users(current_user):

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
@token_required
def get_one_user(current_user, public_id):

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
    # send_sms()

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

@app.route('/login')
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response(
            'Could not verify', 
            401, 
            {'WWW-Authenticate' : 'Basic realm="Login required"'}
            )
    user = User.query.filter_by(name=auth.username).first()

    if not user:
        return jsonify({'message' : 'No user found!'})
    
    # to get token
    if check_password_hash(user.password, auth.password):
        token = jwt.encode({
            'public_id' : user.public_id, 
            'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, 
            app.config['SECRET_KEY']
            )
        return jsonify({'token' : token.decode('UTF-8')})
        
    return make_response(
        'Could not verify', 
        401, 
        {'WWW-Authenticate' : 'Basic realm="Login required"'}
        )

# PRODUCTS

@app.route('/product', methods=['POST'])
@token_required
def create_product(current_user):
    data = request.get_json()

    new_product = Product(
        title = data['title'], 
        description = data['description'], 
        user_id = current_user.id)

    if request.files.get('image_file'):
        file = request.files['image_file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            new_product.image_file = filename
    db.session.add(new_product)
    db.session.commit()

    return jsonify({'message' : 'New product created!'})

@app.route('/product', methods=['GET'])
def get_all_product():

    products = Product.query.all()

    output = []

    if not products:
        return jsonify({'message' : 'No product found!'})

    for product in products:
        product_data = {}
        product_data['id'] = product.id
        product_data['title'] = product.title
        product_data['description'] = product.description
        product_data['date_posted'] = product.date_posted
        product_data['image_file'] = product.image_file

        user = User.query.get(product.user_id)
    
        product_data['user_id'] = user.public_id
        product_data['user_name'] = user.name

        output.append(product_data)

    return jsonify ({'products' : output})

@app.route('/product/<product_id>', methods=['PUT'])
@token_required
def update_product(current_user, product_id):
    # Current data
    product = Product.query.filter_by(id=product_id, user_id=current_user.id).first()

    if not product:
        return jsonify({'message' : 'No product found!'})

    # fetch JSON data to update current data in table
    data = request.get_json()
    product.title = data['title']
    product.description = data['description']

    if request.files.get('image_file'):
        file = request.files['image_file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            product.image_file = filename

    db.session.commit()

    product_data = {}
    product_data['id'] = product.id
    product_data['title'] = product.title
    product_data['description'] = product.description
    product_data['date_posted'] = product.date_posted
    product_data['image_file'] = product.image_file
    product_data['user_id'] = product.user_id

    return jsonify({'message' : 'Product updated!', 'product' : product_data})

@app.route('/product/<product_id>', methods=['DELETE'])
@token_required
def delete_product(current_user, product_id):

    product = Product.query.filter_by(id=product_id, user_id=current_user.id).first()

    if not product:
        return jsonify({'message' : 'No product found!'})
        
    db.session.delete(product)
    db.session.commit()

    return jsonify({'message' : 'Product deleted!'})