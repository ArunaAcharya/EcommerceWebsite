from flask import Flask
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import Table, Column, Integer, ForeignKey, String,select, insert, delete, update, Date, VARCHAR, create_engine
from sqlalchemy import create_engine
from sqlalchemy import exc,event
from sqlalchemy_utils import database_exists, create_database

Base= declarative_base()
engine = create_engine("sqlite:///ray.db",connect_args={'check_same_thread': False}, echo=True)

DBSession= sessionmaker()
DBSession.configure(bind= engine)
SessionLocal= sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(engine)

session= DBSession()


class Admin(UserMixin, Base,):
    __tablename__ = "admin"
    id= Column(Integer, primary_key= True)
    email= Column(String(100), unique= True)
    password= Column(String(100), nullable= True)
    name= Column(String(100), nullable= True)




# CartItem=Table('cartitem', Base.metadata,
#         Column('cart_id', ForeignKey('cart.id')),
#         Column('product_id', ForeignKey('products.id'))
#           )
class Product(Base):
    __tablename__='products'
    pCode=Column(VARCHAR,unique= True, nullable= False, primary_key= True)
    name= Column(String, nullable= False)
    description= Column(String(500))
    price= Column(Integer,nullable= False)
    stockonhand= Column(Integer, nullable= False)
    category= Column(String(100))
    picture= Column(VARCHAR)

    def __repr__(self):
        return f"<Product {self.name}>"

class Customer(UserMixin, Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True)
    email = Column(String(100), unique=True)
    name = Column(String(100), nullable=False)
    username= Column(String(100), unique= True, nullable= False)
    password = Column(String(100), nullable=False)
    mobile= Column(Integer, nullable=False)
    dob= Column(Date, nullable= False)
    gender=Column(String(100), nullable=False)
    wishlist = relationship('Wishlist', backref='customers')
    cart= relationship("Cart")
    def __repr__(self):
        return f"<Customer {self.name}>"

class Wishlist(Base):
    __tablename__= "wishlists"
    id= Column(Integer,primary_key= True)
    customer_id=Column(Integer, ForeignKey("customers.id"), nullable= False)
    products= Column(String(200),ForeignKey("products.pCode"), nullable= True )


class Cart(Base):
    __tablename__ = 'cart'
    id= Column(Integer, primary_key=True)
    customer_id= Column(Integer, ForeignKey('customers.id'))
    products= Column(String,ForeignKey('products.pCode'))
    quantity = Column(Integer, nullable=False)


# query= session.query(Product).filter(Product.name== 'Dress').all()
#

# req_search= session.query(Product).filter(Product.name == 'Dress').first()
# print(req_search)
#
# # cart_product= session.query(Product).join(Cart).add_columns(Cart.customer_id, Cart.products,Cart.quantity,Product.price,Product.name,Product.picture).where(Cart.customer_id == 3).all()
# for item in cart_product:
#     print(item.name)

# cart_product = session.query(Product).join(Cart).add_columns(Cart.customer_id, Cart.products, Cart.quantity,Product.category,
#                                                                      Product.price, Product.name, Product.picture).where(
#             Cart.customer_id == 1).all()
# print(cart_product)
# product = session.execute(select(Product).where(Product.pCode == 'one')).first()
# for products in product:
#     print(products.name)

# result= session.execute(select(Customer).where(Customer.username== "ArunaAcharya")).first()
# if result is not None:
#   for row in result:
#       print(row.password)
# else:print("Not Found")

# result= session.execute(select(Cart).where(Cart.customer_id== 1 and Cart.products == "one")).all()
# print(len(result))

# cart_item= session.execute(select(Cart).where(Cart.customer_id==1)).all()
# for items in cart_item:
#     for item in items:
#         products= (item.products)
#         print(type(products))

# cart_item = session.query(Cart).where(Cart.customer_id == 1).first()
# for row in cart_item:
#     print(row.products)
#
# # query= session.query(Product).where (Product.pCode==products).first()
# print(query)
#
# result= session.execute(select(Product).where(Product.pCode== products)).first()
# print(result)





