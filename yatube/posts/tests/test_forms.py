import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse, reverse_lazy

from ..models import Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class TaskCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='Pushkin')

        cls.group = Group.objects.create(
            title='test_title',
            description='test_description',
            slug='test_slug'
        )

        cls.post = Post.objects.create(
            text='test_post',
            author=cls.author,
            group=cls.group,
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        """Создаем  пользователей."""
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_create_post(self):
        """Проверка создания поста в базе данных"""
        post_count = Post.objects.count()
        form_data = {'text': 'test_text',
                     'group': self.post.id}
        response = self.authorized_client.post(
            reverse_lazy('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:profile',
                             kwargs={'username': self.author}))
        self.assertEqual(Post.objects.count(), post_count + 1)

    def test_cant_create_existing_post(self):
        """Проверка редактирования поста"""
        post_2 = Post.objects.get(id=self.post.id)
        form_data = {
            'text': 'В лесу родилась елочка',
            'group': self.group.id
        }
        response_edit = self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={
                        'post_id': post_2.id
                    }),
            data=form_data,
            follow=True,
        )
        post_2 = Post.objects.get(id=self.post.id)
        self.assertEqual(response_edit.status_code, HTTPStatus.OK)
        self.assertEqual(post_2.text, 'В лесу родилась елочка')

    def test_post_with_picture(self):
        """при отправке поста с картинкой через форму PostForm
        создаётся запись в базе данных и выводится наглавную стараницу"""
        post_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'title': 'Тестовый заголовок',
            'text': 'Тестовый текст',
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('post:index'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse('post:index'))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                slug='Тестовый заголовок',
                text='Тестовый текст',
                image='tasks/small.gif'
            ).exists()
        )
