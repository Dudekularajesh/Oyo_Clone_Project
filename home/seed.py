from accounts.models import CustomUser, Hotel, Ameneties, HotelImages
from faker import Faker
import random
from django.core.files.base import ContentFile
import requests
from accounts.utils import generateSlug  # required for slug creation

fake = Faker()

# -------------------------
# 1. CREATE AMENITIES
# -------------------------
def create_amenities():
    amenities_list = [
        "Free WiFi",
        "Parking",
        "Power Backup",
        "Hot Water",
        "Lift",
        "Room Service",
        "AC",
        "TV",
        "CCTV",
        "Housekeeping",
    ]

    for item in amenities_list:
        Ameneties.objects.get_or_create(name=item)

    print("✔ Amenities inserted")


# -------------------------
# 2. CREATE FAKE VENDORS
# -------------------------
def create_vendors(n=10):
    for i in range(n):
        email = fake.unique.email()

        vendor = CustomUser(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=email,
            username=email,
            phone_number=str(random.randint(7000000000, 9999999999)),
            business_name=fake.company(),
            role="vendor",
            is_verified=True
        )

        vendor.set_password("123456")
        vendor.save()

    print(f"✔ {n} Vendors created")


# -------------------------
# 3. CREATE FAKE USERS
# -------------------------
def create_users(n=30):
    for i in range(n):
        email = fake.unique.email()

        user = CustomUser(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=email,
            username=email,
            phone_number=str(random.randint(6000000000, 9999999999)),
            role="user",
            is_verified=True
        )

        user.set_password("123456")
        user.save()

    print(f"✔ {n} Users created")


# -------------------------
# 4. CREATE HOTELS
# -------------------------
def create_hotels(n=20):
    vendors = list(CustomUser.objects.filter(role="vendor"))
    amenities = list(Ameneties.objects.all())

    if not vendors:
        print("❌ No vendors found — Run create_vendors() first!")
        return

    for i in range(n):
        vendor = random.choice(vendors)
        name = fake.company()

        hotel = Hotel.objects.create(
            hotel_name=name,
            hotel_description=fake.text(),
            hotel_slug=generateSlug(name),
            hotel_owner=vendor,
            hotel_price=random.randint(800, 8000),
            hotel_offer_price=random.randint(500, 6000),
            hotel_location=fake.city(),
            is_active=True
        )

        # Assign random amenities
        hotel.ameneties.set(random.sample(amenities, random.randint(3, len(amenities))))
        hotel.save()

    print(f"✔ {n} Hotels created")


# -------------------------
# 5. ADD IMAGES TO HOTELS
# -------------------------
def add_hotel_images():
    hotels = Hotel.objects.all()
    sample_image_url = "https://picsum.photos/640/480"

    for hotel in hotels:
        for i in range(3):  # add 3 images per hotel
            try:
                response = requests.get(sample_image_url, timeout=5)
                if response.status_code == 200:
                    img_name = f"{hotel.hotel_slug}_{i}.jpg"
                    HotelImages.objects.create(
                        hotel=hotel,
                        image=ContentFile(response.content, img_name)
                    )
            except:
                print("❌ Error downloading random image")

    print("✔ Hotel images added")


# -------------------------
# RUN ALL
# -------------------------
def run_all():
    print("⏳ Inserting Dummy Data...")
    create_amenities()
    create_vendors()
    create_users()
    create_hotels()
    add_hotel_images()
    print("🎉 All dummy data inserted successfully!")


# from home.seed import run_all
# run_all()