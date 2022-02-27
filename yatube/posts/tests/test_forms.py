from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, Group, User, Comment


class PostFormsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()

        cls.author = User.objects.create_user(username='test_author')
        cls.authorized_author = Client()
        cls.authorized_author.force_login(cls.author)

        cls.group = Group.objects.create(
            title='test_group_title',
            slug='test_group_slug',
            description='test_group_description',
        )

        cls.post = Post.objects.create(
            text='Тестовый пост',
            group=cls.group,
            author=cls.author,
        )

        cls.form_data_create = {
            'text': 'new_text',
            'group': cls.group.id,
            'username': cls.author.username,
        }

        cls.form_data_edit = {
            'post_id': cls.post.id,
            'text': 'editted_text',
            'group': cls.group.id,
            'author': cls.author,
        }

    def test_create_post(self):
        posts_count = Post.objects.count()

        response = self.authorized_author.post(
            reverse('posts:post_create'),
            data=self.form_data_create,
            follow=True,
        )

        self.assertRedirects(
            response, reverse('posts:profile', args=[self.author.username])
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)

        self.assertTrue(
            Post.objects.filter(
                group=self.group,
                text='new_text',
                author=self.author,
            ).exists()
        )

    def test_edit_post(self):

        posts_count = Post.objects.count()

        response = self.authorized_author.post(
            reverse('posts:post_edit', args=[self.post.id]),
            data=self.form_data_edit,
            follow=True,
        )
        self.assertRedirects(
            response, reverse('posts:post_detail', args=[self.post.id])
        )
        self.assertEqual(Post.objects.count(), posts_count)
        edit_post = Post.objects.latest('id')
        self.assertEqual(edit_post.text, 'editted_text')
        self.assertEqual(edit_post.author, self.author)
        self.assertEqual(edit_post.group, self.group)


class CommentsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='title',
            slug='slug',
            description='description'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='text'
        )
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_comments_from_user(self):
        """Комментировать посты может только авторизованный пользователь."""
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'new text',
        }
        self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data
        )
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data
        )
        self.assertEqual(Comment.objects.count(), comments_count + 1)

    def test_comments_appeared(self):
        """После успешной отправки комментарий появляется на странице поста."""
        form_data = {
            'text': 'new text',
        }
        self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data
        )
        response = self.authorized_client.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.id}
        ))
        comment = Comment.objects.get(id=1)
        self.assertIn(
            comment,
            response.context.get('comments')
        )
