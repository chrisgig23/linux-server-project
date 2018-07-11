from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, CategoryItem

engine = create_engine('postgresql://catalog:password@localhost/catalog')
Base.metadata.bind = create_engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

category1 = Category(name = 'Soccer', user_id=2)

session.add(category1)
session.commit()

categoryItem1 = CategoryItem(name = 'Soccer Cleats', description = 'An item of footwear worn when playing soccer, designed for grass fields with studs on the outsole to aid grip.', category = category1, user_id=2)

session.add(categoryItem1)
session.commit()

categoryItem2 = CategoryItem(name = 'Shin Guards', description = 'Sock inserts to protect the shins from stray kicks', category = category1, user_id=2)

session.add(categoryItem2)
session.commit()

category2 = Category(name = 'Baseball', user_id=2)

session.add(category2)
session.commit()

categoryItem1 = CategoryItem(name = 'Bat', description = 'Made of wood or aluminum. Used by the batter/hitter to hit the baseball.', category = category2, user_id=2)

session.add(categoryItem1)
session.commit()

categoryItem2 = CategoryItem(name = 'Helmet', description = 'Protects the hitter from stray pitches.', category = category2, user_id=2)

session.add(categoryItem2)
session.commit()

category3 = Category(name = 'Basketball', user_id=2)

session.add(category3)
session.commit()

categoryItem1 = CategoryItem(name = 'Sneakers', description = 'Ideal shoe for basketball. Gives the player optimal grip on wood and concrete courts.', category = category3, user_id=2)

session.add(categoryItem1)
session.commit()

categoryItem2 = CategoryItem(name = 'Jersey', description = "Light, breathable material, usually representative of the player's team.", category = category2, user_id=2)

session.add(categoryItem2)
session.commit()

category4 = Category(name = 'Frisbee', user_id=2)

session.add(category4)
session.commit()

categoryItem1 = CategoryItem(name = 'Frisbee', description = 'Plastic disc used to play Frisbee. When thrown properly it can soar long distances.', category = category4, user_id=2)

session.add(categoryItem1)
session.commit()

category5 = Category(name = 'Snowboarding', user_id=2)

session.add(category5)
session.commit()

categoryItem1 = CategoryItem(name = 'Snowboard', description = 'All-mountain snowboards perform anywhere on a mountain, groomed runs, back country, even park and pipe. ', category = category5, user_id=2)

session.add(categoryItem1)
session.commit()

category6 = Category(name = 'Rock Climbing', user_id=2)

session.add(category6)
session.commit()

category7 = Category(name = 'Hockey', user_id=2)

session.add(category7)
session.commit()

category8 = Category(name = 'Skating', user_id=2)

session.add(category8)
session.commit()

category9 = Category(name = 'Foosball', user_id=2)

session.add(category9)
session.commit()
