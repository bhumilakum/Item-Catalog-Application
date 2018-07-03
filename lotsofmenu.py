from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
import datetime
from database_setup import Base, Category, Item,  User

# connect to the database
engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

# create database session
DBSession = sessionmaker(bind=engine)
session = DBSession()

# fetching current date
today_date = datetime.datetime.now()

# adding data into database manually

user1 = User(name="Bhumi Lakum", email="bhumi.lakum@gmail.com",
             picture="https://avatars0.githubusercontent.com\
                        /u/37665131?s=460&v=4")
session.add(user1)
session.commit()

category1 = Category(user_id=1, name="Sports")
session.add(category1)
session.commit()

item1 = Item(name="Carrom Board",
             description="This is an indoor game for all people\
                        of any age group.",
             image="carrom_board.jpg", price=500,
             created=today_date, user_id=1, category=category1)
session.add(item1)
session.commit()

item2 = Item(name="Football", description="A ball with high quelity\
                    for kids to play.",
             image="football.jpg", price=400,
             created=today_date, user_id=1, category=category1)
session.add(item2)
session.commit()

item3 = Item(name="Hand Weights", description="Exercies is the most potent\
                    and underutilized antidepressant and it's free.",
             image="hand_weight.jpg", price=2000,
             created=today_date, user_id=1, category=category1)
session.add(item3)
session.commit()

# ===========================================================================
category2 = Category(user_id=1, name="Education")
session.add(category2)
session.commit()

item1 = Item(name="Color Markers", description="Perfect for highlighting\
                    important points!!!",
             image="markers.jpg", price=100,
             created=today_date, user_id=1, category=category2)
session.add(item1)
session.commit()

item2 = Item(name="Notebook", description="Making and keeping notebooks\
                    was such an important information management technique\
                    that children learned how to do it in school.",
             image="notebook.jpg", price=50,
             created=today_date, user_id=1, category=category2)
session.add(item2)
session.commit()

item3 = Item(name="School Bag", description="Animal Printed School\
                Bag Blue Yellow.",
             image="school_bag.jpg", price=400,
             created=today_date, user_id=1, category=category2)
session.add(item3)
session.commit()

item1 = Item(name="Alpha Numeric Board", description="Alpha Numero Board\
                    A double sided playing board. Write and wipe on the\
                    green board with a chalk.",
             image="alpha_numeric_board.jpg", price=350,
             created=today_date, user_id=1, category=category2)
session.add(item1)
session.commit()

item2 = Item(name="Sticky Notes", description="Sticky Note Memo Pad with\
                    Arrow Flags Set - 100 Sheets 4 Sticky Note Pads.",
             image="sticky_notes.jpg", price=250,
             created=today_date, user_id=1, category=category2)
session.add(item2)
session.commit()

item3 = Item(name="Geometry Box", description="Specially designed self\
                centering compass and divider, for ease and accuracy while\
                drawing circles and angles.",
             image="geometric_box.jpg", price=200,
             created=today_date, user_id=1, category=category2)
session.add(item3)
session.commit()
# ==========================================================================
category3 = Category(user_id=1, name="Fashion")
session.add(category3)
session.commit()

item1 = Item(name="Sun Glasses", description="Sunglasses are a form of\
                protective eyewear designed primarily to prevent bright\
                sunlight and high-energy visible light from damaging or\
                discomforting the eyes.",
             image="sunglasses.jpg", price=500,
             created=today_date, user_id=1, category=category3)
session.add(item1)
session.commit()

item2 = Item(name="Hand Bag", description="A bag is a common tool in the\
                form of a non-rigid container.",
             image="bag.jpg", price=700,
             created=today_date, user_id=1, category=category3)
session.add(item2)
session.commit()

item3 = Item(name="Sandals", description="Sandals are an open type of\
                footwear, consisting of a sole held to the wearer's foot by\
                straps going over the instep and, sometimes,\
                around the ankle.",
             image="sandal.jpg", price=600,
             created=today_date, user_id=1, category=category3)
session.add(item3)
session.commit()

# ===========================================================================
category4 = Category(user_id=1, name="Home Decor")
session.add(category4)
session.commit()

item1 = Item(name="Wind Chimes", description="Wind chimes are a type of\
                percussion instrument constructed from suspended tubes,\
                rods, bells or other objects that are often made of\
                metal or wood.",
             image="windchimes.jpg", price=350,
             created=today_date, user_id=1, category=category4)
session.add(item1)
session.commit()

item2 = Item(name="Photo Frames", description="A photo frame is a decorative\
                edging for a picture, such as a painting or photograph,\
                intended to enhance it, make it easier to display or\
                protect it.",
             image="photo_frames.jpg", price=800,
             created=today_date, user_id=1, category=category4)
session.add(item2)
session.commit()

item3 = Item(name="Flower Pot", description="Flower pot is a container in\
                which flowe and other plants are cultivated and displayed.",
             image="flower_pot.jpg", price=600,
             created=today_date, user_id=1, category=category4)
session.add(item3)
session.commit()

# ==========================================================================
category5 = Category(user_id=1, name="Travel")
session.add(category5)
session.commit()

item1 = Item(name="Power Bank", description="Power bank is a high-capacity\
                portable charger from Asus.You never again have to worry\
                about your devices running out of charge!",
             image="power_bank.jpg", price=1800,
             created=today_date, user_id=1, category=category5)
session.add(item1)
session.commit()

item2 = Item(name="Travel Bag", description="Hard and soft luggage bags\
                with tsa combination lock.",
             image="travel_bag.jpg", price=2500,
             created=today_date, user_id=1, category=category5)
session.add(item2)
session.commit()
# ==========================================================================

category6 = Category(user_id=1, name="Electronics")
session.add(category6)
session.commit()

item1 = Item(name="Iron", description="A clothes iron is a roughly\
                triangular surface that, when heated, is used to press\
                clothes to remove creases.",
             image="iron.jpg", price=1500,
             created=today_date, user_id=1, category=category6)
session.add(item1)
session.commit()

item2 = Item(name="Hair Dryer", description=" This hair dryer features\
                the Ehd + technology which ensures that only the right\
                amount of heat is distributed on your hair and thus prevents\
                any damage to your hair.",
             image="hair_dryer.jpg", price=600,
             created=today_date, user_id=1, category=category6)
session.add(item2)
session.commit()

item3 = Item(name="Coffee Maker", description="Coffee drip filter machine.",
             image="coffee_maker.jpg", price=1500,
             created=today_date, user_id=1, category=category6)
session.add(item3)
session.commit()

# ==========================================================================

category7 = Category(user_id=1, name="Kids")
session.add(category7)
session.commit()

item1 = Item(name="Tricycle", description="Tricycle is three-wheeled\
                vehicle based on the same technology as a bicycle or\
                motorcycle.",
             image="tricycle.jpg", price=1000,
             created=today_date, user_id=1, category=category7)
session.add(item1)
session.commit()

item2 = Item(name="Animal Chair", description="It is Ideal for children\
                between 3 Yea to 8 Yea.It is very comfortable to sit on it.",
             image="animal_chair.jpg", price=400,
             created=today_date, user_id=1, category=category7)
session.add(item2)
session.commit()

item3 = Item(name="Mug", description="A mug is a type of cup typically used\
                for drinking hot beverages, such as coffee, hot chocolate,\
                soup, or tea.",
             image="mug.jpg", price=150,
             created=today_date, user_id=1, category=category7)
session.add(item3)
session.commit()

item1 = Item(name="Beach Sand Toy", description="Kids Beach Sand Toy with\
                Mesh Bag Sandbox Play Set for Toddle, Includes Sand Bucket,\
                Sea Creatures, Sand Stamps, Sand Castle Molds with Shovels,\
                Rakes, and Knif - 36 pcs.",
             image="beach_sand_toy.jpg", price=250,
             created=today_date, user_id=1, category=category7)
session.add(item1)
session.commit()
