from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class UsernameOrEmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
        try:
            user = User._default_manager.get_by_natural_key(username)
        except User.DoesNotExist:
            try:
                user = User._default_manager.get(email=username)
            except User.DoesNotExist:
                User().set_password(password)
        if user.check_password(password) and self.user_can_authenticate(user):
            return user