from flask import Flask, render_template, request, redirect, session, flash, make_response
import database as db
import ordermanagement as om
import authentication
import logging
from bson.json_util import loads, dumps

app = Flask(__name__)

# secret key
app.secret_key = b's@g@d@c0ff33!'

# config
app.config['DEBUG'] = True
app.config['TESTING'] = True
logging.basicConfig(level=logging.DEBUG)
app.logger.setLevel(logging.INFO)


@app.route("/")
def index():
    return render_template('index.html', page='Index')


@app.route('/products')
def products():
    product_list = db.get_products()
    return render_template('products.html', page='Products', product_list=product_list)



@app.route('/productdetails')
def productdetails():
    """route to access detail of each product"""
    code = request.args.get('code', '')
    product = db.get_product(int(code))
    return render_template('productdetails.html', code=code, product=product)


@app.route('/branches')
def branches():
    branch_list = db.get_branches()
    print(branch_list)
    return render_template('branches.html', page='Branches', branch_list=branch_list) 


# route to access detail of each branch
@app.route('/branchdetails')
def branchdetials():
    code = request.args.get('code', '')
    branch = db.get_branch(float(code))
    return render_template('branchdetails.html', code=code, branch=branch)


@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html', page='About Us')


# login route
@app.route('/login', methods=['GET','POST'])
def login():
    return render_template('login.html')


# auth route
@app.route('/auth', methods=['POST'])
def auth():
    username = request.form.get('username')
    password = request.form.get('password')
    is_successful, user = authentication.login(username, password)
    app.logger.info('%s', is_successful)
    if is_successful:
        session["user"] = user
        return redirect('/')
    else:
        flash("Invalid username or password. Please try again.")
        return redirect('/login')


# logout route
@app.route('/logout')
def logout():
    session.pop("user", None)
    session.pop("cart", None)
    return redirect('/')


# add to cart route
@app.route('/addtocart', methods=['GET'])
def add_to_cart():
    code = request.args.get('code', '') # get product code from url
    product = db.get_product(int(code))
    item = dict()

    item["qty"] = 1
    item["name"] = product["name"]
    item["subtotal"] = product["price"] * item["qty"]

    if session.get("cart") is None:
        session["cart"] = {}
    
    cart = session["cart"]
    cart[code] = item
    session["cart"] = cart
    return redirect('/cart')


# cart route
@app.route('/cart')
def cart():
    return render_template('cart.html')


@app.route('/deleteitem')
def deleteitem():
    """remove an item from cart"""
    code = request.args.get('code', '')
    try:
        cart = session["cart"]
        del cart[code]
    except KeyError:
        return redirect('/cart')
    session["cart"] = cart
    return redirect('/cart')
    


@app.route('/checkout')
def checkout():
    """create a checkout route"""
    om.create_order_from_cart()
    session.pop("cart",None) # clear cart in session memory upon checkout
    return redirect('/ordercomplete')



@app.route('/ordercomplete')
def ordercomplete():
    """display completed orders"""
    return render_template('ordercomplete.html')


@app.route('/vieworders')   
def vieworders():
    """route for displaying orders"""
    user_cart = db.get_orders()
    user = session["user"]
    order_cart = []
    for order in user_cart:
        if order["username"] == user["username"]:
            user_cart_history = order["details"]
            order_cart.append(user_cart_history)
            print(user_cart_history)
    
    return render_template('vieworders.html', order_cart=order_cart)



@app.route('/changepasswordform')
def change_pass_form():
    """redirect to change password html"""
    return render_template('changepasswordform.html')


@app.route('/changepassword', methods=['GET','POST'])
def changepassword():
    """route for changing passwords"""
    users = session["user"]
    username = users["username"]
    old_pass = request.form.get('oldpassword')
    new_pass_1 = request.form.get('newpassword1')
    new_pass_2  = request.form.get('newpassword2')
    user_list = db.get_users()
    
    # check credentials and change pass if all are valid
    for user in user_list:
        if user["username"] == username and user["password"] == old_pass and new_pass_1 == new_pass_2:
            db.set_new_password(username, new_pass_1)
            error = False
            break
        else:
            error = True

    # check status of error
    if error:
        flash("Please again check if passwords match!")
        return render_template('changepasswordform.html')
    else:
        flash("Successfully changed passwords!")
        return redirect('/')


@app.route('/api/products', methods=["GET"])
def api_get_products():
    """Products API route"""
    resp = make_response(dumps(db.get_products()))
    resp.mimetype = 'application/json'
    return resp


@app.route('/api/products/<int:code>', methods=["GET"])
def api_get_product(code):
    """Product API route"""
    resp = make_response(dumps(db.get_product(code)))
    resp.mimetype = 'application/json'
    return resp