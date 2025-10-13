"""
Serializers for REJLERS Backend authentication system
"""

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from .models import User, UserProfile


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    User registration serializer
    """
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = (
            'email', 'username', 'password', 'password_confirm',
            'first_name', 'last_name', 'company_name', 'job_title',
            'phone', 'industry', 'company_size', 'newsletter_subscribed'
        )
        extra_kwargs = {
            'username': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                "password": "Password fields didn't match."
            })
        return attrs
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    """
    User serializer for profile display
    """
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'company_name', 'job_title', 'phone', 'profile_picture', 'bio',
            'industry', 'company_size', 'newsletter_subscribed', 'marketing_emails',
            'email_verified', 'email_verified_at', 'last_login', 'date_joined',
            'is_active'
        )
        read_only_fields = (
            'id', 'email_verified', 'email_verified_at', 'last_login', 
            'date_joined', 'is_active'
        )


class UserProfileSerializer(serializers.ModelSerializer):
    """
    User profile serializer
    """
    user = UserSerializer(read_only=True)
    services_of_interest = serializers.StringRelatedField(many=True, read_only=True)
    industries_of_interest = serializers.StringRelatedField(many=True, read_only=True)
    services_of_interest_ids = serializers.PrimaryKeyRelatedField(
        many=True, 
        read_only=True,
        source='services_of_interest',
        required=False
    )
    industries_of_interest_ids = serializers.PrimaryKeyRelatedField(
        many=True, 
        read_only=True,
        source='industries_of_interest',
        required=False
    )
    
    class Meta:
        model = UserProfile
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set querysets for the foreign key fields
        from apps.core.models import ServiceCategory, IndustrySector
        self.fields['services_of_interest_ids'].queryset = ServiceCategory.objects.filter(is_active=True)
        self.fields['industries_of_interest_ids'].queryset = IndustrySector.objects.filter(is_active=True)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom token serializer with additional user data
    """
    username_field = 'email'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'] = serializers.EmailField()
        del self.fields['username']
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                username=email,
                password=password
            )
            
            if not user:
                raise serializers.ValidationError('Invalid email or password')
            
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            
            # Update attrs for parent validation
            attrs['username'] = user.username
            
        return super().validate(attrs)
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add custom claims
        token['email'] = user.email
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['company_name'] = user.company_name
        token['email_verified'] = user.email_verified
        
        return token


class ChangePasswordSerializer(serializers.Serializer):
    """
    Change password serializer
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(
        required=True, 
        validators=[validate_password]
    )
    new_password_confirm = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                "new_password": "Password fields didn't match."
            })
        return attrs


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Password reset request serializer
    """
    email = serializers.EmailField(required=True)


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Password reset confirmation serializer
    """
    token = serializers.UUIDField(required=True)
    new_password = serializers.CharField(
        required=True, 
        validators=[validate_password]
    )
    new_password_confirm = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                "new_password": "Password fields didn't match."
            })
        return attrs


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    User update serializer (for profile updates)
    """
    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'company_name', 'job_title',
            'phone', 'profile_picture', 'bio', 'industry', 'company_size',
            'newsletter_subscribed', 'marketing_emails'
        )
    
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance