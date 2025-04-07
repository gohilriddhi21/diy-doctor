import yaml
from pymongo import MongoClient
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MongoDBConnector:
    def __init__(self, config_file_path: str):
        self.config = self._read_config(config_file_path)     
        self.mongo_uri = self.config.get('mongodb', {}).get('uri') 
        self.database_name = self.config.get('mongodb', {}).get('database_name') 
        self.client = None # MongoDB client for connecting to MongoDB
        self.db = None # MongoDB database object which will be used to interact with the database
        self._connect()
    
    def _read_config(self, config_file):
        try:
            logger.info("Reading configuration file...")
            with open(config_file, 'r') as f:
                data = yaml.safe_load(f)
                logger.info("Config file read successfully")
                return data
        except FileNotFoundError:
            logger.error(f"Configuration file '{config_file}' not found.")
            return {}
        except yaml.YAMLError as e:
            logger.error(f"Error parsing configuration file '{config_file}': {e}")
            return {}

    def _connect(self):
        logger.info("Connecting to MongoDB...")
        if not self.mongo_uri or not self.database_name:
            logger.error("MongoDB URI or database name not found in configuration.")
            return

        try:
            self.client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=3000)
            self.client.admin.command("ping")  # Force connection check
            self.db = self.client[self.database_name]
            logger.info(f"Connected to MongoDB database: {self.database_name}")
        except Exception as e:
            logger.error(f"Error connecting to MongoDB: {e}")
            self.close()

    def close(self):
        try:
            logger.info("Closing MongoDB connection...")
            if self.client:
                self.client.close()
                self.client = None # Reset client to None after closing
                self.db = None # Reset db to None after closing
                logger.info("MongoDB connection closed.")
        except Exception as e:
            logger.error(f"Error closing MongoDB connection: {e}")