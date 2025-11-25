from django.urls import path
from . import views

urlpatterns = [

    # ----- USER AUTH -----
    path('login/', views.login_page, name='login_page'),
    path('register/', views.register_page, name='register_page'),
    path('verify-email/<str:token>/', views.verify_email_token, name='verify_email'),
    path('send-otp/<str:email>/', views.send_otp, name='send_otp'),
    path('verify-otp/<str:email>/', views.verify_otp, name='verify_otp'),

    # ----- VENDOR AUTH -----
    path('vendor/login/', views.login_vendor, name='login_vendor'),
    path('vendor/register/', views.register_vendor, name='register_vendor'),
    path('vendor/verify-email/<str:token>/', views.verify_vendor_email, name='verify_vendor_email'),

    # ----- VENDOR DASHBOARD + HOTEL MANAGEMENT -----
    path('vendor/dashboard/', views.dashboard, name='dashboard'),
    path('vendor/add-hotel/', views.add_hotel, name='add_hotel'),
    path('vendor/edit-hotel/<slug:slug>/', views.edit_hotel, name='edit_hotel'),
    path('vendor/upload-images/<slug:slug>/', views.upload_images, name='upload_images'),
    path('vendor/delete-image/<int:id>/', views.delete_image, name='delete_image'),

    path("book/<slug:slug>/", views.create_booking, name="create_booking"),
    path("profile/", views.profile, name="profile"),
    path("delete-booking/<int:booking_id>/", views.delete_booking, name="delete_booking"),
    path('payment/<int:booking_id>/', views.make_payment, name='make_payment'),






    # ----- LOGOUT -----
    path('logout/', views.logout_view, name='logout'),
]
