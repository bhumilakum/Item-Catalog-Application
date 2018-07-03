import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from datetime import datetime

# Declaring the Base class
Base = declarative_base()


class User(Base):
    """ Class User contains all information about a user of an application
        such as, user ID as primary key, username, email, picture
    """
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class Category(Base):
    """ Class Category represents all item categories
        it includes, category ID, name, user ID
        here, user_id is foreignkey belongs to the ID of user in User table
    """
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
        }


class Item(Base):
    """ Class Item contains data of an item related with perticular category
        such as, ID, name, image, price etc.
        here, user_id and category_id are foreignkeys belongs to the ID
        of user in User table and category of Category table respectivly
    """
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    description = Column(String(250))
    image = Column(String(250))
    price = Column(Integer)
    created = Column(DateTime)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category, backref='items')
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'category_id': self.category_id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'cerated': self.created
        }


# connect to the database
engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.create_all(engine)
