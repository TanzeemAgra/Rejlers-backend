"""
Test API Views for Frontend-Backend Communication Verification
============================================================
Professional API endpoints for testing frontend-backend connectivity
using soft coding techniques and comprehensive response handling.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
from django.conf import settings
from apps.core.mongodb_service import mongodb_service, test_mongodb_connection
from django.contrib.auth.models import User
import json
from datetime import datetime

@api_view(['GET'])
@permission_classes([AllowAny])
def test_connection(request):
    """
    Test endpoint to verify basic API connectivity.
    Returns system status and connection information.
    """
    try:
        return Response({
            'status': 'success',
            'message': 'Backend API is operational',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'environment': settings.DEBUG and 'development' or 'production',
            'cors_enabled': True,
            'multi_database': True
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def test_database_status(request):
    """
    Test both PostgreSQL and MongoDB database connections.
    Returns detailed status for multi-database architecture.
    """
    try:
        # Test PostgreSQL connection
        postgres_status = {}
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT version(), current_database(), current_user;")
                pg_info = cursor.fetchone()
                cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")
                table_count = cursor.fetchone()[0]
                
                postgres_status = {
                    'status': 'connected',
                    'database': pg_info[1],
                    'user': pg_info[2],
                    'tables': table_count,
                    'type': 'PostgreSQL (Primary)'
                }
        except Exception as e:
            postgres_status = {
                'status': 'error',
                'message': str(e),
                'type': 'PostgreSQL (Primary)'
            }

        # Test MongoDB connection
        mongo_status = {}
        try:
            mongo_info = test_mongodb_connection()
            if mongo_info['status'] == 'connected':
                mongo_status = {
                    'status': 'connected',
                    'database': mongo_info['database'],
                    'version': mongo_info['server_version'],
                    'collections': mongo_info['collections_count'],
                    'type': 'MongoDB (Document)'
                }
            else:
                mongo_status = {
                    'status': 'error',
                    'message': mongo_info['error'],
                    'type': 'MongoDB (Document)'
                }
        except Exception as e:
            mongo_status = {
                'status': 'error',
                'message': str(e),
                'type': 'MongoDB (Document)'
            }

        return Response({
            'status': 'success',
            'message': 'Database status retrieved',
            'timestamp': datetime.now().isoformat(),
            'databases': {
                'postgresql': postgres_status,
                'mongodb': mongo_status
            },
            'architecture': 'Multi-Database (PostgreSQL + MongoDB)'
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def test_cors(request):
    """
    Test CORS configuration by returning request headers.
    Helps verify frontend-backend communication setup.
    """
    try:
        headers = dict(request.headers)
        
        return Response({
            'status': 'success',
            'message': 'CORS test endpoint',
            'timestamp': datetime.now().isoformat(),
            'request_info': {
                'method': request.method,
                'origin': headers.get('Origin', 'No origin header'),
                'user_agent': headers.get('User-Agent', 'Unknown'),
                'referer': headers.get('Referer', 'No referer'),
                'host': headers.get('Host', 'Unknown')
            },
            'cors_headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
            }
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def test_data_exchange(request):
    """
    Test data exchange between frontend and backend.
    Handles both GET requests and POST data processing.
    """
    try:
        if request.method == 'GET':
            # Return sample data from both databases
            sample_data = {
                'postgresql_sample': {
                    'users_count': User.objects.count(),
                    'sample_user': User.objects.first().username if User.objects.exists() else 'No users yet'
                },
                'mongodb_sample': {
                    'collections': [],
                    'sample_documents': {}
                }
            }
            
            # Get MongoDB sample data
            try:
                db = mongodb_service.get_database()
                collections = db.list_collection_names()
                sample_data['mongodb_sample']['collections'] = collections
                
                # Get sample documents from each collection
                for collection_name in collections[:3]:  # Limit to first 3 collections
                    collection = db[collection_name]
                    sample_doc = collection.find_one()
                    if sample_doc:
                        # Convert ObjectId to string for JSON serialization
                        if '_id' in sample_doc:
                            sample_doc['_id'] = str(sample_doc['_id'])
                        sample_data['mongodb_sample']['sample_documents'][collection_name] = sample_doc
            except Exception as mongo_error:
                sample_data['mongodb_sample']['error'] = str(mongo_error)

            return Response({
                'status': 'success',
                'message': 'Data exchange test - GET request',
                'timestamp': datetime.now().isoformat(),
                'data': sample_data
            }, status=status.HTTP_200_OK)
            
        elif request.method == 'POST':
            # Process POST data from frontend
            received_data = request.data
            
            return Response({
                'status': 'success',
                'message': 'Data exchange test - POST request processed',
                'timestamp': datetime.now().isoformat(),
                'received_data': received_data,
                'processed_by': 'Django Backend API',
                'confirmation': 'Data successfully received and processed'
            }, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)