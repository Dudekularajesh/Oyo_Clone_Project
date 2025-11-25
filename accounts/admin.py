from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Ameneties, Hotel, HotelImages, HotelManager, HotelBooking

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email','first_name','last_name','role','is_verified','is_staff','is_superuser')
    ordering = ('email',)
    search_fields = ('email','first_name','last_name','phone_number')
    fieldsets = (
        (None, {'fields': ('email','password')}),
        ('Personal info', {'fields': ('first_name','last_name','phone_number','business_name','profile_picture')}),
        ('Permissions', {'fields': ('role','is_active','is_staff','is_superuser','groups','user_permissions')}),
        ('Important dates', {'fields': ('last_login','date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email','password1','password2','role', 'is_staff'),
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Ameneties)
admin.site.register(Hotel)
admin.site.register(HotelImages)
admin.site.register(HotelManager)
admin.site.register(HotelBooking)
