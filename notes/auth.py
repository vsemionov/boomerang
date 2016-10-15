from django.contrib.auth.models import User
from allauth.account.adapter import DefaultAccountAdapter, app_settings
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


# email username generating adapter
class AccountAdapter(DefaultAccountAdapter):
    def populate_username(self, request, user):
        from allauth.account.utils import user_username, user_email, user_field
        first_name = user_field(user, 'first_name')
        last_name = user_field(user, 'last_name')
        email = user_email(user)
        username = user_username(user)
        if app_settings.USER_MODEL_USERNAME_FIELD:
            user_username(
                user,
                username or self.generate_unique_username([
                    email,
                    first_name,
                    last_name,
                    username,
                    'user']))


# social account connecting adapter
# adapted from:
# http://stackoverflow.com/questions/19354009/django-allauth-social-login-automatically-linking-social-site-profiles-using-th
class SocialAccountAdapter(DefaultSocialAccountAdapter):
    _verified_field = dict(google='verified_email', facebook='verified')

    def pre_social_login(self, request, sociallogin):
        """
        Invoked just after a user successfully authenticates via a
        social provider, but before the login is actually processed
        (and before the pre_social_login signal is emitted).

        We're trying to solve different use cases:
        - social account already exists, just go on
        - social account has no email or email is unknown, just go on
        - social account's email exists, link social account to existing user
        """

        # Ignore existing social accounts, just do this stuff for new ones
        if sociallogin.is_existing:
            return

        # some social logins don't have an email address, e.g. facebook accounts
        # with mobile numbers only, but allauth takes care of this case so just
        # ignore it
        if 'email' not in sociallogin.account.extra_data:
            return

        if not sociallogin.account.extra_data.get(self._verified_field.get(sociallogin.account.provider)):
            return

        # check if given email address already exists.
        # Note: __iexact is used to ignore cases
        try:
            email = sociallogin.account.extra_data['email'].lower()
            user = User.objects.get(email__iexact=email)

        # if it does not, let allauth take care of this new social account
        except User.DoesNotExist:
            return

        # if it does, connect this new social login to the existing user
        sociallogin.connect(request, user)
