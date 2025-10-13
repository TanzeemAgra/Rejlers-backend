"""
Views for REJLERS Backend authentication system
"""

from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import uuid

from .models import User, UserProfile, EmailVerificationToken, PasswordResetToken
from .serializers import (
    UserRegistrationSerializer,
    UserSerializer,
    UserProfileSerializer,
    CustomTokenObtainPairSerializer,
    ChangePasswordSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer
)


class UserRegistrationView(generics.CreateAPIView):
    """
    User registration endpoint
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Create user profile
        UserProfile.objects.create(user=user)
        
        # Create email verification token
        token = EmailVerificationToken.objects.create(
            user=user,
            expires_at=timezone.now() + timedelta(hours=24)
        )
        
        # Send verification email (in production, use proper email templates)
        try:
            send_mail(
                subject='Welcome to REJLERS - Verify Your Email',
                message=f'''
                Welcome to REJLERS!
                
                Please verify your email by clicking this link:
                {settings.FRONTEND_URL}/verify-email/{token.token}
                
                This link will expire in 24 hours.
                
                Best regards,
                REJLERS Team
                ''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Email sending failed: {e}")
        
        # Generate tokens for immediate login
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'User registered successfully',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'verification_sent': True
        }, status=status.HTTP_201_CREATED)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom login endpoint with additional user data
    """
    serializer_class = CustomTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            # Get user data
            email = request.data.get('email')
            try:
                user = User.objects.get(email=email)
                response.data['user'] = UserSerializer(user).data
                
                # Update last login IP
                user.last_login_ip = self.get_client_ip(request)
                user.save(update_fields=['last_login_ip'])
                
            except User.DoesNotExist:
                pass
        
        return response
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Get and update user profile
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile


class ChangePasswordView(generics.UpdateAPIView):
    """
    Change user password
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            # Check old password
            if not user.check_password(serializer.data.get("old_password")):
                return Response({
                    'error': 'Invalid old password'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Set new password
            user.set_password(serializer.data.get("new_password"))
            user.save()
            
            return Response({
                'message': 'Password updated successfully'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmailVerificationView(APIView):
    """
    Verify email address
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        token_str = request.data.get('token')
        
        if not token_str:
            return Response({
                'error': 'Token is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            token = EmailVerificationToken.objects.get(
                token=token_str,
                used=False
            )
        except EmailVerificationToken.DoesNotExist:
            return Response({
                'error': 'Invalid or expired token'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if token.is_expired():
            return Response({
                'error': 'Token has expired'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Mark email as verified
        user = token.user
        user.verify_email()
        token.mark_used()
        
        return Response({
            'message': 'Email verified successfully'
        }, status=status.HTTP_200_OK)


class PasswordResetRequestView(generics.CreateAPIView):
    """
    Request password reset
    """
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        
        try:
            user = User.objects.get(email=email)
            
            # Create password reset token
            token = PasswordResetToken.objects.create(
                user=user,
                expires_at=timezone.now() + timedelta(hours=1),
                ip_address=self.get_client_ip(request)
            )
            
            # Send password reset email
            try:
                send_mail(
                    subject='REJLERS - Password Reset Request',
                    message=f'''
                    You have requested a password reset for your REJLERS account.
                    
                    Please click this link to reset your password:
                    {settings.FRONTEND_URL}/reset-password/{token.token}
                    
                    This link will expire in 1 hour.
                    
                    If you did not request this, please ignore this email.
                    
                    Best regards,
                    REJLERS Team
                    ''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True,
                )
            except Exception as e:
                print(f"Email sending failed: {e}")
            
        except User.DoesNotExist:
            # Don't reveal whether user exists for security
            pass
        
        return Response({
            'message': 'If the email exists, a password reset link has been sent'
        }, status=status.HTTP_200_OK)
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class PasswordResetConfirmView(generics.CreateAPIView):
    """
    Confirm password reset with token
    """
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        token_str = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']
        
        try:
            token = PasswordResetToken.objects.get(
                token=token_str,
                used=False
            )
        except PasswordResetToken.DoesNotExist:
            return Response({
                'error': 'Invalid or expired token'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if token.is_expired():
            return Response({
                'error': 'Token has expired'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Reset password
        user = token.user
        user.set_password(new_password)
        user.save()
        
        # Mark token as used
        token.mark_used()
        
        return Response({
            'message': 'Password reset successfully'
        }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_detail(request):
    """
    Get current user details
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """
    Logout user by blacklisting refresh token
    """
    try:
        refresh_token = request.data["refresh_token"]
        token = RefreshToken(refresh_token)
        token.blacklist()
        
        return Response({
            'message': 'Logged out successfully'
        }, status=status.HTTP_205_RESET_CONTENT)
    except Exception as e:
        return Response({
            'error': 'Invalid token'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def resend_verification_email(request):
    """
    Resend email verification
    """
    user = request.user
    
    if user.email_verified:
        return Response({
            'message': 'Email already verified'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Create new verification token
    token = EmailVerificationToken.objects.create(
        user=user,
        expires_at=timezone.now() + timedelta(hours=24)
    )
    
    # Send verification email
    try:
        send_mail(
            subject='REJLERS - Verify Your Email',
            message=f'''
            Please verify your email by clicking this link:
            {settings.FRONTEND_URL}/verify-email/{token.token}
            
            This link will expire in 24 hours.
            
            Best regards,
            REJLERS Team
            ''',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )
        
        return Response({
            'message': 'Verification email sent'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': 'Failed to send email'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)