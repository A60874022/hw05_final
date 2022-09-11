from http import HTTPStatus

from django import forms
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Follow, Group, Post

User = get_user_model()


class PostsPagesTests(TestCase):

    POSTS_AUTHORIZED: int = 2

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='Name')
        cls.group = Group.objects.create(
            title='test_title',
            description='test_description',
            slug='test-slug'
        )
        cls.post = Post.objects.create(
            text='test_post',
            author=cls.author,
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='2727')
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)
        self.user_2 = User.objects.create_user(
            username='Второй')
        self.authorized_author_2 = Client()
        self.authorized_author_2.force_login(self.user_2)

    def test_username(self):
        """view-функциях используются правильные html-шаблоны."""
        template_page_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse('posts:group_list',
                                             kwargs={'slug': 'test-slug'}),
            'posts/profile.html': reverse('posts:profile',
                                          kwargs={'username': 'Name'}),
            'posts/post_details.html': reverse('posts:post_detail',
                                               kwargs={'post_id':
                                                       self.post.id}),
            'posts/create_post.html': reverse('posts:post_edit',
                                              kwargs={'post_id':
                                                      self.post.id}),
        }
        for template, reverse_name in template_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_author.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_create_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_author.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_author.get(reverse('posts:post_edit',
                                                      kwargs={'post_id':
                                                              self.post.id}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_detail_show_correct_context(self):
        """Шаблон task_detail сформирован с правильным контекстом."""
        response = self.authorized_author.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}))
        self.assertEqual(response.context['post'].text, 'test_post')

    def test_post_another_group(self):
        """Пост не попал в другую группу"""
        reverse_index = reverse('posts:index')
        response_index = self.authorized_author.get(reverse_index)
        context_index = response_index.context.get('page_obj')
        self.assertNotIn(self.post.id, context_index)
        group_2 = Group.objects.create(
            title='Название',
            slug='address',
            description='Описание',
        )
        post_for_test = Post.objects.create(
            author=self.user_2,
            text='Text',
            group=group_2,
        )
        reverse_index = reverse('posts:index')
        response_index = self.authorized_author_2.get(reverse_index)
        context_index = response_index.context.get('page_obj')
        self.assertIn(post_for_test, context_index)

    def test_authorized_create_comment(self):

        """комментировать посты может только авторизованный пользователь."""
        self.authorized_author.post(reverse('posts:add_comment',
                                            kwargs={'post_id': self.post.id}))
        self.assertEqual(Post.objects.all().count(), self.POSTS_AUTHORIZED)


class PaginatorViewsTest(TestCase):
    NUMBER_PAGINATOR: int = 10
    NUMBER_PAGINATOR_1: int = 10

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.authorized_author = Client()
        cls.author = User.objects.create_user(username='NoName')
        cls.group = Group.objects.create(
            title='test_title',
            description='test_description',
            slug='test-slug'
        )

    def setUp(self):
        for post_temp in range(self.NUMBER_PAGINATOR):
            Post.objects.create(
                text=f'text{post_temp}', author=self.author, group=self.group
            )

    def test_first_page(self):
        """Проверка вывода первых 10 записей на первой странице"""
        templates_pages_names = {reverse('posts:index'),
                                 reverse('posts:group_list',
                                         kwargs={'slug': self.group.slug}),
                                 reverse('posts:profile',
                                         kwargs={'username': self.author})}
        for reverse_name in templates_pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                self.assertEqual(
                    len(response.context['page_obj']), self.NUMBER_PAGINATOR_1)


class CacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post = Post.objects.create(
            author=User.objects.create_user(username='test_name',
                                            password='test_pass',),
            text='Тестовая запись для создания поста')

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='123')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_cache_index(self):
        """Тест кэширования страницы index.html"""
        first_state = self.authorized_client.get(reverse('posts:index'))
        post_1 = Post.objects.get(pk=1)
        post_1.text = 'Измененный текст'
        post_1.save()
        second_state = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(first_state.content, second_state.content)
        cache.clear()
        third_state = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(first_state.content, third_state.content)


class FollowTests(TestCase):
    @classmethod
    def setUp(self):
        self.client_follower = Client()
        self.client_following = Client()
        self.user_follower = User.objects.create_user(username='follower',
                                                      password='3073')
        self.user_following = User.objects.create_user(username='following',
                                                       password='3073')
        self.post = Post.objects.create(
            author=self.user_following,
            text='Проверка теста')
        self.client_follower.force_login(self.user_follower)

    def test_follow(self):
        """Проверка , что авторизованный пользователь может подписываться."""
        self.client_follower.get(reverse('posts:profile_follow',
                                         kwargs={'username':
                                                 self.user_following.
                                                 username}))
        self.assertEqual(Follow.objects.all().count(), 1)

    def test_unfollow(self):
        """Проверка, что неавторизованный
        пользователь не может подписываться"""
        self.client_following.get(reverse('posts:profile_follow',
                                          kwargs={'username':
                                                  self.user_following.
                                                  username}))
        self.client_following.get(reverse('posts:profile_unfollow',
                                          kwargs={'username':
                                                  self.user_following.
                                                  username}))
        self.assertEqual(Follow.objects.all().count(), 0)

    def test_follow_lenta(self):
        """Проверка записи в ленте подписчиков"""
        Follow.objects.create(user=self.user_follower,
                              author=self.user_following)
        response = self.client_follower.get(reverse('posts:follow_index'))
        post_text_0 = response.context['page_obj'][0].text
        self.assertEqual(post_text_0, 'Проверка теста')
        response = self.client_following.get('posts:follow_index')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
