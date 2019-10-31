from flask import Flask
from flask_restful import Api, Resource, reqparse
from neo4j import GraphDatabase  # neo4j
# rem: http://localhost:5000/user/Stacy

# flask setup
app = Flask(__name__)
api = Api(app)

# neo4j setup:
# create driver
driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'devpass'))
# pull results from neo4j needed to vend requests to api
with driver.session() as session:
    result = session.run('MATCH (c:Category)-[:HAS_PRODUCT]->(p:Product)-[:HAS_ATTRIBUTES]->(a:Attributes) WHERE c.catName = \'Bearing\' RETURN DISTINCT p.prodDescription AS Product, p.manufacturerId AS Manuf_Id, p.manufacturer as Manuf, a.attributes AS Attributes')

# create api store from neo4j query
products = []
# Product	Manuf_Id	Manuf	Attributes
for record in result:
    print('{} : {} : {} : {}'.format(record['Product'], record['Manuf_Id'], record['Manuf'], record['Attributes']))
    products.append(
        {
            'product':record['Product'],
            'manuf_id':record['Manuf_Id'],
            'manuf':record['Manuf'],
            'attributes':record['Attributes']
        }
    )

# TEST
print(products)

# create api endpoints via user resource class
class Product(Resource):
    # method to get user data
    def get(self, manuf_id):
        for product in products:
            if manuf_id == product['manuf_id'].replace(" ", "").lower():
                return product, 200
        return 'Product not found', 404

# after implementing all the methods in your User resource,
# add the resource to your api and specify the route,
# then finally run the flask application

api.add_resource(Product, '/product/<string:manuf_id>')

# rem running in debug mode enable flask to reload
# automatically when code is updated and give warning messages
# if something goes wrong-- dev only feature
app.run(debug=True)
