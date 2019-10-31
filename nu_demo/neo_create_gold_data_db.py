# first, load constraint into the db
from neo4j import GraphDatabase
driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'devpass'))
with driver.session() as session:
    session.run('CREATE CONSTRAINT ON (p:Product) ASSERT p.prodDescription IS UNIQUE;')

# next, load data from csv
create_gold_query = '''
LOAD CSV WITH HEADERS FROM "file:///in_bearings_gold_data.csv" AS goldcsv
FIELDTERMINATOR '|'
WITH goldcsv
WHERE goldcsv.Product_Description IS NOT NULL
MERGE(p:Product {catName: goldcsv.Category, prodDescription: goldcsv.Product_Description, type: goldcsv.Product_Type, manufacturer: goldcsv.Manuf, manufacturerId: goldcsv.Manufacturer_Material_ID, iesaMaterialId: goldcsv.Material, wrWxId: goldcsv.WrWx_ID})
WITH goldcsv
WHERE goldcsv.Category IS NOT NULL
MERGE(c:Category {catName: goldcsv.Category})
WITH goldcsv
//WHERE goldcsv.Product_Attributes IS NOT NULL
MERGE(a:Attributes {prodDescription: goldcsv.Product_Description, attributes: goldcsv.Product_Attributes})
// create category to product relationships (rem row by row as csv loads)
WITH goldcsv
MATCH
(ca:Category {catName: goldcsv.Category}),
(pr:Product {prodDescription: goldcsv.Product_Description, type: goldcsv.Product_Type, manufacturer: goldcsv.Manuf, manufacturerId: goldcsv.Manufacturer_Material_ID, iesaMaterialId: goldcsv.Material, wrWxId: goldcsv.WrWx_ID}),
(at:Attributes {prodDescription: goldcsv.Product_Description, attributes: goldcsv.Product_Attributes})
CREATE
(ca)-[:HAS_PRODUCT]->(pr),
(pr)-[:HAS_ATTRIBUTES]->(at);
'''

with driver.session() as session:
    result = session.run(create_gold_query)
