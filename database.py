from flask.globals import session
import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")

# reference the db from mongodb
products_db = myclient["products"]
order_management_db = myclient["order_management"]


# access product code
def get_product(code):
    products_coll = products_db["products"]
    product = products_coll.find_one({"code": code}, {"_id": 0})
    return product


# return all products
def get_products():
    product_list = []

    products_coll = products_db["products"]
    for p in products_coll.find({}, {"_id": 0}):
        product_list.append(p)

    return product_list


# access branch code
def get_branch(code):
    branches = products_db["branches"]
    branch = branches.find_one({"code": code})
    return branch


# return all branches
def get_branches():
    branch_list = []

    branches = products_db["branches"]
    for b in branches.find({}):
        branch_list.append(b)

    return branch_list


# getting user
def get_user(username):
    customers_coll = order_management_db["customers"]
    user = customers_coll.find_one({"username": username})
    return user


# create order
def create_order(order):
    orders_coll = order_management_db["orders"]
    orders_coll.insert(order)


# get orders
def get_orders():
    order_list = []

    orders_from_db = order_management_db["orders"]
    for order in orders_from_db.find({}):
        order_list.append(order)

    return order_list


# get all users
def get_users():
    user_list = []

    customers_db = order_management_db["customers"]
    for order in customers_db.find({}):
        user_list.append(order)

    return user_list


# change password
def set_new_password(username, new_password):
    customers_db = order_management_db["customers"]
    confirm = customers_db.update_one(
        {"username": username}, {"$set": {"password": new_password}}, upsert=False
    )
    return confirm
