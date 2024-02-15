# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db, DataValidationError
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    #
    # ADD YOUR TEST CASES HERE
    #
    def test_read_a_product(self):
        """It should Read a product"""
        product = ProductFactory()
        app.logger.info(str(product))
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        # Read product by id
        read_product = Product.find(product.id)
        # Assert that it is the same as the one stored
        self.assertEqual(read_product.id, product.id)
        self.assertEqual(read_product.description, product.description)
        self.assertEqual(read_product.price, product.price)
        self.assertEqual(read_product.available, product.available)
        self.assertEqual(read_product.category, product.category)

    def test_update_a_product(self):
        """It should Update a product"""
        product = ProductFactory()
        app.logger.info(str(product))
        product.id = None
        product.create()
        app.logger.info(str(product))
        current_id = product.id
        # Modify the product
        product.description = "This is a test description"
        product.update()
        # Assert that it has been properly updated
        all_products = Product.all()
        self.assertEqual(len(all_products), 1)
        self.assertEqual(product.id, current_id)
        self.assertEqual(product.description, "This is a test description")
        # Assert that updating a product with no ID throws an exception
        product.id = None
        self.assertRaises(DataValidationError, product.update)

    def test_delete_a_product(self):
        """It should Delete a product"""
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that there is only one product
        all_products = Product.all()
        self.assertEqual(len(all_products), 1)
        product.delete()
        all_products = Product.all()
        self.assertEqual(len(all_products), 0)

    def test_list_all_products(self):
        """It should List all products"""
        products = Product.all()
        self.assertEqual(len(products), 0)
        # Create Products
        for _ in range(0, 5):
            product = ProductFactory()
            product.id = None
            product.create()
        # Assert that they have been created and can be listed
        products = Product.all()
        self.assertEqual(len(products), 5)

    def test_find_a_product_by_name(self):
        """It should Find all products with a given name"""
        # Create Products
        products = ProductFactory.create_batch(5)
        for p in products:
            p.id = None
            p.create()
        first_name = products[0].name
        # Get number of occurrences for the same product name
        occurrences = len([x for x in products if x.name == first_name])
        # Get number of occurrences for the same product name in the db
        find_all = Product.find_by_name(first_name)
        # Assert that find_by_name got all the products with the same name
        self.assertEqual(find_all.count(), occurrences)
        for p in find_all:
            self.assertEqual(p.name, first_name)

    def test_find_a_product_by_availability(self):
        """It should Find all products by availability"""
        # Create Products
        products = ProductFactory.create_batch(10)
        for p in products:
            p.id = None
            p.create()
        first_availability = products[0].available
        # Get number of occurrences for the same product availability
        occurrences = len([x for x in products if x.available == first_availability])
        # Get number of occurrences for the same product availability in the db
        find_all = Product.find_by_availability(first_availability)
        # Assert that find_by_name got all the products with the same name
        self.assertEqual(find_all.count(), occurrences)
        for p in find_all:
            self.assertEqual(p.available, first_availability)

    def test_find_a_product_by_category(self):
        """It should Find all products by category"""
        # Create Products
        products = ProductFactory.create_batch(10)
        for p in products:
            p.id = None
            p.create()
        first_category = products[0].category
        # Get number of occurrences for the same product availability
        occurrences = len([x for x in products if x.category == first_category])
        # Get number of occurrences for the same product availability in the db
        find_all = Product.find_by_category(first_category)
        # Assert that find_by_name got all the products with the same name
        self.assertEqual(find_all.count(), occurrences)
        for p in find_all:
            self.assertEqual(p.category, first_category)

    def test_find_a_product_by_price(self):
        """It should Find all products by price"""
        # Create Products
        products = ProductFactory.create_batch(10)
        for p in products:
            p.id = None
            p.create()
        first_price = products[0].price
        # Get number of occurrences for the same product availability
        occurrences = len([x for x in products if x.price == first_price])
        # Get number of occurrences for the same product availability in the db
        find_all = Product.find_by_price(str(first_price))
        # Assert that find_by_name got all the products with the same name
        self.assertEqual(find_all.count(), occurrences)
        for p in find_all:
            self.assertEqual(p.price, first_price)
        