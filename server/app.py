#!/usr/bin/env python3
from flask import Flask, request, jsonify
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
import os

# Setting up database
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

# Initialize migration and DB
migrate = Migrate(app, db)
db.init_app(app)

# Route for testing
@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

# API Routes

@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    try:
        restaurants = [restaurant.to_dict(only=['id','name','address']) for restaurant in Restaurant.query.all()]
        if not restaurants:
            return jsonify({'error': 'No restaurants found'}), 404  # Handle no results found
        return jsonify(restaurants)
    except Exception as e:
        return jsonify({'error': str(e), 'message': 'Failed to retrieve restaurants'}), 500

@app.route('/restaurants/<int:id>', methods=['GET'])
def get_restaurant(id):
    try:
        restaurant = db.session.get(Restaurant,id)
        if not restaurant:
            return jsonify({'error': 'Restaurant not found'}), 404
        return jsonify(restaurant.to_dict())
    except Exception as e:
        return jsonify({'error': str(e), 'message': 'Failed to retrieve the restaurant'}), 200

@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    try:
        restaurant = db.session.get(Restaurant,id)
        if not restaurant:
            return jsonify({'error': 'Restaurant not found'}), 404
        db.session.delete(restaurant)
        db.session.commit()
        return '', 204
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    try:
        pizzas = [pizza.to_dict(only=['id','name','ingredients']) for pizza in Pizza.query.all()]
        if not pizzas:
            return jsonify({'error': 'No pizzas found'}), 404  # Handle no results found
        return jsonify(pizzas)
    except Exception as e:
        return jsonify({'error': str(e), 'message': 'Failed to retrieve pizzas'}), 200

@app.route('/restaurant_pizzas', methods=['POST','GET'])
def create_restaurant_pizza():
    if request.method=='POST':
        data = request.get_json()
        try:
            # Ensure price is passed and within valid range
            price = data.get('price')
            if price is None:
                return jsonify({'errors': ['Price required']}), 400
            if not (1 <= price <= 30):
                return jsonify({'errors': ['validation errors']}), 400

            # Ensure pizza_id and restaurant_id are also passed
            pizza_id = data.get('pizza_id')
            restaurant_id = data.get('restaurant_id')
            
            if not pizza_id or not restaurant_id:
                return jsonify({'errors': ['Pizza ID and Restaurant ID are required']}), 400

            # Try to insert the new restaurant_pizza record
            restaurant_pizza = RestaurantPizza(
                price=price,
                pizza_id=int(pizza_id),
                restaurant_id=restaurant_id
            )
            db.session.add(restaurant_pizza)
            db.session.commit()
            return jsonify(restaurant_pizza.to_dict()), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'errors': [str(e)]}), 400
    if request.method == 'GET':
        rp=[rp.to_dict() for rp in RestaurantPizza.query.all()]
        return rp
if __name__ == '__main__':
    app.run(port=5000, debug=True)
