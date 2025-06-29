from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

class EmailBackend(ModelBackend):
    """
    Custom authentication backend that allows users to log in using their email address.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        
        if username is None or password is None:
            return None
            
        try:
            # Try to find a user with the given username or email
            user = UserModel._default_manager.get(
                Q(username__iexact=username) | 
                Q(email__iexact=username)
            )
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a non-existing user
            UserModel().set_password(password)
            return None
        else:
            # Verify the password and return the user if valid
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        return None
