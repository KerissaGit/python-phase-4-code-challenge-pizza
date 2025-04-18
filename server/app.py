#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)
api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


class Restaurants(Resource):
    def get(self):
        try:
            restaurants = [restaurant.to_dict() for restaurant in Restaurant.query.all()]
            return make_response(restaurants, 200)
        except Exception as e:
            return make_response({"error": str(e)}, 500)


class RestaurantById(Resource):
    def get(self, id):
        try:
            restaurant = db.session.get(Restaurant, id)
            if not restaurant:
                return make_response({"error": "Restaurant not found"}, 404)
            return make_response(restaurant.to_dict(rules=("restaurant_pizzas",)), 200)
        except Exception as e:
            return make_response({"error": str(e)}, 500)

    def delete(self, id):
        try:
            restaurant = db.session.get(Restaurant, id)
            if not restaurant:
                return make_response({"error": "Restaurant not found"}, 404)
            db.session.delete(restaurant)
            db.session.commit()
            return make_response("", 204)
        except Exception as e:
            return make_response({"error": str(e)}, 500)


class MostExpensivePizzas(Resource):
    def get(self):
        try:
            pizzas = db.session.query(Pizza).join(RestaurantPizza).order_by(RestaurantPizza.price.desc()).limit(3).all()
            return make_response([pizza.to_dict() for pizza in pizzas], 200)
        except Exception as e:
            return make_response({"error": str(e)}, 500)


class RestaurantSpecificPizza(Resource):
    def get(self, pizza_id):
        try:
            restaurants = Restaurant.query.join(RestaurantPizza).filter(RestaurantPizza.pizza_id == pizza_id).all()
            result = [restaurant.to_dict() for restaurant in restaurants]
            return make_response(result, 200)
        except Exception as e:
            return make_response({"error": str(e)}, 500)


class PizzasAtRestaurant(Resource):
    def get(self, id):
        try:
            pizzas = db.session.query(Pizza).join(RestaurantPizza).filter(RestaurantPizza.restaurant_id == id).all()
            result = [pizza.to_dict() for pizza in pizzas]
            return make_response(result, 200)
        except Exception as e:
            return make_response({"error": str(e)}, 500)


class Pizzas(Resource):
    def get(self):
        try:
            pizzas = [pizza.to_dict(rules=("-restaurant_pizzas",)) for pizza in Pizza.query.all()]
            return make_response(pizzas, 200)
        except Exception as e:
            return make_response({"error": str(e)}, 500)


class RestaurantPizzas(Resource):
    def post(self):
        try:
            data = request.get_json()
            price = data.get("price")
            pizza_id = data.get("pizza_id")
            restaurant_id = data.get("restaurant_id")

            if price is None or pizza_id is None or restaurant_id is None:
                return make_response({"errors": ["validation errors"]}, 400)

            restaurant_pizza = RestaurantPizza(
                price=price,
                pizza_id=pizza_id,
                restaurant_id=restaurant_id
            )
            db.session.add(restaurant_pizza)
            db.session.commit()

            response_data = restaurant_pizza.to_dict(rules=("restaurant", "pizza",))
            return make_response(response_data, 201)
        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)
        except Exception as e:
            return make_response({"errors": ["validation errors"]}, 400)



# Add routes
api.add_resource(Restaurants, "/restaurants")
api.add_resource(RestaurantById, "/restaurants/<int:id>")
api.add_resource(MostExpensivePizzas, '/pizzas/most_expensive')
api.add_resource(RestaurantSpecificPizza, "/restaurants/<int:pizza_id>/restaurants")
api.add_resource(PizzasAtRestaurant, "/restaurants/<int:id>/pizzas")
api.add_resource(Pizzas, "/pizzas")
api.add_resource(RestaurantPizzas, "/restaurant_pizzas")


if __name__ == "__main__":
    app.run(port=5555, debug=True)
