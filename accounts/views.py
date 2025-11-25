# accounts/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from accounts.models import Hotel
from accounts.models import Booking
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, time

import random

from .models import CustomUser, Hotel, Ameneties, HotelImages, Payment
from .utils import generateSlug
from accounts.utils import generateRandomToken, sendEmailToken, sendOTPtoEmail


def login_page(request):
    """
    Generic login page used by both users and vendors (we detect by role after login).
    """
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, username=email, password=password)
        if user is None:
            messages.warning(request, "Invalid credentials or account does not exist.")
            return redirect("login_page")

        if not user.is_verified:
            messages.warning(request, "Account not verified.")
            return redirect("login_page")

        login(request, user)

        # Redirect according to role
        if user.is_vendor():
            return redirect('dashboard')  # vendor dashboard
        else:
            # normal user -> to index or user-home
            return redirect('index')

    return render(request, "login.html")


def register_page(request):
    """
    Register a regular user (role='user').
    """
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone_number = request.POST.get('phone_number')

        if CustomUser.objects.filter(Q(email=email) | Q(phone_number=phone_number)).exists():
            messages.warning(request, "Account exists with Email or Phone Number.")
            return redirect('register_page')

        user = CustomUser(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            role='user',
            email_token=generateRandomToken()
        )
        user.set_password(password)
        user.save()

        sendEmailToken(email, user.email_token, user_type='user')
        messages.success(request, "Verification email sent. Please check your inbox.")
        return redirect('register_page')

    return render(request, 'register.html')


def verify_email_token(request, token):
    user = CustomUser.objects.filter(email_token=token).first()
    if user:
        user.is_verified = True
        user.email_token = ''
        user.save()
        messages.success(request, "Email verified successfully. Please login.")
        return redirect('login_page')
    else:
        messages.error(request, "Invalid or expired token.")
        return redirect('register_user')


def send_otp(request, email):
    user = CustomUser.objects.filter(email=email).first()
    if not user:
        messages.warning(request, "No Account Found.")
        return redirect('login_page')

    otp = random.randint(1000, 9999)
    user.otp = str(otp)
    user.save()

    sendOTPtoEmail(email, otp)
    return redirect(f'/accounts/verify-otp/{email}/')


def verify_otp(request, email):
    if request.method == "POST":
        otp = request.POST.get('otp')
        user = get_object_or_404(CustomUser, email=email)

        if str(otp) == str(user.otp):
            # log the user in
            login(request, user)
            user.otp = ''
            user.save()
            messages.success(request, "Login Success")
            # redirect based on role
            if user.is_vendor():
                return redirect('dashboard')
            return redirect('index')

        messages.warning(request, "Wrong OTP")
        return redirect(f'/accounts/verify-otp/{email}/')

    return render(request, 'verify_otp.html')


def login_vendor(request):
    """
    Vendor-specific login page (optional). Works same as generic login.
    """
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        vendor = CustomUser.objects.filter(email=email, role='vendor').first()
        if not vendor:
            messages.error(request, "No vendor account found with this email.")
            return redirect('login_vendor')

        if not vendor.is_verified:
            messages.warning(request, "Please verify your email before logging in.")
            return redirect('login_vendor')

        user = authenticate(request, username=email, password=password)
        if user is not None and user.role == 'vendor':
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect('dashboard')

        messages.error(request, "Invalid credentials. Please try again.")
        return redirect('login_vendor')

    return render(request, 'vendor/login_vendor.html')


def register_vendor(request):
    """
    Register as vendor (role='vendor').
    """
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        business_name = request.POST.get('business_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone_number = request.POST.get('phone_number')

        if CustomUser.objects.filter(Q(email=email) | Q(phone_number=phone_number)).exists():
            messages.warning(request, "Account exists with Email or Phone Number.")
            return redirect('register_vendor')

        vendor = CustomUser(
            first_name=first_name,
            last_name=last_name,
            business_name=business_name,
            email=email,
            phone_number=phone_number,
            role='vendor',
            email_token=generateRandomToken()
        )
        vendor.set_password(password)
        vendor.save()

        sendEmailToken(email, vendor.email_token, user_type='vendor')
        messages.success(request, "An email sent to your email for verification.")
        return redirect('register_vendor')

    return render(request, 'vendor/register_vendor.html')


def verify_vendor_email(request, token):
    vendor = CustomUser.objects.filter(email_token=token, role='vendor').first()
    if vendor:
        vendor.is_verified = True
        vendor.email_token = ''
        vendor.save()
        messages.success(request, "Vendor email verified successfully. Please login.")
        return redirect('login_vendor')
    else:
        messages.error(request, "Invalid or expired token.")
        return redirect('register_vendor')


@login_required(login_url='login_vendor')
def dashboard(request):
    # ensure only vendors can access
    if not request.user.is_vendor():
        return HttpResponse("Unauthorized", status=403)

    hotels = Hotel.objects.filter(hotel_owner=request.user)
    context = {'hotels': hotels}
    return render(request, 'vendor/vendor_dashboard.html', context)


@login_required(login_url='login_vendor')
def add_hotel(request):
    if not request.user.is_vendor():
        return HttpResponse("Unauthorized", status=403)

    if request.method == "POST":
        vendor = request.user

        hotel_name = request.POST.get('hotel_name')
        hotel_description = request.POST.get('hotel_description')
        ameneties_list = request.POST.getlist('ameneties')
        hotel_price = request.POST.get('hotel_price')
        hotel_offer_price = request.POST.get('hotel_offer_price')
        hotel_location = request.POST.get('hotel_location')
        hotel_slug = generateSlug(hotel_name)

        hotel_obj = Hotel.objects.create(
            hotel_name=hotel_name,
            hotel_description=hotel_description,
            hotel_price=hotel_price or 0,
            hotel_offer_price=hotel_offer_price or 0,
            hotel_location=hotel_location,
            hotel_slug=hotel_slug,
            hotel_owner=vendor,
        )

        for amenity_id in ameneties_list:
            try:
                amenity = Ameneties.objects.get(id=amenity_id)
                hotel_obj.ameneties.add(amenity)
            except Ameneties.DoesNotExist:
                continue

        messages.success(request, "Hotel Created Successfully!")
        return redirect('add_hotel')

    ameneties = Ameneties.objects.all()
    return render(request, 'vendor/add_hotel.html', {'ameneties': ameneties})


@login_required(login_url='login_vendor')
def edit_hotel(request, slug):
    hotel_obj = get_object_or_404(Hotel, hotel_slug=slug)
    if request.user != hotel_obj.hotel_owner:
        return HttpResponse("You are not authorized", status=403)

    if request.method == "POST":
        hotel_obj.hotel_name = request.POST.get('hotel_name')
        hotel_obj.hotel_description = request.POST.get('hotel_description')
        hotel_obj.hotel_price = request.POST.get('hotel_price') or 0
        hotel_obj.hotel_offer_price = request.POST.get('hotel_offer_price') or 0
        hotel_obj.hotel_location = request.POST.get('hotel_location')
        hotel_obj.save()
        messages.success(request, "Hotel Details Updated")
        return HttpResponseRedirect(request.path_info)

    ameneties = Ameneties.objects.all()
    return render(request, 'vendor/edit_hotel.html', context={'hotel': hotel_obj, 'ameneties': ameneties})


@login_required(login_url='login_vendor')
def upload_images(request, slug):
    hotel_obj = get_object_or_404(Hotel, hotel_slug=slug)
    if request.user != hotel_obj.hotel_owner:
        return HttpResponse("You are not authorized", status=403)

    if request.method == "POST" and request.FILES.get('image'):
        image = request.FILES['image']
        HotelImages.objects.create(hotel=hotel_obj, image=image)
        return HttpResponseRedirect(request.path_info)

    return render(request, 'vendor/upload_images.html', context={'images': hotel_obj.hotel_images.all()})


@login_required(login_url='login_vendor')
def delete_image(request, id):
    hotel_image = get_object_or_404(HotelImages, id=id)
    if request.user != hotel_image.hotel.hotel_owner:
        return HttpResponse("You are not authorized", status=403)

    hotel_image.delete()
    messages.success(request, "Hotel Image deleted")
    return redirect('dashboard')



@login_required
def create_booking(request, slug):
    hotel = get_object_or_404(Hotel, hotel_slug=slug)

    if request.method == "POST":
        check_in = request.POST.get("check_in")
        check_out = request.POST.get("check_out")

        # Validate both dates selected
        if not check_in or not check_out:
            messages.error(request, "Please select both check-in and check-out dates.")
            return redirect(request.META.get("HTTP_REFERER"))

        # Convert to Python date objects
        start = datetime.strptime(check_in, "%Y-%m-%d").date()
        end = datetime.strptime(check_out, "%Y-%m-%d").date()

        # Validate range
        if end <= start:
            messages.error(request, "Check-out date must be AFTER check-in date.")
            return redirect(request.META.get("HTTP_REFERER"))

        # Calculate number of days
        num_days = (end - start).days

        # Total price calculation
        total_amount = hotel.hotel_offer_price * num_days

        # Real-time booking timestamp
        booking_time = timezone.now()

        # Exit time (checkout day at 11:00 AM)
        exit_dt = datetime.combine(end, time(11, 0))  
        exit_dt = timezone.make_aware(exit_dt)

        # Save the booking
        Booking.objects.create(
            user=request.user,
            hotel=hotel,
            booking_date=booking_time,
            check_in=start,
            check_out=end,
            total_price=total_amount,
            exit_time=exit_dt,
        )

        messages.success(request, "Booking successful!")
        return redirect("profile")

    return redirect("profile")


@login_required
def make_payment(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    # Create or update Payment
    payment, created = Payment.objects.get_or_create(
        booking=booking,
        defaults={
            'amount': booking.total_price,
            'payment_status': "Success",
            'payment_method': "Cash / Dummy Payment"
        }
    )

    messages.success(request, "Payment completed successfully!")
    return redirect("profile")
  


@login_required
def profile(request):
    bookings = Booking.objects.filter(user=request.user).select_related("hotel")
    return render(request, "profile.html", {"bookings": bookings})

@login_required
def delete_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    booking.delete()
    messages.success(request, "Booking deleted successfully.")
    return redirect("profile")


def logout_view(request):
    logout(request)
    return redirect('login_page')
