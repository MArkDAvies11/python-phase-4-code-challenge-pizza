# Standard imports
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy

# Configure the database connection
metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)


# Define the Restaurant model
class Restaurant(db.Model):
    __tablename__ = 'restaurants'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    address = db.Column(db.String)

    # Define the relationship to RestaurantPizza
    restaurant_pizzas = db.relationship(
        'RestaurantPizza', back_populates='restaurant', cascade="all, delete-orphan")
    pizzas = association_proxy('restaurant_pizzas', 'pizza')

    # Serialization rules to prevent recursion
    def to_dict(self, include_pizzas=False):
        data = {
            'id': self.id,
            'name': self.name,
            'address': self.address,
        }
        if include_pizzas:
            data['restaurant_pizzas'] = [
                rp.to_dict() for rp in self.restaurant_pizzas]
        return data

    def __repr__(self):
        return f'<Restaurant {self.name}>'


# Define the Pizza model
class Pizza(db.Model):
    __tablename__ = 'pizzas'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    ingredients = db.Column(db.String)

    # Define the relationship to RestaurantPizza
    restaurant_pizzas = db.relationship(
        'RestaurantPizza', back_populates='pizza')
    restaurants = association_proxy('restaurant_pizzas', 'restaurant')

    # Serialization rules
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'ingredients': self.ingredients,
        }

    def __repr__(self):
        return f'<Pizza {self.name}>'


# Define the RestaurantPizza model (the join table)
class RestaurantPizza(db.Model):
    __tablename__ = 'restaurant_pizzas'

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer)
    restaurant_id = db.Column(db.Integer, db.ForeignKey(
        'restaurants.id', ondelete='CASCADE'))
    pizza_id = db.Column(db.Integer, db.ForeignKey('pizzas.id'))
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    # Define the relationships to Restaurant and Pizza
    restaurant = db.relationship('Restaurant', back_populates='restaurant_pizzas')
    pizza = db.relationship('Pizza', back_populates='restaurant_pizzas')

    # Validation: price must be between 1 and 30
    @validates('price')
    def validate_price(self, key, price):
        if not (1 <= price <= 30):
            raise ValueError("Price must be between 1 and 30")
        return price

    # Serialization rules
    def to_dict(self):
        return {
            'id': self.id,
            'price': self.price,
            'pizza_id': self.pizza_id,
            'restaurant_id': self.restaurant_id,
        }

    # Serialization for the POST route
    def to_dict_with_relationships(self):
        return {
            'id': self.id,
            'price': self.price,
            'pizza_id': self.pizza_id,
            'restaurant_id': self.restaurant_id,
            'pizza': self.pizza.to_dict(),
            'restaurant': self.restaurant.to_dict(),
        }

    def __repr__(self):
        return f'<RestaurantPizza {self.price}>'