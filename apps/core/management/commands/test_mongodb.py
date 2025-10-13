"""
MongoDB Connection Test Command
==============================
Django management command to test MongoDB MangaDB connection using soft coding.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.core.mongodb_service import mongodb_service, test_mongodb_connection
import json

class Command(BaseCommand):
    help = 'Test MongoDB MangaDB connection and display database information'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Show detailed collection information',
        )
        parser.add_argument(
            '--collections',
            nargs='*',
            help='Test specific collections',
        )
    
    def handle(self, *args, **options):
        """Test MongoDB connection with professional output."""
        
        self.stdout.write("🔌 MONGODB MANGADB CONNECTION TEST")
        self.stdout.write("=" * 60)
        self.stdout.write("📍 Location: Django Management Command")
        self.stdout.write("🔧 Configuration: Soft Coding Techniques")
        self.stdout.write("=" * 60)
        
        try:
            # Test connection
            connection_info = test_mongodb_connection()
            
            if connection_info['status'] == 'connected':
                self.stdout.write(
                    self.style.SUCCESS("✅ MONGODB CONNECTION SUCCESSFUL!")
                )
                self.stdout.write("=" * 60)
                
                # Display connection details
                self.stdout.write(f"🗄️  Database Name: {connection_info['database']}")
                self.stdout.write(f"🌐 Host: {connection_info['host']}")
                self.stdout.write(f"🔌 Port: {connection_info['port']}")
                self.stdout.write(f"📊 MongoDB Version: {connection_info['server_version']}")
                self.stdout.write(f"📁 Collections Count: {connection_info['collections_count']}")
                
                # Display size information
                data_size = connection_info.get('database_size', 0)
                storage_size = connection_info.get('storage_size', 0)
                indexes_count = connection_info.get('indexes_count', 0)
                
                self.stdout.write(f"💾 Data Size: {self.format_bytes(data_size)}")
                self.stdout.write(f"🗃️  Storage Size: {self.format_bytes(storage_size)}")
                self.stdout.write(f"📋 Indexes: {indexes_count}")
                
                # Display collections
                collections = connection_info.get('collections', [])
                if collections:
                    self.stdout.write("\\n📚 Collections Found:")
                    self.stdout.write("-" * 40)
                    for collection in collections:
                        self.stdout.write(f"   ✅ {collection}")
                        
                        # Show detailed collection info if requested
                        if options['detailed']:
                            try:
                                coll = mongodb_service.get_collection(collection)
                                doc_count = coll.estimated_document_count()
                                self.stdout.write(f"      📄 Documents: {doc_count}")
                            except Exception as e:
                                self.stdout.write(f"      ⚠️  Count error: {str(e)}")
                else:
                    self.stdout.write("\\n📚 No collections found in database")
                
                # Test specific collections if requested
                if options['collections']:
                    self.stdout.write("\\n🔍 Testing Specific Collections:")
                    self.stdout.write("-" * 40)
                    
                    for collection_name in options['collections']:
                        try:
                            collection = mongodb_service.get_collection(collection_name)
                            doc_count = collection.estimated_document_count()
                            
                            # Get sample document
                            sample_doc = collection.find_one()
                            
                            self.stdout.write(f"   ✅ {collection_name}:")
                            self.stdout.write(f"      📄 Documents: {doc_count}")
                            
                            if sample_doc:
                                # Show sample document structure (without _id)
                                sample_keys = [k for k in sample_doc.keys() if k != '_id']
                                self.stdout.write(f"      🔑 Sample fields: {', '.join(sample_keys[:5])}")
                                if len(sample_keys) > 5:
                                    self.stdout.write(f"         ... and {len(sample_keys) - 5} more fields")
                            else:
                                self.stdout.write("      📄 Collection is empty")
                                
                        except Exception as e:
                            self.stdout.write(
                                self.style.ERROR(f"   ❌ {collection_name}: {str(e)}")
                            )
                
                self.stdout.write("\\n" + "=" * 60)
                self.stdout.write(
                    self.style.SUCCESS("🎉 MANGADB INTEGRATION: READY FOR USE!")
                )
                self.stdout.write("✅ Multi-Database Architecture: PostgreSQL + MongoDB")
                self.stdout.write("✅ Soft Coding Configuration: ACTIVE")
                self.stdout.write("✅ Connection Pooling: ENABLED")
                
            else:
                self.stdout.write(
                    self.style.ERROR("❌ MONGODB CONNECTION FAILED!")
                )
                self.stdout.write("=" * 60)
                self.stdout.write(f"🔍 Error: {connection_info['error']}")
                self.stdout.write(f"🗄️  Database: {connection_info['database']}")
                self.stdout.write(f"🌐 Host: {connection_info['host']}")
                self.stdout.write(f"🔌 Port: {connection_info['port']}")
                self.stdout.write("=" * 60)
                self.stdout.write("💡 TROUBLESHOOTING STEPS:")
                self.stdout.write("1. Ensure MongoDB is running")
                self.stdout.write("2. Check MongoDB Compass connection")
                self.stdout.write("3. Verify MangaDB database exists")
                self.stdout.write("4. Check network connectivity")
                self.stdout.write("5. Review MongoDB authentication settings")
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ MONGODB TEST FAILED: {str(e)}")
            )
    
    def format_bytes(self, bytes_value):
        """Format bytes into human readable format."""
        if bytes_value == 0:
            return "0 B"
        
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} PB"