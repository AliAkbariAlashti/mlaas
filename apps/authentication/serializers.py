from rest_framework import serializers

from .models import User


class PhoneSerializer(serializers.Serializer):
    phone_number = serializers.RegexField(r"^\+?[0-9]{10,15}$", max_length=15)


class VerifyOTPSerializer(PhoneSerializer):
    otp_code = serializers.CharField(min_length=6, max_length=6)


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("company_name", "industry", "platform")

    def validate(self, attrs):
        if any(not attrs.get(field) for field in self.Meta.fields):
            raise serializers.ValidationError("All profile fields are required.")
        return attrs


class SendOTPResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    expires_in_seconds = serializers.IntegerField()


class TokenResponseSerializer(serializers.Serializer):
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()
    is_profile_complete = serializers.BooleanField()


class SuccessResponseSerializer(serializers.Serializer):
    status = serializers.CharField()


class UserDetailSerializer(serializers.ModelSerializer):
    is_profile_complete = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "phone_number",
            "company_name",
            "industry",
            "platform",
            "credit_limit",
            "date_joined",
            "is_profile_complete",
        )
        read_only_fields = ("id", "phone_number", "credit_limit", "date_joined", "is_profile_complete")
