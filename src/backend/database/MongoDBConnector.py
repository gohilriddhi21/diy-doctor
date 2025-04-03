import yaml
from pymongo import MongoClient

class MongoDBConnector:
    def __init__(self, config_path: str):
        """
        Initialize MongoDB connection using credentials from a config file.
        :param config_path: Path to the YAML configuration file
        """
        with open(config_path, "r") as file:
            self.config = yaml.safe_load(file)
        
        uri = self.config["mongodb"]["uri"]
        self.client = MongoClient(uri)

    def get_collection(self, collection_key: str):
        """
        Get a collection from the database using collection key.
        :param collection_key: The key for the collection in config.yaml
        :return: The collection object
        """
        collection_name = self.config["mongodb"]["collections"].get(collection_key)
        if not collection_name:
            raise ValueError(f"Collection key '{collection_key}' not found in config.")
        return self.db[collection_name]
    
    def close_connection(self):
        """
        Close the database connection.
        """
        self.client.close()