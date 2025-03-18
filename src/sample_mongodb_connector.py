
import yaml
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

CONFIG_FILE_PATH =  "config/config.yaml"

def read_config():
    with open(CONFIG_FILE_PATH, 'r') as file:
        try:
            return yaml.safe_load(file)
        except yaml.YAMLError as e:
            print(f"Error reading YAML file: {e}")
            return None

def main():
    config_data = read_config()
    if config_data:
        print("Configuration data read successfully.")
        uri = config_data['mongodb']['uri']
        print(f"Set MongoDB URI: {uri}")
    else:
        print("Failed to read configuration data.")
        return

    # Create a new client and connect to the server
    client = MongoClient(uri, server_api=ServerApi('1'))

    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()