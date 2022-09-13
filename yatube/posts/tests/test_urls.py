from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
            group=cls.group, pub_date='Дата публикации',
        )

    def setUp(self):
        self.guest_client = Client()
        self.author_post = Client()
        self.author_post.force_login(self.user)
        self.authorized_user = User.objects.create_user(username='НЕ АВТОР')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.authorized_user)

    def test_url_all_users(self):
        """Страницы доступна любому пользователю."""
        all_users = [
            '/',
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user}),
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})]
        for urls in all_users:
            response = self.guest_client.get(urls)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_authorized_users(self):
        """Страница доступна авторизованному пользователю."""
        authorized_user = [
            reverse('posts:post_create')
        ]
        for urls in authorized_user:
            response = self.authorized_client.get(urls)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_task_detail_url_redirect_anonymous(self):
        """Страница /posts:post_create/ перенаправляет анонимного
        пользователя.
        """
        response = self.guest_client.get('posts:post_create')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_url_post_author(self):
        """Страница доступна автору поста."""
        post_author = [
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        ]
        for urls in post_author:
            response = self.author_post.get(urls)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        """Проверка вызываемых HTML-шаблонов c правом доступа всем"""
        all_users = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            f'/profile/{PostModelTest.post.author}/': ('posts/profile.html'),
            f'/posts/{PostModelTest.post.id}/':
            ('posts/post_details.html'),
        }
        for address, template in all_users.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_authorized_correct_template(self):
        """Проверка вызываемых HTML-шаблонов c
           правом доступа авторизованным."""
        authorized_user = {'/create/': ('posts/create_post.html')}
        for address, template in authorized_user.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_author_correct_template(self):
        """Проверка вызываемых HTML-шаблонов c правом доступа автору."""
        reverse_post_for_edit = reverse(
            'posts:post_edit',
            kwargs={'post_id': self.post.id}
        )
        urls_set = {
            reverse_post_for_edit: 'posts/create_post.html'
        }
        for urls, template in urls_set.items():
            with self.subTest(urls=urls):
                response = self.author_post.get(urls)
                self.assertTemplateUsed(response, template)
