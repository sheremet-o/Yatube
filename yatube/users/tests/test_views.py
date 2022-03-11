from django.test import TestCase, Client
from django.urls import reverse
from django import forms


class UsersPagesTests(TestCase):

    def setUp(self):
        self.guest_client = Client()

    def test_signup_page_uses_correct_template(self):
        '''Страница signup использует шаблон users/signup.html.'''
        response = self.guest_client.get(reverse('users:signup'))
        self.assertTemplateUsed(response, 'users/signup.html')

    def test_signup_page_shows_correct_context(self):
        '''Шаблон signup сформирован с правильным контекстом'''
        response = self.guest_client.get(reverse('users:signup'))
        form_fields = {
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'username': forms.fields.CharField,
            'email': forms.fields.EmailField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
