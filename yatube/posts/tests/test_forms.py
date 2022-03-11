import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.http import HttpResponseNotFound
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.forms import PostForm, CommentForm
from posts.models import Post, Group, Comment
from http import HTTPStatus
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Название тестовой группы',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
            image=cls.uploaded,
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Posts."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id,
            'image': self.uploaded,
        }

        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:profile', kwargs={
            'username': self.user.username}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст',
                group=self.group.id,
                image='posts/small.gif',
            ).exists()
        )

    def test_guest_client_cant_create_posts(self):
        '''Неавторизованный пользователь не может создавать посты.'''
        posts_count = Post.objects.count()
        response = self.guest_client.get(HttpResponseNotFound())
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Post.objects.count(), posts_count)

    def test_edit_post(self):
        '''Валидная форма изменяет пост в базе данных'''
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Измененный тестовый текст',
        }

        response = self.authorized_client.post(reverse(
            'posts:post_edit', args=({self.post.id})),
            data=form_data,
            follow=True)

        self.assertRedirects(
            response,
            reverse('posts:post_detail', args=({self.post.id})))
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                text='Измененный тестовый текст',
            ).exists()
        )
        self.assertEqual(response.status_code, 200)

    def test_guest_client_cant_edit_posts(self):
        '''Неавторизованный пользователь не может редактировать посты.'''
        response = self.guest_client.get(HttpResponseNotFound())
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)


class CommentFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Название тестовой группы',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Текст комментария',
        )
        cls.form = CommentForm()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_add_comment(self):
        '''Валидная форма создает запись в Comments.'''
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Текст нового комментария',
        }
        response = self.authorized_client.post(
           reverse('posts:add_comment', kwargs=({'post_id': self.post.id})),
            data=form_data,
            follow=True)
        self.assertRedirects(
            response,
            reverse('posts:post_detail', args=({self.post.id})))
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertTrue(
            Comment.objects.filter(
                text='Текст нового комментария',
                post=self.post.pk,
            ).exists()
        )

    def test_guest_client_cant_add_comments(self):
        '''Неавторизованный пользователь не может добавлять комментарии.'''
        comments_count = Comment.objects.count()
        response = self.guest_client.get(HttpResponseNotFound())
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Comment.objects.count(), comments_count)
