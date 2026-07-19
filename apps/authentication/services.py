from django.core.cache import cache

OTP_TTL_SECONDS = 120


def send_otp(phone_number: str) -> None:
    # TODO: Replace the fixed MVP OTP with an SMS provider and cryptographically random code.
    cache.set(f"otp:{phone_number}", "123456", OTP_TTL_SECONDS)


def verify_otp(phone_number: str, otp_code: str) -> bool:
    key = f"otp:{phone_number}"
    is_valid = cache.get(key) == otp_code
    if is_valid:
        cache.delete(key)
    return is_valid
