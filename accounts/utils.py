import uuid
from django.core.mail import send_mail
from django.conf import settings
from django.utils.text import slugify

from .models import Hotel, CustomUser


def generateRandomToken():
    return str(uuid.uuid4())


def sendEmailToken(email, token, user_type='user'):
    """
    Sends email verification link.
    User types:
        'user'   → normal user verification
        'vendor' → vendor verification
    """

    if user_type == 'vendor':
        verify_url = f"http://127.0.0.1:8000/accounts/vendor/verify-email/{token}/"
    else:
        verify_url = f"http://127.0.0.1:8000/accounts/verify-email/{token}/"

    subject = "Verify your Email Address"
    message = f"""
Hi,

Please click the link below to verify your email address:
{verify_url}

If you didn’t request this, please ignore this email.

Thank you,
Oyo Clone Support
"""

    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )


def sendOTPtoEmail(email, otp):
    subject = "OTP for Account Login"
    message = f"""Hi, use this OTP to login:

{otp}

Thank you,
Oyo Clone Support
"""

    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )


def generateSlug(hotel_name):
    slug = f"{slugify(hotel_name)}-" + str(uuid.uuid4()).split('-')[0]
    if Hotel.objects.filter(hotel_slug=slug).exists():
        return generateSlug(hotel_name)
    return slug


def get_logged_in_user(request):
    """
    Returns logged-in CustomUser using session key.
    Works for both user and vendor.
    """
    user_id = request.session.get("hotel_user_id")
    
    if user_id:
        try:
            return CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return None

    return None
