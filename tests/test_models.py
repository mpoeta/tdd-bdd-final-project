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

    def test_read_a_product(self):
        """It should Read a Product"""
        # Create a Product object using the ProductFactory
        product = ProductFactory()
        app.logger.info(product.serialize())
        # Set the ID of the product object to None and then create the product
        product.id = None
        product.create()
        # Assert that the product ID is not None
        self.assertIsNotNone(product.id)
        # Fetch the product back from the database
        found_product = Product.find(product.id)
        # Assert the properties of the found product are correct
        self.assertEqual(found_product.id, product.id)
        self.assertEqual(found_product.name, product.name)
        self.assertEqual(found_product.description, product.description)
        self.assertEqual(found_product.price, product.price)
        self.assertEqual(found_product.available, product.available)
        self.assertEqual(found_product.category, product.category)

    def test_update_a_product(self):
        """It should Update a Product"""
        # Create a Product object using the ProductFactory
        product = ProductFactory()
        app.logger.info(product.serialize())
        # Set the ID of the product object to None and create the product
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        app.logger.info(product.serialize())
        # Update the description property of the product object
        original_id = product.id
        original_description_reverse = product.description[::-1]
        product.description = original_description_reverse
        product.update()
        # Assert that that the id and description properties of the product object have been updated correctly
        self.assertEqual(product.id, original_id)
        self.assertEqual(product.description, original_description_reverse)
        # Fetch all products from the database to verify that after updating the product,
        # there is only one product in the system
        all_products = Product.all()
        self.assertEqual(len(all_products), 1)
        # Assert the product has the original id and the new description
        found_product = all_products[0]
        self.assertEqual(found_product.id, original_id)
        self.assertEqual(found_product.description, original_description_reverse)

    def test_delete_a_product(self):
        """It should Delete a Product"""
        # Create a Product object using the ProductFactory and save it to the database
        product = ProductFactory()
        product.create()
        # Assert that after creating a product and saving it to the database, there is only one product in the system.
        self.assertEqual(len(Product.all()), 1)
        # Remove the product from the database
        product.delete()
        # Assert if the product has been successfully deleted from the database
        self.assertEqual(len(Product.all()), 0)

    def test_list_all_products(self):
        """It should List all Products"""
        # Retrieve all products from the database and assign them to the products variable
        all_products = Product.all()
        # Assert there are no products in the database at the beginning of the test case
        self.assertEqual(len(all_products), 0)
        # Create five products and save them to the database
        for _ in range(5):
            product = ProductFactory()
            product.create()
        # Fetching all products from the database again and assert the count is 5
        all_products = Product.all()
        self.assertEqual(len(all_products), 5)

    def test_find_a_product_by_name(self):
        """It should Find a Product by Name"""
        # Create a batch of 5 Product objects using the ProductFactory and save them to the database
        products_batch = ProductFactory.create_batch(5)
        for product in products_batch:
            product.create()
        # Retrieve the name of the first product in the products list
        name = products_batch[0].name
        # Count the number of occurrences of the product name in the list
        name_count = sum(product.name == name for product in products_batch)
        # Retrieve products from the database that have the specified name
        found_products = Product.find_by_name(name)
        # Assert if the count of the found products matches the expected count
        self.assertEqual(found_products.count(), name_count)
        # Assert that each product's name matches the expected name
        for product in found_products:
            self.assertEqual(product.name, name)

    def test_find_a_product_by_availability(self):
        """It should Find a Product by Availability"""
        # Create a batch of 10 Product objects using the ProductFactory and save them to the database
        products_batch = ProductFactory.create_batch(10)
        for product in products_batch:
            product.create()
        # Retrieve the availability of the first product in the products list
        available = products_batch[0].available
        # Count the number of occurrences of the product availability in the list
        available_count = sum(product.available == available for product in products_batch)
        # Retrieve products from the database that have the specified availability
        found_products = Product.find_by_availability(available)
        # Assert if the count of the found products matches the expected count
        self.assertEqual(found_products.count(), available_count)
        # Assert that each product's availability matches the expected availability
        for product in found_products:
            self.assertEqual(product.available, available)

    def test_find_a_product_by_category(self):
        """It should Find a Product by Category"""
        # Create a batch of 10 Product objects using the ProductFactory and save them to the database
        products_batch = ProductFactory.create_batch(10)
        for product in products_batch:
            product.create()
        # Retrieve the category of the first product in the products list
        category = products_batch[0].category
        # Count the number of occurrences of the product that have the same category in the list
        category_count = sum(product.category == category for product in products_batch)
        # Retrieve products from the database that have the specified category
        found_products = Product.find_by_category(category)
        # Assert if the count of the found products matches the expected count
        self.assertEqual(found_products.count(), category_count)
        # Assert that each product's category matches the expected category
        for product in found_products:
            self.assertEqual(product.category, category)

    def test_update_a_product_with_empty_id(self):
        """It should Raise Error When Update with Empty ID"""
        # Create a Product object using the ProductFactory and save to database
        product = ProductFactory()
        product.create()
        # Set the ID of the product object to None
        product.id = None
        # Assert that update returns error
        self.assertRaises(DataValidationError, product.update)

    def test_serialize(self):
        """It should Serialize a Product"""
        # Create a Product using ProductFactory and serialize it
        product = ProductFactory()
        serialized = product.serialize()
        # Assert the serialized result has correct values
        self.assertEqual(serialized['id'], product.id)
        self.assertEqual(serialized['name'], product.name)
        self.assertEqual(serialized['description'], product.description)
        self.assertEqual(serialized['price'], str(product.price))
        self.assertEqual(serialized['available'], product.available)
        self.assertEqual(serialized['category'], product.category.name)

    def test_deserialize(self):
        """It should Deserialize a Product"""
        # Create a Product using ProductFactory and serialize it
        product_a = ProductFactory()
        serialized = product_a.serialize()
        # Create second, empty product and populate its properties from the serialized data
        product_b = Product()
        product_b.deserialize(serialized)
        # Assert product B has now the same properties as the product A, except id
        self.assertEqual(product_b.id, None)
        self.assertEqual(product_b.name, product_a.name)
        self.assertEqual(product_b.description, product_a.description)
        self.assertEqual(product_b.price, product_a.price)
        self.assertEqual(product_b.available, product_a.available)
        self.assertEqual(product_b.category, product_a.category)

    def test_deserialize_with_invalid_data(self):
        """It should Raise Error when Deserialize a Product with invalid data"""
        # Create an empty product
        product = Product()
        # Attempt to populate it using invalid data
        serialized = ProductFactory().serialize()
        serialized["available"] = "something"
        self.assertRaises(DataValidationError, lambda: product.deserialize(serialized))
        serialized = ProductFactory().serialize()
        serialized["category"] = "something"
        self.assertRaises(DataValidationError, lambda: product.deserialize(serialized))
        serialized = ProductFactory().serialize()
        serialized["category"] = None
        self.assertRaises(DataValidationError, lambda: product.deserialize(serialized))

    def test_find_a_product_by_price(self):
        """It should Find a Product by Price"""
        # Create a batch of 10 Product objects using the ProductFactory and save them to the database
        products_batch = ProductFactory.create_batch(10)
        for product in products_batch:
            product.create()
        # Retrieve the price of the first product in the products list
        price = products_batch[0].price
        # Count the number of occurrences of the product price in the list
        price_count = sum(product.price == price for product in products_batch)
        # Retrieve products from the database that have the specified price
        found_products = Product.find_by_price(price)
        # Assert if the count of the found products matches the expected count
        self.assertEqual(found_products.count(), price_count)
        # Assert that each product's price matches the expected price
        for product in found_products:
            self.assertEqual(product.price, price)

    def test_find_a_product_by_price_as_string(self):
        """It should Find a Product by Price as String"""
        # Create a batch of 10 Product objects using the ProductFactory and save them to the database
        products_batch = ProductFactory.create_batch(10)
        for product in products_batch:
            product.create()
        # Retrieve the price of the first product in the products list
        price = products_batch[0].price
        # Count the number of occurrences of the product price in the list
        price_count = sum(product.price == price for product in products_batch)
        # Retrieve products from the database that have the specified price converted to a string
        found_products = Product.find_by_price(str(price))
        # Assert if the count of the found products matches the expected count
        self.assertEqual(found_products.count(), price_count)
        # Assert that each product's price matches the expected price
        for product in found_products:
            self.assertEqual(product.price, price)
