import os
import random
from google.cloud import bigquery
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
# Load from environment variables
PROJECT_ID = os.getenv("PROJECT_ID")
DATASET_ID = os.getenv("DATASET_ID")
TABLE_ID = os.getenv("TABLE_ID")

if not PROJECT_ID or not DATASET_ID or not TABLE_ID:
    print("Error: Ensure PROJECT_ID, DATASET_ID, and TABLE_ID are set in your .env file.")
    exit()

# --- 1. Initialize BigQuery Client ---
try:
    # Uses credentials set up in your environment (e.g., gcloud auth application-default login)
    client = bigquery.Client(project=PROJECT_ID)
except Exception as e:
    print(f"Error initializing BigQuery client. Ensure GOOGLE_APPLICATION_CREDENTIALS is set.")
    print(e)
    exit()

def create_dataset_and_get_table():
    """
    Creates the dataset and table if they do not exist.
    Returns the fully defined Table object, ensuring the schema is available for insertion.
    """
    dataset_ref = client.dataset(DATASET_ID)
    try:
        client.get_dataset(dataset_ref)
        print(f"Dataset {DATASET_ID} already exists.")
    except Exception:
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "US" # Choose your preferred region
        client.create_dataset(dataset)
        print(f"Dataset {DATASET_ID} created.")

    # Define the schema for the retail data
    schema = [
        bigquery.SchemaField("transaction_date", "DATE"),
        bigquery.SchemaField("customer_id", "STRING"),
        bigquery.SchemaField("product_id", "STRING"),
        bigquery.SchemaField("product_category", "STRING"),
        bigquery.SchemaField("sales_amount", "FLOAT"),
        bigquery.SchemaField("quantity", "INTEGER"),
        bigquery.SchemaField("region", "STRING"),
    ]

    table_ref = dataset_ref.table(TABLE_ID)
    table = bigquery.Table(table_ref, schema=schema)
    
    try:
        # Try to create the table
        created_table = client.create_table(table)
        print(f"Table {TABLE_ID} created.")
        return created_table # Return the newly created table object
    except Exception:
        # If creation fails (e.g., table already exists), fetch the existing table
        print(f"Table {TABLE_ID} setup check complete (Table likely exists).")
        # Explicitly get the table object with its full metadata/schema
        return client.get_table(table_ref)

def populate_data(table_object):
    """Inserts sample data rows using the provided BigQuery Table object."""
    
    rows_to_insert = []
    categories = ["Electronics", "Apparel", "Home Goods", "Books", "Outdoor"]
    regions = ["North", "South", "East", "West"]
    
    # Generate 500 rows of diverse sample data across 1 year
    for i in range(500):
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        date_str = f"2024-{month:02d}-{day:02d}"
        
        category = random.choice(categories)
        sales = round(random.uniform(5.00, 500.00), 2)
        qty = random.randint(1, 5)
        
        row = (
            date_str,
            f"CUST{random.randint(1000, 9999)}",
            f"PROD{random.randint(100, 999)}",
            category,
            sales,
            qty,
            random.choice(regions)
        )
        rows_to_insert.append(row)
    
    print(f"Inserting {len(rows_to_insert)} rows...")
    
    # Insert rows using the full table object
    # The table_object ensures the schema is known, resolving the ValueError
    errors = client.insert_rows(table_object, rows_to_insert)

    if errors:
        print("Encountered errors while inserting rows:", errors)
    else:
        print("Data insertion successful.")

if __name__ == "__main__":
    # Get the table object (creating it if necessary)
    retail_table = create_dataset_and_get_table()
    
    # Pass the complete table object to the population function
    populate_data(retail_table)
    
    print("\nBigQuery setup complete.")