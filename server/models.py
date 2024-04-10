from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates, relationship
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)


class Hero(db.Model, SerializerMixin):
    __tablename__ = 'heroes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    super_name = db.Column(db.String)

    powers = relationship('Power', secondary='hero_powers', back_populates='heroes')
    hero_powers = relationship('HeroPower', back_populates='hero', cascade='all, delete')

    serialize_rules = ('-hero_powers',)

    def __repr__(self):
        return f'<Hero {self.id}>'


class Power(db.Model, SerializerMixin):
    __tablename__ = 'powers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)

    heroes = relationship('Hero', secondary='hero_powers', back_populates='powers')
    hero_powers = relationship('HeroPower', back_populates='power', cascade='all, delete')

    serialize_rules = ('-hero_powers',)

    @validates('name')
    def validate_name(self, key, name):
        if not name:
            raise ValueError("Name cannot be empty")
        return name
    
    @validates('description')
    def validate_description(self, key, description):
        if not description:
            raise ValueError("Description cannot be empty")
        if len(description) < 20:
            raise ValueError("Description must be at least 20 characters long")
        return description

    def __repr__(self):
        return f'<Power {self.id}>'


class HeroPower(db.Model, SerializerMixin):
    __tablename__ = 'hero_powers'

    id = db.Column(db.Integer, primary_key=True)
    strength = db.Column(db.String, nullable=False)
    hero_id = db.Column(db.Integer, db.ForeignKey('heroes.id', ondelete='CASCADE'))
    power_id = db.Column(db.Integer, db.ForeignKey('powers.id', ondelete='CASCADE'))

    hero = relationship('Hero', back_populates='hero_powers')
    power = relationship('Power', back_populates='hero_powers')

    serialize_rules = ('-hero', '-power',)

    @validates('strength')
    def validate_strength(self, key, strength):
        strengths_list = ['Strong', 'Weak', 'Average']
        if strength not in strengths_list:
            raise ValueError("Strength must be 'Strong', 'Weak' or 'Average'")
        return strength

    def __repr__(self):
        return f'<HeroPower {self.id}>'
