from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomUserBackend(ModelBackend):
    """Custom backend untuk authenticate user dengan field password_hash."""
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None
        
        # Django's set_password/check_password work with the `password` field
        # but our DB stores it in `password_hash` —  mapping sudah di-handle di model
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
