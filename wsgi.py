# wsgi.py
from flask import Flask, request, abort, render_template
from flask_restplus import Api,Namespace, Resource
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

import os
import logging
from config import Config

logging.warn(os.environ["SECRET_KEY"])

app = Flask(__name__)
app.config.from_object(Config)

from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow # Order is important here!
db = SQLAlchemy(app)
ma = Marshmallow(app)

from models import Product
from schemas import products_schema, product_schema

admin = Admin(app, template_mode='bootstrap3')
admin.add_view(ModelView(Product, db.session))

@app.route('/')
def home():
    products = db.session.query(Product).all()
    return render_template('home.html', products=products)


@app.route('/<int:id>')
def product_html(id):
    product = db.session.query(Product).get(id)
    return render_template('product.html', product=product)

# @app.route('/products')
# def products():
#     products = db.session.query(Product).all() # SQLAlchemy request => 'SELECT * FROM products'
#     return products_schema.jsonify(products)


# product = Product()
# product.id = ""
# prodcut.name =""

# READ: The endpoint to list a single product from its id.
# CREATE: The endpoint to create a new product from a POST request body
# DELETE: The endpoint to remove a product from a database
# UPDATE: The endpoint to update an existing product from a PATCH request body and its id in the URL

ns = Namespace('api/v1/products')

api = Api()
api.add_namespace(ns)
api.init_app(app)

@ns.route('/')
class ApiProducts(Resource):
    def get(self):
        products = db.session.query(Product).all() # SQLAlchemy request => 'SELECT * FROM products'
        return products_schema.jsonify(products)

    def put(self):
        body = request.get_json()
        productid = body.get('id')
        productname = body.get('name')
        product = Product(id=productid,name=productname)
        db.session.add(product)
        db.session.commit()
        return None

@ns.route('/<int:id>')
class ApiProduct(Resource):
    def get(self, id):
        product = Product.query.get(id)
        return product_schema.jsonify(product)

    def patch(self, id):
        body = request.get_json()
        name = body.get('name')
        if name is None:
            abort(400)

        product = Product.query.get(id)
        product.name = name
        db.session.commit()
        return product_schema.jsonify(product)

    # def patch(self, id):
    #     product = Product.query.get(id)
    #     product.name = "nouveaunom"
    #     db.session.commit()
    #     return product_schema.jsonify(product)

    def delete(self, id):
        logging.warn(f"delete is called id={id}")
        product = Product.query.get(id)
        db.session.delete(product)
        db.session.commit()
        return product_schema.jsonify(product)


