#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource
from flask_cors import CORS
from models import db, Hero, Power, HeroPower
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def index():
    return make_response('<h1>Code challenge</h1>', 200)

#Route set-up to get heroes
@app.route('/heroes', methods=['GET'])
def get_heroes():
    heroes = Hero.query.all()
    serialized_heroes = [hero.to_dict(only=('id', 'name', 'super_name')) for hero in heroes]
    response = jsonify(serialized_heroes)
    return make_response(response, 200)
    
# Route set-up to get heroes by id
@app.route('/heroes/<int:id>', methods=['GET'])
def get_hero_by_id(id):
    hero = Hero.query.get(id)
    if hero is None:
        response = jsonify({"error": "Hero not found"})
        return make_response(response, 404)
    
    serialized_hero = hero.to_dict()
    serialized_hero['hero_powers'] = [hero_power.to_dict() for hero_power in hero.hero_powers]
    response = jsonify(serialized_hero)
    return make_response(response, 200)

#Route set-up to get powers
@app.route('/powers', methods=['GET'])
def get_powers():
    powers = Power.query.all()
    serialized_powers = [power.to_dict(only=('id', 'name', 'description')) for power in powers]
    response = jsonify(serialized_powers)
    return make_response(response, 200)

#Route set-up to get power by id
@app.route('/powers/<int:id>', methods=['GET'])
def get_power_by_id(id):
    power = Power.query.get(id)
    if power is None:
        response = jsonify({"error": "Power not found"})
        return make_response(response, 404)
    
    serialized_power = power.to_dict()
    response = jsonify(serialized_power)
    return make_response(response, 200)

#Helper functtion for input validation
def validate_hero_power_data(data):
    errors = []
    if 'hero_id' not in data:
        errors.append("hero_id is required")
    if 'power_id' not in data:
        errors.append("power_id is required")
    if 'strength' in data and data['strength'] not in ["Strong", "Weak", "Average"]:
        errors.append("Strength must be one of: 'Strong', 'Weak', 'Average'")
    if 'description' not in data or not isinstance(data['description'], str) or len(data['description']) < 20:
        errors.append("Description must be a string of at least 20 characters long.")
    return errors

#Route set-up to update power by id
@app.route('/powers/<int:id>', methods=['PATCH'])
def update_power(id):
    power = Power.query.get(id)
    if power is None:
        response = jsonify({"error": "Power not found"})
        return make_response(response, 404)
    
    data = request.json
    new_description = data.get('description')
    
    if new_description is not None and (not isinstance(new_description, str) or len(new_description) < 20):
        response = jsonify({"errors": ["Description must be a string of at least 20 characters long."]})
        return make_response(response, 400)

    if new_description is not None:
        power.description = new_description
    
    """errors = validate_hero_power_data(data)
    if errors:
        response = jsonify({"errors": errors})
        return make_response(response, 400)

    elif new_description is not None:
        power.description = new_description"""
    
    try:
        db.session.commit()
    except Exception as e:
        response = jsonify({"errors": [str(e)]})
        return make_response(response, 400)
    
    serialized_power = power.to_dict()
    response = jsonify(serialized_power)
    return make_response(response, 200)

#Route set-up to create hero-power
@app.route('/hero_powers', methods=['POST'])
def create_hero_power():
    data = request.json
    errors = validate_hero_power_data(data)
    if errors:
        response = jsonify({"errors": errors})
        return make_response(response, 400)

    hero_id = data.get('hero_id')
    power_id = data.get('power_id')
    strength = data.get('strength')

    if strength not in ["Strong", "Weak", "Average"]:
        response = jsonify({"error": "Strength must be either 'Strong', 'Weak' or 'Average'"})
        return make_response(response, 400)
    
    hero = Hero.query.get(hero_id)
    if hero is None:
        response = jsonify({"error": "Hero not found"})
        return make_response(response, 404)
    
    power = Power.query.get(power_id)
    if power is None:
        response = jsonify({"error": "Power not found"})
        return make_response(response, 404)
    
    hero_power = HeroPower(hero_id=hero_id, power_id=power_id, strength=strength)
    db.session.add(hero_power)
    
    try:
        db.session.commit()
    except Exception as e:
        response = jsonify({"errors": [str(e)]})
        return make_response(response, 400)
    
    serialized_hero_power = hero_power.to_dict()
    serialized_hero_power['hero'] = hero.to_dict(only=('id', 'name', 'super_name'))
    serialized_hero_power['power'] = power.to_dict(only=('id', 'name', 'description'))
    
    return make_response(jsonify(serialized_hero_power), 201)

if __name__ == '__main__':
    app.run(port=5555, debug=True)
