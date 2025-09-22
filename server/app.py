# Standard library imports
import os

# Remote library imports
from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource
from werkzeug.exceptions import NotFound

# Local imports
from models import db, Restaurant, Pizza, RestaurantPizza

# Initialize the Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

# Initialize the database and migration
migrate = Migrate(app, db)
db.init_app(app)

# Initialize the API
api = Api(app)


@app.route('/')
def index():
    return '<h1>Pizza Restaurants</h1>'


# Define the Resources
class RestaurantsResource(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        return jsonify([restaurant.to_dict() for restaurant in restaurants])


class RestaurantByIdResource(Resource):
    def get(self, id):
        restaurant = db.session.get(Restaurant, id)
        if restaurant:
            return jsonify(restaurant.to_dict(include_pizzas=True))
        else:
            return make_response(jsonify({"error": "Restaurant not found"}), 404)

    def delete(self, id):
        restaurant = db.session.get(Restaurant, id)
        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
            return make_response("", 204)
        else:
            return make_response(jsonify({"error": "Restaurant not found"}), 404)


class PizzasResource(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return jsonify([pizza.to_dict() for pizza in pizzas])


class RestaurantPizzasResource(Resource):
    def post(self):
        data = request.get_json()
        price = data.get('price')
        pizza_id = data.get('pizza_id')
        restaurant_id = data.get('restaurant_id')

        try:
            # Check if restaurant and pizza exist
            pizza = db.session.get(Pizza, pizza_id)
            restaurant = db.session.get(Restaurant, restaurant_id)

            if not pizza or not restaurant:
                # The postman collection test might not fail on this, but it's good practice.
                return make_response(jsonify({"errors": ["Restaurant or Pizza not found"]}), 400)

            new_restaurant_pizza = RestaurantPizza(
                price=price,
                pizza_id=pizza_id,
                restaurant_id=restaurant_id
            )
            db.session.add(new_restaurant_pizza)
            db.session.commit()

            return make_response(jsonify(new_restaurant_pizza.to_dict_with_relationships()), 201)

        except ValueError as e:
            return make_response(jsonify({"errors": ["validation errors"]}), 400)
        except Exception as e:
            return make_response(jsonify({"errors": ["An unexpected error occurred"]}), 400)


# Add the resources to the API
api.add_resource(RestaurantsResource, '/restaurants')
api.add_resource(RestaurantByIdResource, '/restaurants/<int:id>')
api.add_resource(PizzasResource, '/pizzas')
api.add_resource(RestaurantPizzasResource, '/restaurant_pizzas')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
