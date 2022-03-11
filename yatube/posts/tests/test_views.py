import shutil
import tempfile

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.core.cache import cache

from posts.models import Group, Post, Follow

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Название тестовой группы',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
            image=uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post_page_uses_correct_template(self):
        '''URL-адрес использует шаблон create_post.html.'''
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_create_post_page_uses_correct_template(self):
        '''URL-адрес использует шаблон create_post.html.'''
        self.user = User.objects.get(username='HasNoName')
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.user)
        response = self.authorized_client_author.get(reverse(
            'posts:post_edit', kwargs={'post_id': f'{self.post.id}'}))
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_pages_uses_correct_template(self):
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse('posts:group_name', kwargs={
                'slug': 'test-slug'}),
            'posts/profile.html': reverse('posts:profile', kwargs={
                'username': 'HasNoName'}),
            'posts/post_detail.html': reverse('posts:post_detail', kwargs={
                'post_id': f'{PostPagesTests.post.id}'})}

        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        '''Шаблон index сформирован с правильным контекстом.'''
        response = self.guest_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author.username
        post_group_0 = first_object.group.title
        post_image_0 = first_object.image
        self.assertEqual(post_text_0, 'Тестовый текст')
        self.assertEqual(post_author_0, 'HasNoName')
        self.assertEqual(post_group_0, 'Название тестовой группы')
        self.assertEqual(post_image_0, 'posts/small.gif')

    def test_group_list_page_show_correct_context(self):
        '''Шаблон group_list сформирован с правильным контекстом.'''
        response = self.guest_client.get(reverse('posts:group_name', kwargs={
            'slug': 'test-slug'}))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author.username
        post_group_0 = first_object.group.title
        post_image_0 = first_object.image
        self.assertEqual(post_text_0, 'Тестовый текст')
        self.assertEqual(post_author_0, 'HasNoName')
        self.assertEqual(post_group_0, 'Название тестовой группы')
        self.assertEqual(post_image_0, 'posts/small.gif')

    def test_profile_page_show_correct_context(self):
        '''Шаблон profile сформирован с правильным контекстом.'''
        response = self.guest_client.get(reverse('posts:profile', kwargs={
            'username': 'HasNoName'}))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author.username
        post_group_0 = first_object.group.title
        post_image_0 = first_object.image
        self.assertEqual(post_text_0, 'Тестовый текст')
        self.assertEqual(post_author_0, 'HasNoName')
        self.assertEqual(post_group_0, 'Название тестовой группы')
        self.assertEqual(post_image_0, 'posts/small.gif')

    def test_post_detail_page_show_correct_context(self):
        '''Шаблон post_detail сформирован с правильным контекстом.'''
        response = self.guest_client.get(reverse('posts:post_detail', kwargs={
            'post_id': PostPagesTests.post.id}))
        self.assertEqual(response.context.get(
            'post_number').text, 'Тестовый текст')
        self.assertEqual(response.context.get(
            'post_number').author.username, 'HasNoName')
        self.assertEqual(response.context.get(
            'post_number').group.title, 'Название тестовой группы')
        self.assertEqual(
            response.context.get('post_number').image, 'posts/small.gif')

    def test_post_create_page_show_correct_context(self):
        '''Шаблон post_create сформирован с правильным контекстом.'''
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        '''Шаблон post_edit сформирован с правильным контекстом.'''
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': f'{self.post.id}'}))
        form_fields = {
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_cache(self):
        response = self.guest_client.get(reverse('posts:index'))
        initial_response = response.content
        post = Post.objects.get(pk=1)
        post.delete()
        response_after_delete = self.guest_client.get(reverse('posts:index'))
        response_cached = response_after_delete.content
        self.assertTrue(initial_response == response_cached)
        cache.clear()
        response_after_delete = self.guest_client.get(reverse('posts:index'))
        response_cached = response_after_delete.content
        self.assertTrue(initial_response != response_cached)

    def test_follow_new_post_show_up(self):
        follower = User.objects.create_user(username='AnotherUser')
        self.authorized_client = Client()
        self.authorized_client.force_login(follower)
        self.follow = Follow.objects.create(user=follower, author=self.user)
        response = self.authorized_client.get(reverse('posts:follow_index'))
        author_name = Follow.objects.filter(user=self.user)
        self.assertTrue(response.context['page_obj'].object_list, author_name)

    def test_unfollow_new_post_doesnt_show_up(self):
        follower = User.objects.create_user(username='AnotherUser')
        self.authorized_client = Client()
        self.authorized_client.force_login(follower)
        response = self.authorized_client.get(reverse('posts:follow_index'))
        author_name = Follow.objects.filter(user=self.user)
        self.assertFalse(response.context['page_obj'].object_list, author_name)

    def test_follow_and_unfollow_author(self):
        follows_count = Follow.objects.count()
        follower = User.objects.create_user(username='AnotherUser')
        self.authorized_client = Client()
        self.authorized_client.force_login(follower)
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertEqual(len(response.context["page_obj"]), 0)
        subscribtion = Follow.objects.create(user=follower, author=self.user)
        self.assertEqual(Follow.objects.count(), follows_count + 1)
        subscribtion.delete()
        self.assertEqual(len(response.context["page_obj"]), 0)
