from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):

    LEN_POSTS: int = 15

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post
        post_title = post.text[:self.LEN_POSTS]
        group = PostModelTest.group
        group_title = group.title
        self.assertEqual(self.post.__str__(),
                         post_title, "Неверный вывод информации")
        self.assertEqual(self.group.__str__(),
                         group_title, "Неверный вывод информации123")
