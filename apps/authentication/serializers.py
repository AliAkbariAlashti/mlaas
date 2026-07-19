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
