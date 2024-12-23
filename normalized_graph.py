import traceback

from graph_db import insert_record, create_relationship, driver
import pandas as pd
from logger import init_logger
from graph_db import get_all_records
from neo4j import GraphDatabase

logger = init_logger()


with driver.session(database="neo4j") as session:
    session.execute_write(
        lambda tx: tx.run('MERGE (company:Company {Name: "analog devices"})'))


def insert_or_update_data_from_multiple_dfs(dfs):
    try:
        with driver.session() as session:
            for df in dfs:
                for _, row in df.iterrows():
                    name, parent, relation = row['Name'].lower(), row['Parent'], row['Relation']
                    row.drop(labels=['Parent', 'Relation', "check"], errors='ignore')

                    properties = []
                    for col, val in row.items():
                        if col != 'Name':
                            val = val.replace("'", "\\'") if isinstance(val, str) else val

                            properties.append(f"SET n.`{col}` = coalesce(n.`{col}`, '') + ', {val}'")

                    cypher_query = f"MERGE (n:Company {{Name: '{name}'}}){' '.join(properties)}"
                    try:
                        session.run(cypher_query)
                        create_relationship(name, parent, relation)
                    except Exception as e:
                        print(name, parent, relation)
    except:
        print()


file_path = 'Analog Devices/normalized_demo2.xlsx'
excel_file = pd.ExcelFile(file_path)
df_list = [pd.read_excel(excel_file, sheet_name=sheet) for sheet in excel_file.sheet_names]
# df_list = [pd.read_excel(excel_file, sheet_name=sheet) for sheet in ['IG_importers', 'yfRisk', 'yf_officials']]
insert_or_update_data_from_multiple_dfs(df_list)

driver.close()