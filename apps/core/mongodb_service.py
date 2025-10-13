"""
MongoDB Connection Service - Professional Implementation
======================================================
Handles MongoDB connections and operations using soft coding techniques.
Integrates with MangaDB database in MongoDB Compass.
"""

import pymongo
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
from decouple import config
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class MongoDBService:
    """
    Professional MongoDB service for MangaDB integration using soft coding.
    Supports both synchronous and asynchronous operations.
    """
    
    def __init__(self):
        # Soft coding configuration from environment
        self.db_name = config('MONGODB_NAME', default='MangaDB')
        self.host = config('MONGODB_HOST', default='localhost')
        self.port = config('MONGODB_PORT', default='27017', cast=int)
        self.username = config('MONGODB_USER', default='')
        self.password = config('MONGODB_PASSWORD', default='')
        
        # Connection string using soft coding
        self.connection_string = config('MONGODB_URL', default=self._build_connection_string())
        
        # Initialize connections
        self._sync_client = None
        self._async_client = None
        self._sync_db = None
        self._async_db = None
    
    def _build_connection_string(self):
        """Build MongoDB connection string using soft coded parameters."""
        if self.username and self.password:
            return f"mongodb://{self.username}:{self.password}@{self.host}:{self.port}/{self.db_name}"
        else:
            return f"mongodb://{self.host}:{self.port}/{self.db_name}"
    
    @property
    def sync_client(self):
        """Get synchronous MongoDB client with connection pooling."""
        if self._sync_client is None:
            try:
                self._sync_client = MongoClient(
                    self.connection_string,
                    serverSelectionTimeoutMS=5000,
                    connectTimeoutMS=10000,
                    socketTimeoutMS=10000,
                    maxPoolSize=50,
                    minPoolSize=5
                )
                # Test connection
                self._sync_client.admin.command('ping')
                logger.info(f"✅ MongoDB sync connection established: {self.db_name}")
            except Exception as e:
                logger.error(f"❌ MongoDB sync connection failed: {str(e)}")
                raise
        return self._sync_client
    
    @property
    def async_client(self):
        """Get asynchronous MongoDB client for async operations."""
        if self._async_client is None:
            try:
                self._async_client = AsyncIOMotorClient(
                    self.connection_string,
                    serverSelectionTimeoutMS=5000,
                    connectTimeoutMS=10000,
                    socketTimeoutMS=10000,
                    maxPoolSize=50,
                    minPoolSize=5
                )
                logger.info(f"✅ MongoDB async connection established: {self.db_name}")
            except Exception as e:
                logger.error(f"❌ MongoDB async connection failed: {str(e)}")
                raise
        return self._async_client
    
    @property
    def database(self):
        """Get synchronous database instance."""
        if self._sync_db is None:
            self._sync_db = self.sync_client[self.db_name]
        return self._sync_db
    
    @property
    def async_database(self):
        """Get asynchronous database instance."""
        if self._async_db is None:
            self._async_db = self.async_client[self.db_name]
        return self._async_db
    
    def get_collection(self, collection_name):
        """Get synchronous collection instance."""
        return self.database[collection_name]
    
    def get_async_collection(self, collection_name):
        """Get asynchronous collection instance."""
        return self.async_database[collection_name]
    
    def test_connection(self):
        """Test MongoDB connection and return database info."""
        try:
            # Test connection
            client = self.sync_client
            db = self.database
            
            # Get server info
            server_info = client.server_info()
            
            # Get database stats
            db_stats = db.command("dbStats")
            
            # Get collections
            collections = db.list_collection_names()
            
            connection_info = {
                'status': 'connected',
                'database': self.db_name,
                'host': self.host,
                'port': self.port,
                'server_version': server_info.get('version'),
                'collections_count': len(collections),
                'collections': collections,
                'database_size': db_stats.get('dataSize', 0),
                'storage_size': db_stats.get('storageSize', 0),
                'indexes_count': db_stats.get('indexes', 0)
            }
            
            logger.info(f"✅ MongoDB connection test successful: {self.db_name}")
            return connection_info
            
        except Exception as e:
            logger.error(f"❌ MongoDB connection test failed: {str(e)}")
            return {
                'status': 'failed',
                'error': str(e),
                'database': self.db_name,
                'host': self.host,
                'port': self.port
            }
    
    def close_connections(self):
        """Close all MongoDB connections."""
        if self._sync_client:
            self._sync_client.close()
            self._sync_client = None
            logger.info("🔐 MongoDB sync connection closed")
        
        if self._async_client:
            self._async_client.close()
            self._async_client = None
            logger.info("🔐 MongoDB async connection closed")

# Global MongoDB service instance
mongodb_service = MongoDBService()

# Convenience functions for easy access
def get_mongodb_collection(collection_name):
    """Get MongoDB collection using soft coding configuration."""
    return mongodb_service.get_collection(collection_name)

def get_async_mongodb_collection(collection_name):
    """Get async MongoDB collection using soft coding configuration."""
    return mongodb_service.get_async_collection(collection_name)

def test_mongodb_connection():
    """Test MongoDB connection and return status."""
    return mongodb_service.test_connection()