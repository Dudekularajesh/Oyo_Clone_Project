# from django.contrib.auth.backends import ModelBackend
# from django.contrib.auth import get_user_model

# UserModel = get_user_model()

# class EmailBackend(ModelBackend):
#     def authenticate(self, request, username=None, password=None, **kwargs):
#         email = kwargs.get('email', username)
#         try:
#             user = UserModel.objects.get(email=email)
#         except UserModel.DoesNotExist:
#             return None

#         if user.check_password(password):
#             return user
#         return None


from django.contrib.auth.backends import ModelBackend
from accounts.models import HotelUser

class HotelUserBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = HotelUser.objects.get(email=username)
        except HotelUser.DoesNotExist:
            return None

        if user.check_password(password):
            return user
        return None
