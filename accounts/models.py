from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, BaseUserManager


class CustomUserManager(BaseUserManager):
    """ Manager for CustomUser using email instead of username """

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    """
    Single user model for both normal users and vendors.
    Uses email as the USERNAME_FIELD.
    """

    USER_ROLE_CHOICES = (
        ('user', 'User'),
        ('vendor', 'Vendor'),
    )

    # remove unique username requirement
    username = models.CharField(max_length=150, blank=True, null=True)
    email = models.EmailField(unique=True)

    role = models.CharField(max_length=10, choices=USER_ROLE_CHOICES, default='user')

    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    business_name = models.CharField(max_length=200, null=True, blank=True)
    profile_picture = models.ImageField(upload_to="profile", null=True, blank=True)

    email_token = models.CharField(max_length=100, null=True, blank=True)
    otp = models.CharField(max_length=10, null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []   # no username needed

    objects = CustomUserManager()  # <<< important

    class Meta:
        db_table = 'custom_user'

    def __str__(self):
        return self.email

    def is_vendor(self):
        return self.role == 'vendor'

    def is_user(self):
        return self.role == 'user'



class Ameneties(models.Model):
    name = models.CharField(max_length=100)
    icon = models.ImageField(upload_to="hotels", null=True, blank=True)

    def __str__(self):
        return self.name


class Hotel(models.Model):
    hotel_name = models.CharField(max_length=100)
    hotel_description = models.TextField()
    hotel_slug = models.SlugField(max_length=191, unique=True)
    hotel_owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="hotels")
    ameneties = models.ManyToManyField(Ameneties, blank=True)
    hotel_price = models.FloatField()
    hotel_offer_price = models.FloatField(null=True, blank=True)
    hotel_location = models.TextField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.hotel_name


class HotelImages(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name="hotel_images")
    image = models.ImageField(upload_to="hotels")

    def __str__(self):
        return f"Image for {self.hotel.hotel_name}"


class HotelManager(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name="hotel_managers")
    manager_name = models.CharField(max_length=100)
    manager_contact = models.CharField(max_length=100)

    def __str__(self):
        return self.manager_name


class HotelBooking(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name="bookings")
    booking_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    booking_start_date = models.DateField()
    booking_end_date = models.DateField()
    price = models.FloatField()

    def __str__(self):
        # if no username, show email
        username = self.booking_user.username or self.booking_user.email
        return f"Booking for {self.hotel.hotel_name} by {username}"


class Booking(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    booking_date = models.DateTimeField(auto_now_add=True)

    check_in  = models.DateField(null=True, blank=True)
    check_out = models.DateField(null=True, blank=True)

    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    exit_time = models.DateTimeField(null=True, blank=True)

    def number_of_days(self):
        if self.check_in and self.check_out:
            return (self.check_out - self.check_in).days
        return 0

    def __str__(self):
        return f"{self.user} - {self.hotel}"

class Payment(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, default="Pending")  # Pending, Success, Failed
    payment_method = models.CharField(max_length=50, default="Online")
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.booking.id} - {self.payment_status}"
