# Importing libraries
import pandas as pd
import snowflake.connector

import os
from dotenv import load_dotenv
load_dotenv()

# Load Snowflake credentials from environment variables
snowflake_details = {
    'user': os.getenv('snowflake_User'),
    'password': os.getenv('snowflake_Password'),
    'account': os.getenv('snowflake_Account'),
    'database': os.getenv('snowflake_Database'),
    'schema': os.getenv('snowflake_Schema'),
    'staging_area': os.getenv('snowflake_Staging_Area')
}


# Extract data from files
supply_chain_df = pd.read_excel('../data/raw/supply_chain_data.xlsx')

# ----- Transform data -----

# Transform the data
transformed_data = supply_chain_df.dropna()
transformed_data = transformed_data[transformed_data["Customer demographics"] != "Unknown"]

# Save the transformed data to CSV
transformed_data.to_csv('../data/processed/processed_data.csv', index=False)

# Load the data into Snowflake
snowflake_credentials = snowflake_details

# Name of the target table in Snowflake
target_table_name = "SUPPLY_CHAIN_TABLE"
csv_file_path = '../data/processed/processed_data.csv'

# ----- Load data into Snowflake -----

# Stage the local file into Snowflake staging area
staging_area = snowflake_credentials['staging_area']  # Replace with the appropriate staging area location in Snowflake
staging_file_name = 'processed_data.csv'  # Give the file a name in the staging area


# Establish a connection to Snowflake
conn = snowflake.connector.connect(
    user=snowflake_credentials['user'],
    password=snowflake_credentials['password'],
    account=snowflake_credentials['account'],
    database=snowflake_credentials['database'],
    schema=snowflake_credentials['schema']
)

# Create a cursor to execute SQL queries
cur = conn.cursor()

# Create the target table in Snowflake
create_table_query = f"""
CREATE OR REPLACE TABLE {target_table_name} (
    Product STRING,
    SKU STRING,
    Price STRING,
    Availability INTEGER,
    Number_of_products_sold INTEGER,
    Revenue_generated INTEGER,
    Customer_demographics STRING,
    Stock_levels INTEGER,
    Lead_times INTEGER,
    Order_quantities INTEGER,
    Shipping_times INTEGER,
    Shipping_carriers STRING,
    Shipping_costs INTEGER,
    Supplier_name STRING,
    Location STRING,
    Lead_time INTEGER,
    Production_volumes INTEGER,
    Manufacturing_lead_time INTEGER,
    Manufacturing_costs INTEGER,
    Inspection_results STRING,
    Defect_rates INTEGER,
    Transportation_modes STRING,
    Routes STRING,
    Costs INTEGER
);
"""
cur.execute(create_table_query)


stage_file_query = f"""
PUT file://{csv_file_path} {staging_area}/{staging_file_name}
"""
cur.execute(stage_file_query)


# Load the data from the staged file into the target table
copy_into_query = f"""
COPY INTO {target_table_name} 
FROM @{staging_area}/{staging_file_name}  -- Note the usage of '@' before the staging area location
FILE_FORMAT = (TYPE = CSV);
"""
cur.execute(copy_into_query)

# Commit the changes and close the connection
conn.commit()
cur.close()
conn.close()

print("Data loaded into Snowflake successfully!")
