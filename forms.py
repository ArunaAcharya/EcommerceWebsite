from wtforms import SubmitField, StringField, IntegerField, FloatField,HiddenField,DateField, SelectField,FileField
from wtforms.validators import DataRequired, NumberRange
from flask_wtf import FlaskForm
from dbmodel import Product

class SignupForm(FlaskForm):
    email= StringField("Email Address" , validators=[DataRequired()])
    name= StringField("Name", validators=[DataRequired()])
    username= StringField("Username",validators=[DataRequired()])
    password= StringField('Password', validators=[DataRequired()])
    phone_number= IntegerField("Phone Number", validators=[DataRequired()])
    dob= DateField("Date of Birth", validators=[DataRequired()])
    gender= SelectField("Gender", choices=[('Female'), ('Male')])
    submit= SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email= StringField("Email Address or Username", validators=[DataRequired()])
    password= StringField("Password", validators=[DataRequired()])
    submit= SubmitField('Login')

class AddProductForm(FlaskForm):
    pCode= StringField("Product Code", validators=[DataRequired()])
    name= StringField("Product Name", validators=[DataRequired()])
    price= FloatField("Price", validators=[DataRequired()])
    description= StringField("Description", validators=[DataRequired()])
    availablity= IntegerField("Stock On Hand", validators=[DataRequired()])
    category= SelectField("Category", choices=[("women"),("men"),("Kids"),("Accessories")])
    file= FileField("Picture", validators=[DataRequired()])
    submit= SubmitField("Add")

class AddtoCartForm(FlaskForm):
    size= SelectField("Size: ", choices=[("XS"),("S"),("M"),("L"),("XL")])
    quantity= IntegerField("Qty:", validators=[DataRequired()])
    add_to_cart= SubmitField("Add to Bag")

class EditProductForm(FlaskForm):
    name= StringField("Product Name", validators=[DataRequired()])
    price= FloatField("Price", validators=[DataRequired()])
    description= StringField("Description", validators=[DataRequired()])
    availability= IntegerField("Stock On Hand", validators=[DataRequired()])
    category= StringField("Category", validators=[DataRequired()])
    file= FileField("Picture")
    submit= SubmitField("Edit")

class SearchForm(FlaskForm):
    search= StringField('search', validators=[DataRequired()])
    submit= SubmitField('Search', render_kw={'class': 'btn fa-solid icon-btn fa-magnifying-glass'})