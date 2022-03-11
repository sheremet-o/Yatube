from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

User = get_user_model()


class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = ('first_name', 'last_name', 'username', 'email')
        labels = {
            'first_name': _('Имя'),
            'last_name': _('Фамилия'),
            'username': _('Имя на сайте'),
            'email': _('Email')
        }
