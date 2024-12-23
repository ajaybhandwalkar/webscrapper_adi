from neo4j import GraphDatabase, basic_auth
import pandas as pd
import sys

AURA_CONNECTION_URI = "neo4j+s://0246395a.databases.neo4j.io"
AURA_USERNAME = "neo4j"
AURA_PASSWORD = "EA7mn5PARjI5Ey5mEryqMvEq4iEPuMoWrDM6MqhxEP0"
driver = GraphDatabase.driver(
    AURA_CONNECTION_URI,
    auth=basic_auth(AURA_USERNAME, AURA_PASSWORD))
if not driver.verify_authentication():
    print("Authentication Failed")
    sys.exit()

df = pd.read_excel("Analog Devices/demo.xlsx")
for row in df.iterrows():
    row = row[1]
    name, level, source= row["Name"], row["Level"], row["Source"]
    node = ""
    try:
        node = row["Relationship"]
    except:
        node = "Company"
    query = f"""
    MERGE (company: {node} {{name: $name, level: $level, source: $source}})
    """
    with driver.session(database="neo4j") as session:
        session.execute_write(
            lambda tx: tx.run(query,
                              name=name,
                              level=level,
                              source=source))

for row in df.iterrows():
    row = row[1]
    child = row["Name"]
    parent = row["Parent"]
    child_type= row["Relationship"]
    if (df["Parent"] == parent).any() and parent:
        parent_type = str(df.loc[df['Name'] == parent, 'Relationship']).split()[1]

        try:
            relation = row["Relationship"]
            query = f"""
            MATCH (a:{parent_type} {{name: $parent}}), (b:{child_type} {{name: $child}})
            WHERE NOT (a)-[:{relation}]->(b) AND NOT (b)-[:{relation}]->(a)
            MERGE (a)-[r:{relation}]->(b)
            RETURN a,b,r
            """
            with driver.session(database="neo4j") as session:
                session.execute_write(
                    lambda tx: tx.run(query, parent=parent, child=child))
        except Exception as e:
            pass
