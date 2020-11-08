from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.dialects.postgresql import UUID
import uuid

from server import db


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
                   unique=True, nullable=False)
    email = db.Column(db.String(50), index=True, unique=True, nullable=False)
    first_name = db.Column(db.String(64), index=True, nullable=False)
    last_name = db.Column(db.String(64), index=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    recipes = db.relationship('Recipe', backref='author', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.first_name} {self.last_name}>'

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


recipe_ing = db.Table(
    'recipe_ing',
    db.Column('recipe_id', UUID(as_uuid=True), db.ForeignKey('recipe.id'),
              primary_key=True),
    db.Column('ingredient_id', UUID(as_uuid=True),
              db.ForeignKey('ingredient.id'), primary_key=True)
)


class Recipe(db.Model):
    __tablename__ = 'recipe'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
                   unique=True, nullable=False)
    name = db.Column(db.String(40), nullable=False)
    preparation = db.Column(db.String())
    rating = db.Column(db.Float(), default=0)
    num_of_ratings = db.Column(db.Integer(), default=0)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'),
                        nullable=False)
    num_of_ingredients = db.Column(db.Integer())
    ingredients = db.relationship('Ingredient', secondary=recipe_ing,
                                  back_populates='recipes', lazy='dynamic')

    def __repr__(self):
        return f'<Recipe {self.name}>'


class Ingredient(db.Model):
    __tablename__ = 'ingredient'

    id = db.Column(UUID(as_uuid=True),
                   primary_key=True,
                   default=uuid.uuid4,
                   unique=True, nullable=False)
    name = db.Column(db.String(60), nullable=False, unique=True)
    recipes = db.relationship('Recipe', secondary=recipe_ing,
                              back_populates='ingredients', lazy='dynamic')

    def __repr__(self):
        return f'<Ingredient {self.name}>'


# Token helper model
class TokenBlacklist(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
                   unique=True, nullable=False)
    jti = db.Column(db.String(36), nullable=False)
    token_type = db.Column(db.String(10), nullable=False)
    user_identity = db.Column(db.String(50), nullable=False)
    revoked = db.Column(db.Boolean, nullable=False)
    expires = db.Column(db.DateTime, nullable=False)

    def to_dict(self):
        return {
            'token_id': self.id,
            'jti': self.jti,
            'token_type': self.token_type,
            'user_identity': self.user_identity,
            'revoked': self.revoked,
            'expires': self.expires
        }
