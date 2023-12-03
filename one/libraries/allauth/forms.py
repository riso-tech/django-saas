from allauth.account.forms import PasswordField, SignupForm
from allauth.socialaccount.forms import SignupForm as SocialSignupForm
from django.contrib.auth.password_validation import password_validators_help_texts
from django.utils.functional import lazy
from django.utils.html import format_html, format_html_join
from django.utils.translation import gettext_lazy as _


def _password_validators_help_text_html(password_validators=None):
    """
    Return an HTML string with all help texts of all configured validators
    in an <ul>.
    """
    help_texts = password_validators_help_texts(password_validators)
    help_items = format_html_join("", "<div class='text-muted'>{}</div>", ((help_text,) for help_text in help_texts))
    return format_html("{}", help_items) if help_items else ""


password_validators_help_text_html = lazy(_password_validators_help_text_html, str)


class UserSignupForm(SignupForm):
    """
    Form that will be rendered on a user sign up section/screen.
    Default fields will be added automatically.
    Check UserSocialSignupForm for accounts created from social.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"] = PasswordField(
            label=_("Password"),
            autocomplete="new-password",
            help_text=password_validators_help_text_html(),
        )


class UserSocialSignupForm(SocialSignupForm):
    """
    Renders the form when user has signed up using social accounts.
    Default fields will be added automatically.
    See UserSignupForm otherwise.
    """
