import traceback

from graph_db import insert_record, create_relationship
import pandas as pd
from logger import init_logger

logger = init_logger()


partners_df = pd.read_excel("Analog Devices/Partnerbase_Partners.xlsx")
# partners_df.drop_duplicates(subset='Company', keep='first', inplace=True)
# partners_df = partners_df.groupby('Level').head(30).reset_index(drop=True)
# if not "Analog Devices" in partners_df["Company"].tolist():
#     insert_record('Analog Devices', "47 Partners", 88)
# for row in partners_df.iterrows():
#
#     row = row[1]
#     try:
#         insert_record(row["Company"], row["Partners"], row["Partnerbase Score"], row["URL/link"])
#     except Exception as e:
#         logger.error(f"Failed to create node {row}")
#         logger.error(traceback.print_exc())

for row in partners_df.iterrows():

    row = row[1]
    try:
        create_relationship(row["Company"], row["Level"], "PARTNER")
    except Exception as e:
        logger.error(f"Failed to create node {row}")
        logger.error(traceback.print_exc())















