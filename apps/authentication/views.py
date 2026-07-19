from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import PhoneSerializer, ProfileSerializer, VerifyOTPSerializer
from .services import OTP_TTL_SECONDS, send_otp, verify_otp


class SendOTPView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = PhoneSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        send_otp(serializer.validated_data["phone_number"])
        return Response({
            "message": "OTP verification code sent successfully.",
            "expires_in_seconds": OTP_TTL_SECONDS,
        })


class VerifyOTPView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        if not verify_otp(data["phone_number"], data["otp_code"]):
            return Response({"detail": "Invalid or expired OTP code."}, status=status.HTTP_400_BAD_REQUEST)
        user, _ = User.objects.get_or_create(phone_number=data["phone_number"])
        refresh = RefreshToken.for_user(user)
        return Response({
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
            "is_profile_complete": user.is_profile_complete,
        })


class ProfileUpdateView(APIView):
    def put(self, request):
        serializer = ProfileSerializer(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"status": "success"})
