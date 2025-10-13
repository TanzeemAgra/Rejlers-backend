"""
Database Router for Multi-Database Architecture
==============================================
Handles routing between PostgreSQL (Railway) and MongoDB (MangaDB) using soft coding techniques.
"""

class DatabaseRouter:
    """
    Professional database router for multi-database architecture.
    Routes requests between PostgreSQL (default) and MongoDB (mangadb) databases.
    """
    
    # MongoDB apps and models
    MONGODB_APPS = ['manga', 'documents']
    MONGODB_MODELS = ['manga', 'chapter', 'collection', 'document']
    
    def db_for_read(self, model, **hints):
        """Suggest the database to read from."""
        # Route MongoDB models to mongoDB
        if model._meta.app_label in self.MONGODB_APPS:
            return 'mangadb'
        
        # Route specific models by name
        if model._name.lower() in self.MONGODB_MODELS:
            return 'mangadb'
        
        # Default to PostgreSQL
        return 'default'
    
    def db_for_write(self, model, **hints):
        """Suggest the database to write to."""
        # Route MongoDB models to MongoDB
        if model._meta.app_label in self.MONGODB_APPS:
            return 'mangadb'
        
        # Route specific models by name
        if model._name.lower() in self.MONGODB_MODELS:
            return 'mangadb'
        
        # Default to PostgreSQL
        return 'default'
    
    def allow_relation(self, obj1, obj2, **hints):
        """Allow relations if models are in the same database."""
        db_set = {'default', 'mangadb'}
        if obj1._state.db in db_set and obj2._state.db in db_set:
            return True
        return None
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Ensure that certain apps' models get created on the right database."""
        
        # MongoDB apps should only migrate to MongoDB
        if app_label in self.MONGODB_APPS:
            return db == 'mangadb'
        
        # MongoDB models should only migrate to MongoDB
        if model_name and model_name.lower() in self.MONGODB_MODELS:
            return db == 'mangadb'
        
        # Default apps should only migrate to PostgreSQL
        if db == 'mangadb':
            return False
        
        # Default database handles all other apps
        return db == 'default'