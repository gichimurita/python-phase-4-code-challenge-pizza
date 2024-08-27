from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy_serializer import SerializerMixin

# Defining metadata with a naming convention
metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

# Initializing the SQLAlchemy instance with custom metadata
db = SQLAlchemy(metadata=metadata)

class Restaurant(db.Model, SerializerMixin):
    __tablename__ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)

    # Relationship with RestaurantPizza
    restaurant_pizzas = db.relationship('RestaurantPizza', backref='restaurant', cascade='all, delete-orphan')
    
    # Serialization rules
    serialize_rules = ('-restaurant_pizzas',)  # Exclude restaurant_pizzas field in serialization

    def __repr__(self):
        return f"<Restaurant {self.name}>"
    
    def to_dict(self, include=None, exclude=None):
        """Convert model instance to a dictionary, including or excluding specified fields."""
        include = include or []
        exclude = exclude or []

        # Convert the model instance to a dictionary of its columns
        result = {c.name: getattr(self, c.name) for c in self.__table__.columns}

        # Include specified relationships if they exist
        for field in include:
            relationship = getattr(self, field, None)
            if relationship is not None:
                # Check if the relationship is a single object or a collection
                if isinstance(relationship, list):
                    result[field] = [item.to_dict() for item in relationship]
                else:
                    result[field] = relationship.to_dict()

        # Exclude specified fields
        for field in exclude:
            result.pop(field, None)

        return result


class Pizza(db.Model, SerializerMixin):
    __tablename__ = "pizzas"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    ingredients = db.Column(db.String, nullable=False)

    # Serialization rules
    serialize_rules = ('-restaurant_pizzas',)  # Exclude restaurant_pizzas field in serialization
    def to_dict(self):
        """Convert model instance to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "ingredients": self.ingredients
        }
   

    def __repr__(self):
        return f"<Pizza {self.name}, {self.ingredients}>"


class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = 'restaurant_pizzas'

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)
    pizza_id = db.Column(db.Integer, db.ForeignKey('pizzas.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)

    # Add validation for the price field
    @validates('price')
    def validate_price(self, key, value):
        if value < 1 or value > 30:
            raise ValueError("Price must be between 1 and 30")
        return value

    def __repr__(self):
        return f"<RestaurantPizza ${self.price}>"
    
    def to_dict(self, include=None, exclude=None):
        """Convert model instance to a dictionary, including or excluding specified fields."""
        include = include or []
        exclude = exclude or []

        result = {c.name: getattr(self, c.name) for c in self.__table__.columns}

        if 'pizza' in include:
            result['pizza'] = self.pizza.to_dict() if self.pizza else None
        if 'restaurant' in include:
            result['restaurant'] = self.restaurant.to_dict() if self.restaurant else None

        for field in exclude:
            if field in result:
                del result[field]

        return result

