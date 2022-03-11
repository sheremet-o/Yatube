from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from users.forms import CreationForm
User = get_user_model()


class UserSignupFormTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.form = CreationForm()

    def test_create_user(self):
        '''Валидная форма создает запись в Users.'''
        user_count = User.objects.count()
        form_data = {
            'first_name': 'Тестовое имя',
            'last_name': 'Тестовая фамилия',
            'username': 'TestUser',
            'email': 'test@mail.ru',
            'password1': '5678test',
            'password2': '5678test'
        }

        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:index'))
        self.assertEqual(User.objects.count(), user_count + 1)
