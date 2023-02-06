from flask import Flask, render_template, url_for, redirect, request, flash, abort, session
import stripe
from forms import LoginForm,SignupForm,AddProductForm,AddtoCartForm, EditProductForm, SearchForm
from dbmodel import Admin, Customer,Cart,Product, DBSession,Wishlist
from dbmodel import session as db
from flask_bootstrap import Bootstrap
from flask_login import login_user, LoginManager, login_required, current_user, logout_user, UserMixin
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from flask_uploads import UploadSet, configure_uploads, IMAGES
from sqlalchemy import select, insert, delete, update

#app config
app= Flask(__name__)
app.config['SECRET_KEY']= "thisismysecretkey283628352746tgved"
Bootstrap(app)

#stripe
app.config['STRIPE_PUBLIC_KEY']='pk_test_51MCBf2FdUlqHcmR21kFBJDOBWFShSf3SUCudaEMcPilNgKNAEVBRrjTZaPlPv2AOM5HJCkwlLBD1fjO99YH1YTX2006HkZ0Vwn'
app.config['STRIPE_SECRET_KEY']='sk_test_51MCBf2FdUlqHcmR2Ad3kaDQk6B1wef1QRCYYCo6gWunODCEbojPj3APU6gMX2VdLMBCQ29LJdwcgDJdMj9pNiCEQ00fWJI1ADJ'
stripe.api_key = 'sk_test_51MCBf2FdUlqHcmR2Ad3kaDQk6B1wef1QRCYYCo6gWunODCEbojPj3APU6gMX2VdLMBCQ29LJdwcgDJdMj9pNiCEQ00fWJI1ADJ'
YOUR_DOMAIN= "http://127.0.0.1:5000/"

#UPLOAD FILES
UPLOAD_FOLDER= f'static/images/products'
ALLOWED_EXTENSIONS={'txt', 'pdf','png','jpg','jpeg','gif'}
app.config['UPLOADED_PHOTOS_DEST']= UPLOAD_FOLDER
photos= UploadSet('photos', IMAGES)
configure_uploads(app,photos)



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS


def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:return redirect(url_for('login'))
    return wrap

def not_logged_in(f):
    @wraps(f)
    def wrap (*args, **kwargs ):
        if 'logged_in' in session:
            return redirect(url_for('home'))
        else:return f(*args, **kwargs)
    return wrap

def is_admin_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'admin_logged_in' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('admin_login'))
    return wrap

def not_admin_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'admin_logged_in' in session:
            return redirect(url_for('admin'))
        else:
            return f(*args, **kwargs)
    return wrap

def wrappers(func, *args, **kwargs):
    def wrapped():
        return func(*args, **kwargs)
    return wrapped()




@app.route('/')
def home():

    return render_template("home.html")

@app.route('/women', methods=['GET', 'POST'])
def women():
    women_products= db.query(Product).where (Product.category=="women").all()
    return render_template("women.html", products= women_products)


@app.route('/men')
def men():
    men_products= db.query(Product).where(Product.category=='men').all()
    return render_template("men.html", products=men_products)

@app.route('/signup', methods=['Get', 'POST'])
@not_logged_in
def signup():
    form= SignupForm()
    if form.validate_on_submit():
        if request.method == "POST" and form.validate():
            cus_email = form.email.data

            result = db.execute(select(Customer).where(Customer.email == cus_email)).first()
            if result is not None:
                flash("you have already signed up please login")
                return redirect(url_for('login'))
            name = form.name.data
            username = form.username.data
            gender = form.gender.data
            password = generate_password_hash(
                form.password.data,
                method="pbkdf2:sha256",
                salt_length=8
            )
            mobile = form.phone_number.data
            dob = form.dob.data

            new_customer= Customer(
                name= name,
                username= username,
                email= cus_email,
                password= password,
                gender= gender,
                mobile= mobile,
                dob= dob
            )
            db.add(new_customer)
            db.commit()

            return redirect(url_for('login'))

    return render_template("signup.html", form= form, user= current_user)

@app.route('/login', methods= ['GET', 'POST'])
@not_logged_in
def login():
    form= LoginForm(request.form)
    if request.method =="POST" and form.validate():
        log_username= form.email.data
        customer_password= form.password.data

        customer= db.execute(select(Customer).where(Customer.username==log_username or Customer.email== log_username) ).first()
        if customer is not None:
            for row in customer:
                password= row.password
                uid= row.id
                name= row.name
                if check_password_hash(password, customer_password):
                    session['logged_in'] = True
                    session['uid'] = uid
                    session['s_name'] = name
                    print(session['uid'])
                    return redirect(url_for('home'))
                else:
                    flash("password incorrect, please try again")
                    return redirect(url_for('login'))

        else:
            flash("That username does not exist please try again!")
            return redirect(url_for('login'))

    return render_template("login.html", form= form )

@app.route('/admin_login', methods= ['GET', 'POST'])
@not_admin_logged_in
def admin_login():
    form = LoginForm(request.form)
    if request.method == 'POST':
        username= request.form['email']
        password_candidate= request.form['password']

        result= db.execute(select(Admin).where(Admin.email== username)).first()
        if result is not None:
            for row in result:
                admin_password= row.password
                admin_name= row.name
                admin_id= row.id
                if check_password_hash(admin_password, password_candidate):
                    session['admin_logged_in'] = True
                    session['admin_id'] = admin_id
                    session['admin_name'] = admin_name
                    return redirect(url_for('admin'))

                else:flash("Password incorrect please try again")
                return redirect(request.referrer)

        else:
            flash("that username does not exist please try again!")
            return render_template("admin_login.html")

    return render_template('admin/admin_login.html', form= form)

@app.route('/index')
@is_admin_logged_in
def admin():
    products=db.query(Product).all()
    return render_template("admin/index.html", products= products)

@app.route('/admin_add_product', methods= ['GET', 'POST'])
@is_admin_logged_in
def admin_add_product():
    form = AddProductForm(request.form)
    if request.method == 'POST':
        product_code= request.form['pCode']
        product_name= request.form['name']
        price= request.form['price']
        description= request.form['description']
        available= request.form['availablity']
        category= request.form['category']
        file= request.files['file']

        if 'file' not in request.files:
            flash('Pictures Not found')
            return redirect(url_for('admin_add_product'))

        if file.filename=='':
            flash('No selected file')
            return redirect(url_for('admin_add_product'))

        if file :
            pic= file.filename
            photo= pic.replace("'","")
            picture= photo.replace(" ","_")
            if picture.lower().endswith(('.png' , '.jpg','.jpeg')):
                save_photo= photos.save(file,folder=category)
                if save_photo:
                    new_product= Product(
                        pCode= product_code,
                        name= product_name,
                        price= price,
                        description= description,
                        stockonhand= available,
                        category= category,
                        picture= picture
                    )
                    db.add(new_product)
                    db.commit()
                    flash("Product successfully added")
                    return redirect(url_for('admin_add_product'))
    return render_template('admin/add_product.html', form= form)

@app.route('/delete/<product_id>')
def admin_delete_product(product_id):
    product= db.query(Product).get(product_id)
    db.delete(product)
    db.commit()
    return render_template("admin/index.html")


@app.route('/edit/<product_id>', methods= ['GET', 'POST'])
def admin_edit_product(product_id):
    product= db.query(Product).get(product_id)
    form= EditProductForm(

        name= product.name,
        price= product.price,
        description= product.description,
        availability= product.stockonhand,
        category= product.category,
        file= product.picture,

    )
    if request.method=='POST':
        file= request.files['file']
        if file :
            pic= file.filename
            photo= pic.replace("'","")
            picture= photo.replace(" ","_")
            if picture.lower().endswith(('.png' , '.jpg','.jpeg')):
                save_photo= photos.save(file,folder=product.category)
                if save_photo:
                    product.pCode = product_id
                    product.name = request.form['name']
                    product.price = request.form['price']
                    product.description = request.form['description']
                    product.stockonhand = request.form['availability']
                    product.category = request.form['category']
                    product.picture=save_photo

                    try:
                        db.commit()

                    except:
                        db.rollback()
                        raise
                    finally:
                        db.close()
                    return redirect(url_for('admin'))

    return render_template("admin/edit_product.html", form= form, pCode_edit= True, product= product)


@app.route('/viewproduct/<product_id>', methods= ['GET','POST'])
def viewproduct(product_id):
    form= AddtoCartForm()
    requested_product = db.query(Product).where(Product.pCode == product_id).all()
    for row in requested_product:
        price = row.price
        name = row.name
        description = row.description
        image = row.picture
        category = row.category
    if request.method=='POST':
        if 'uid' in session:
            result = db.execute(select(Cart).where(Cart.customer_id == session['uid'] and Cart.products == product_id)).all()

            item= Cart(
                customer_id= session['uid'],
                products= product_id,
                quantity= request.form.get('quantity')
            )
            db.add(item)
            db.commit()
            return redirect(url_for('cart'))
        else:
            flash("Login required to continue")
            return redirect(url_for('login'))

    return render_template("show_product.html", product= requested_product, form= form,product_price=price, name=name, description= description, picture= image, category= category, current_user= current_user, id= Cart.id)


@app.route('/cart', methods= ['GET','POST'])
@is_logged_in
def bag():
    cart_product = db.query(Product).join(Cart).add_columns(Cart.customer_id, Cart.products, Cart.quantity,
                                                            Product.category,
                                                            Product.price, Product.name, Product.picture).where(
        Cart.customer_id == session['uid']).all()
    session['cart'] = len(cart_product)
    total_price = 0


    for row in cart_product:
        total_price += row.price* row.quantity

    return render_template("cart.html", cart= cart_product, total_price= total_price)

@app.route('/cart', methods= ["GET", "POST"])
@is_logged_in
def cart():
    if 'uid' in session:
        uid= session['uid']

        cart_product = db.query(Product).join(Cart).add_columns(Cart.customer_id, Cart.products, Cart.quantity,Product.category,
                                                                     Product.price, Product.name, Product.picture).where(
            Cart.customer_id == uid).all()
        if 'cart' in session:
            print(session['cart'])
        else:
            session['cart'] = len(cart_product)
            return redirect(request.referrer)

        total_price= 0
        for row in cart_product:
            total_price += row.price* row.quantity


    else:
        flash("Please Login to continue")
        return redirect(url_for('login'))

    return render_template("cart.html", cart= cart_product, total_price= total_price)

@app.route('/addquantity')
def add_quantity():
    product_id= request.args.get('products')
    item = db.query(Cart).where(Cart.customer_id == session['uid'] and Cart.products == product_id).first()
    item.quantity += 1
    db.commit()
    return redirect(request.referrer)

@app.route('/lowerquantity')
def remove_quantity():
    product_id = request.args.get('products')
    item = db.query(Cart).where(Cart.customer_id == session['uid'] and Cart.products == product_id).first()
    item.quantity -= 1
    db.commit()
    if item.quantity <=0:
        removed_item= db.query(Cart).where(Cart.customer_id== session['uid'] and Cart.quantity<=0).first()
        db.delete(removed_item)
        db.commit()
    return redirect(request.referrer)

@app.route('/wishlist', methods= ['GET','POST'])
def wishlist():
    if request.method=='POST':
        product_id= request.args.get('product_id')
        if 'uid' in session:
            item=Wishlist(
                customer_id= session['uid'],
                products= product_id

            )
            db.add(item)
            db.commit()
            return redirect(request.referrer)

    return render_template('wish.html',)


@app.route('/checkout', methods= ['GET','POST'])
def pay():
    stripesession = stripe.checkout.Session.create(
        line_items=[
            {
                # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                'price': 'price_1MCupUFdUlqHcmR2U0TTIHQ1',
                'quantity': 5,
            }],
        mode='payment',
        success_url=url_for('home', _external=True),
        cancel_url=url_for('men', _external=True))

    return redirect(stripesession.url)

@app.context_processor
def base():
    form= SearchForm()
    return dict(form= form)

@app.route('/search', methods= [ 'POST'])
def search():
    form = SearchForm()
    if form.validate_on_submit():

        searched= form.search.data
        query= db.query(Product).filter(Product.name == searched).all()
        print(query)
        if query == []:
            flash(f'We could not  find any results for "{searched}"')
            return render_template("search.html")

        return render_template('search.html', form= form, searched= query)
    else:
        return redirect(request.referrer)
    

@app.route('/logout')
def logout():
    if 'uid' in session:
        session.clear()
        return redirect(url_for('home'))
    return redirect(url_for('login'))



if __name__ == "__main__":
    app.run(debug=True)
