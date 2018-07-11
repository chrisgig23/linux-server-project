import sys
import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class Users(Base):
    __tablename__ = 'users'

    name = Column(String(80), nullable = False)
    picture = Column(String(250), nullable = False)
    email = Column(String(250))
    id = Column(Integer, primary_key = True)

    @property
    def serialize(self):
        return {
            'name'      : self.name,
            'picture'   : self.picture,
            'email'     : self.email,
            'id'        : self.id
    }

class Category(Base):
    __tablename__ = 'category'

    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    user_id = Column(Integer, ForeignKey('users.id'))
    users = relationship(Users)

    @property
    def serialize(self):
        return {
            'name'  : self.name,
            'id'    : self.id,
    }

class CategoryItem(Base):
    __tablename__ = 'item'

    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    description = Column(String(250))
    timeAdded = Column(DateTime, default=datetime.datetime.utcnow())
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('users.id'))
    users = relationship(Users)

    @property
    def serialize(self):
        return {
            'name'          : self.name,
            'id'            : self.id,
            'description'   : self.description,
            'timeAdded'     : self.timeAdded
    }

engine = create_engine('postgresql://catalog:password@localhost/catalog')

Base.metadata.create_all(engine)
