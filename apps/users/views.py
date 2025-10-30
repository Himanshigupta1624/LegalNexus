from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
import random

from .models import User, OTPLogin, PasswordResetCode
from .serializers import (
	UserSerializer,
	UserRegistrationSerializer,
	OTPLoginSerializer,
	PasswordResetCodeSerializer,
	OTPRequestSerializer,
	OTPVerifySerializer,
	PasswordResetRequestSerializer,
	PasswordResetConfirmSerializer,
	EmailTokenObtainPairSerializer,
)


class UserViewSet(viewsets.ModelViewSet):
	queryset = User.objects.all()
	serializer_class = UserSerializer
	permission_classes = [permissions.IsAuthenticated]

	def get_queryset(self):
		user = self.request.user
		if user.is_staff:
			return User.objects.all()
		return User.objects.filter(pk=user.pk)


class RegisterAPIView(APIView):
	permission_classes = [permissions.AllowAny]

	def post(self, request):
		serializer = UserRegistrationSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		user = serializer.save()
		return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class OTPRequestAPIView(APIView):
	permission_classes = [permissions.AllowAny]

	def post(self, request):
		serializer = OTPRequestSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		mobile = serializer.validated_data['mobile']

		otp = f"{random.randint(0, 999999):06d}"
		obj = OTPLogin.objects.create(mobile=mobile, otp=otp, expires_at=timezone.now() + timezone.timedelta(minutes=10))
		# In production you'd send OTP over SMS. For dev we return it in the response.
		out = OTPLoginSerializer(obj)
		return Response(out.data, status=status.HTTP_201_CREATED)


class OTPVerifyAPIView(APIView):
	permission_classes = [permissions.AllowAny]

	def post(self, request):
		serializer = OTPVerifySerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		mobile = serializer.validated_data['mobile']
		otp = serializer.validated_data['otp']

		qs = OTPLogin.objects.filter(mobile=mobile, otp=otp, is_verified=False)
		if not qs.exists():
			return Response({"detail": "invalid otp"}, status=status.HTTP_400_BAD_REQUEST)
		obj = qs.latest("created_at")
		if not obj.is_valid():
			return Response({"detail": "otp expired or already used"}, status=status.HTTP_400_BAD_REQUEST)
		obj.is_verified = True
		obj.save()
		out = OTPLoginSerializer(obj)
		return Response(out.data, status=status.HTTP_200_OK)


class PasswordResetRequestAPIView(APIView):
	permission_classes = [permissions.AllowAny]

	def post(self, request):
		serializer = PasswordResetRequestSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		email = serializer.validated_data['email']
		user = get_object_or_404(User, email=email)
		pr = PasswordResetCode.objects.create(user=user, expires_at=timezone.now() + timezone.timedelta(hours=24))
		# In production you'd email the code. For dev we return it in the response.
		out = PasswordResetCodeSerializer(pr)
		return Response(out.data, status=status.HTTP_201_CREATED)


class PasswordResetConfirmAPIView(APIView):
	permission_classes = [permissions.AllowAny]

	def post(self, request):
		serializer = PasswordResetConfirmSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		code = serializer.validated_data['code']
		new_password = serializer.validated_data['new_password']

		pr = get_object_or_404(PasswordResetCode, code=code, is_used=False)
		if not pr.is_valid():
			return Response({"detail": "code invalid or expired"}, status=status.HTTP_400_BAD_REQUEST)
		user = pr.user
		user.set_password(new_password)
		user.save()
		pr.is_used = True
		pr.save()
		return Response({"detail": "password reset successful"}, status=status.HTTP_200_OK)


class EmailTokenObtainPairAPIView(APIView):
	permission_classes = [permissions.AllowAny]

	def post(self, request):
		serializer = EmailTokenObtainPairSerializer(data=request.data, context={'request': request})
		serializer.is_valid(raise_exception=True)
		return Response(serializer.validated_data, status=status.HTTP_200_OK)

