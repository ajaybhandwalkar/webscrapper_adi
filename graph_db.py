# pip3 install neo4j-driver
# python3 example.py

from neo4j import GraphDatabase, basic_auth

AURA_CONNECTION_URI = "neo4j+s://0246395a.databases.neo4j.io"
AURA_USERNAME = "neo4j"
AURA_PASSWORD = "EA7mn5PARjI5Ey5mEryqMvEq4iEPuMoWrDM6MqhxEP0"
driver = GraphDatabase.driver(
    AURA_CONNECTION_URI,
    auth=basic_auth(AURA_USERNAME, AURA_PASSWORD))


def insert_record(name, partners, score, url=""):
    query = """
    MERGE (company:Company {name: $name, partners: $partners, partnerbaseScore: $score, url: $url})
    """
    with driver.session(database="neo4j") as session:
        session.execute_write(
            lambda tx: tx.run(query,
                              name=name,
                              partners=partners,
                              score=score,
                              url=url))


def create_relationship(child, parent, relation):
    try:
        # query = f"""
        # MATCH (a:Company {{name: $parent}}), (b:Company {{name: $child}}) MERGE (a)-[r:{relation}]->(b) RETURN a,b,r
        # """

        # query = f"""
        # MATCH (a:Company {{name: $parent}}), (b:Company {{name: $child}})
        # WHERE NOT (a)-[:{relation}]->(b) AND NOT (b)-[:{relation}]->(a)
        # MERGE (a)-[r:{relation}]->(b)
        # RETURN a,b,r
        # """
        # with driver.session(database="neo4j") as session:
        #     session.execute_write(
        #         lambda tx: tx.run(query, parent=parent, child=child))

        # query = f"""MATCH (a:Company {{Name: '{parent}'}}) MATCH (b:Company {{Name: '{child}'}}) MERGE (a)-[r:HAS_SUPPLIER]->(b) RETURN a, b, r"""

        query = f"""
        MATCH (a:Company), (b:Company)
        WHERE toLower(a.Name) = toLower('{parent}') AND toLower(b.Name) = toLower('{child}')
        MERGE (a)-[r:{relation}]->(b)
        RETURN a, b, r
        """

        with driver.session() as session:
            session.execute_write(
                lambda tx: tx.run(query))

    except Exception as e:
        print(e)


def get_all_records():
    query = "MATCH (c:Supplier)-[r]->(related) RETURN c, r, related"
    with driver.session(database="neo4j") as session:
        records = session.execute_read(lambda tx: [record for record in tx.run(query)])
        return [
            {
                "company": record["c"],
                "relationship": record["r"],
                "related": record["related"]
            }
            for record in records
        ]


if __name__ == '__main__':
    data = get_all_records()
    # with driver.session(database="neo4j") as session:
    #     c = session.execute_read(lambda tx: [record for record in tx.run("MATCH (c:Company) RETURN c")])
    #     print([i for i in c])
    # print(data)
