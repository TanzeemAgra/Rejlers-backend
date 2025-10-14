from rest_framework import serializers
from .models import ProjectCategory, Client, Project, Task


class ProjectCategorySerializer(serializers.ModelSerializer):
    """Project category serializer"""
    
    class Meta:
        model = ProjectCategory
        fields = '__all__'
        read_only_fields = ('created_at',)


class ClientSerializer(serializers.ModelSerializer):
    """Client serializer"""
    
    class Meta:
        model = Client
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class ProjectSerializer(serializers.ModelSerializer):
    """Project serializer with nested relations"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    client_name = serializers.CharField(source='client.company_name', read_only=True)
    manager_name = serializers.CharField(source='manager.get_full_name', read_only=True)
    
    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'category', 'category_name',
            'client', 'client_name', 'manager', 'manager_name', 'status', 'priority',
            'budget', 'start_date', 'end_date', 'created_at', 'updated_at'
        ]
        read_only_fields = ('created_at', 'updated_at')


class TaskSerializer(serializers.ModelSerializer):
    """Task serializer"""
    project_name = serializers.CharField(source='project.name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'project', 'project_name', 'title', 'description',
            'assigned_to', 'assigned_to_name', 'status', 'due_date', 'created_at'
        ]
        read_only_fields = ('created_at',)