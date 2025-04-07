import pandas as pd
from pymongo import MongoClient
import yaml
from pymongo.server_api import ServerApi

CONFIG_FILE_PATH = "config/config.yaml"  

# Read configuration from YAML file
def read_config():
    with open(CONFIG_FILE_PATH, 'r') as file:
        try:
            return yaml.safe_load(file)
        except yaml.YAMLError as e:
            print(f"Error reading YAML file: {e}")
            return None

# MongoDB connection and insertion
def connect_to_mongo():
    config_data = read_config()
    if config_data:
        print("Configuration data read successfully.")
        uri = config_data['mongodb']['uri']
        db_name = config_data['mongodb']['database_name']
        collection_name = config_data['mongodb']["collections"]["patient"]['patient_lab_reports_collection']
        print(f"Set MongoDB URI: {uri}")
        
        # Create a new client and connect to the server
        client = MongoClient(uri, server_api=ServerApi('1'))
        
        # Send a ping to confirm a successful connection
        try:
            client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
            db = client[db_name]
            collection = db[collection_name]
            return True, collection
        except Exception as e:
            print(f"Failed to connect to MongoDB: {e}")
            return False, None
    else:
        print("Failed to read configuration data.")
        return None

# Read CSV file into DataFrame and insert into MongoDB
def ingest_csv_to_mongo(csv_file_path, collection):
    try:
        # Read the CSV into a pandas DataFrame
        df = pd.read_csv(csv_file_path)
        
        # Convert DataFrame to dictionary (MongoDB format)
                # Select only the columns needed for insertion
        selected_columns = [
            'Patient_ID', 'WBC', 'LYMp', 'MONp', 'NEUp', 'EOSp', 'BASOp',
            'LYMn', 'MONn', 'NEUn', 'EOSn', 'BASOn', 'RBC', 'HGB', 
            'HCT', 'MCV', 'MCH', 'MCHC', 'RDWSD', 'RDWCV', 'PLT', 
            'MPV', 'PDW', 'PCT', 'PLCR', 'PLCC'
        ]
        
        df_filtered = df[selected_columns][:300]
        df_filtered['Patient_ID'] = df_filtered['Patient_ID'].astype(str)
        data = df_filtered.to_dict(orient='records')
        print("\ndata:\n", data)
        
        # Insert data into MongoDB
        if data:
            collection.insert_many(data)
            print(f'{len(data)} records inserted into MongoDB.')
            return True
        else:
            print('No data to insert into MongoDB.')
    except Exception as e:
        print(f"Error processing CSV: {e}")
    return False

def main():
    # CSV file path (replace with the actual path to your CSV file)
    csv_file_path = 'data/Patient_Lab_Report.csv'
    
    # Connect to MongoDB and get the collection
    val, collection = connect_to_mongo()
    if val:
        # Ingest the CSV data into MongoDB
        val = ingest_csv_to_mongo(csv_file_path, collection)
        if val:
            print("Data ingestion completed.")
        else:
            print("Failed to connect to MongoDB. Data ingestion aborted.")

if __name__ == "__main__":
    main()
