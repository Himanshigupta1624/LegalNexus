from rest_framework import serializers
from .models import User,OTPLogin,PasswordResetCode
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['id','email','first_name','last_name','is_active','date_joined','mobile','storage_quota']
        read_only_fields=['id','date_joined']

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['email', 'mobile', 'first_name', 'last_name', 
                  'password', 'password_confirm']
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        return user

class OTPLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = OTPLogin
        fields = ['id', 'mobile', 'otp', 'created_at', 'is_verified', 'expires_at']
        read_only_fields = ['id', 'created_at', 'is_verified', 'expires_at']


class OTPRequestSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=15)


class OTPVerifySerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=15)
    otp = serializers.CharField(max_length=6)

class PasswordResetCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model=PasswordResetCode
        fields=['id','user','code','created_at']
        read_only_fields=['id','created_at']


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    code = serializers.CharField()
    new_password = serializers.CharField(min_length=8)


class EmailTokenObtainPairSerializer(serializers.Serializer):
    """Accepts email & password and returns access/refresh tokens."""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(request=self.context.get('request'), username=email, password=password)
        if not user:
            raise AuthenticationFailed('No active account found with the given credentials')
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
