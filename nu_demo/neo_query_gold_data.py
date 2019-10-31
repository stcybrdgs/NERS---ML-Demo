from neo4j import GraphDatabase
driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'devpass'))

with driver.session() as session:
    result = session.run('MATCH (c:Category)-[:HAS_PRODUCT]->(p:Product)-[:HAS_ATTRIBUTES]->(a:Attributes) WHERE c.catName = \'Bearing\' RETURN DISTINCT p.prodDescription AS Product, p.manufacturerId AS Manuf_Id, p.manufacturer as Manuf, a.attributes AS Attributes')

products = []
#for record in result:
    #print(record['Manuf'])
    #manufs.append({'record':record['Manuf']})

#print(manufs, '\n')
# Product	Manuf_Id	Manuf	Attributes
for record in result:
    print(record['Product'], record['Manuf_Id'], record['Manuf'], record['Attributes'])
    products.append(
        {
            'product':record['Product'],
            'manuf_id':record['Manuf_Id'],
            'manuf':record['Manuf'],
            'attributes':record['Attributes']
        }
    )

print('-------------------------')

print(products)




'''
MATCH (c:Category)-[:HAS_PRODUCT]->(p:Product) WHERE c.catName = \'Bearing\' RETURN DISTINCT p.manufacturer AS Manuf
MATCH (c:Category)-[:HAS_PRODUCT]->(p:Product) WHERE c.catName = 'Bearing' RETURN DISTINCT p.manufacturer AS Manuf
'''
