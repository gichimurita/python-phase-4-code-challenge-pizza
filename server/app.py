from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, jsonify, make_response
from flask_restful import Api
import os

# Set up the base directory and database URI
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

# Set up migration and initialize the app with the database
migrate = Migrate(app, db)
db.init_app(app)

# Set up the API
api = Api(app)

# Default route
@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

# Route to get all restaurants
@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify([restaurant.to_dict(exclude=['restaurant_pizzas']) for restaurant in restaurants])

# Route to get a single restaurant by ID
@app.route('/restaurants/<int:id>', methods=['GET'])
def get_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if restaurant:
        return jsonify(restaurant.to_dict(include=['restaurant_pizzas']))
    else:
        return make_response(jsonify({"error": "Restaurant not found"}), 404)


# Route to delete a restaurant by ID
@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if restaurant:
        db.session.delete(restaurant)
        db.session.commit()
        return make_response("", 204)
    else:
        return make_response(jsonify({"error": "Restaurant not found"}), 404)

# Route to get all pizzas
@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    try:
        pizzas = Pizza.query.all()
        print(f"Pizzas retrieved: {pizzas}")  # Debugging print statement
        return jsonify([pizza.to_dict() for pizza in pizzas])
    except Exception as e:
        print(f"Error: {e}")  # Debugging print statement
        return jsonify({"error": str(e)}), 500


# Route to create a new RestaurantPizza
@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    data = request.get_json()
    try:
        # Example validation, adapt to your needs
        if 'price' not in data or 'pizza_id' not in data or 'restaurant_id' not in data:
            raise ValueError("Missing required fields")

        if data['price'] < 1 or data['price'] > 30:
            raise ValueError("Price must be between 1 and 30")

        restaurant_pizza = RestaurantPizza(
            price=data['price'],
            pizza_id=data['pizza_id'],
            restaurant_id=data['restaurant_id']
        )
        db.session.add(restaurant_pizza)
        db.session.commit()
        return jsonify(restaurant_pizza.to_dict()), 201
    except ValueError as e:
        return jsonify({"errors": ["validation errors"]}), 400  # Ensure this matches test expectation
    except Exception as e:
        return jsonify({"errors": [str(e)]}), 500

if __name__ == "__main__":
    app.run(port=5555, debug=True)
