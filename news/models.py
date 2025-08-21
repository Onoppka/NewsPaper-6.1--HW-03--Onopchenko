from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum

class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)

    def update_rating(self):


        # суммарный рейтинг каждой статьи автора умножается на 3
        posts_sum = self.post_set.all().aggregate(Sum('rating'))['rating__sum'] or 0
        posts_sum *= 3

        # суммарный рейтинг всех комментариев автора
        comments_sum = self.user.comment_set.all().aggregate(Sum('rating'))[
                           'rating__sum'] or 0

        # суммарный рейтинг всех комментариев к статьям автора
        all_comments_on_posts = sum(
            post.comment_set.all().aggregate(Sum('rating')).get('rating__sum') or 0 for
            post in self.post_set.all())

        # общий рейтинг автора
        total_rating = posts_sum + comments_sum + all_comments_on_posts
        self.rating = total_rating
        self.save()

    def __str__(self):
        return self.user.username


class Category(models.Model):
    category_name = models.CharField(max_length = 64, unique = True)

    def __str__(self):
        return self.category_name


class Post(models.Model):
    POST_TYPES = (
        ('article', 'Статья'),
        ('news', 'Новость')
    )
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    post_type = models.CharField(max_length=7, choices=POST_TYPES)
    created_at = models.DateTimeField(auto_now_add = True)
    categories = models.ManyToManyField(Category, through='PostCategory')
    title = models.CharField(max_length=255)
    content = models.TextField()
    rating = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.title.title()}: {self.content[:20]}'

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        if self.rating > 0:
            self.rating -= 1
        else:
            pass
        self.save()

    def preview(self):
        return f"{self.content[:124]}..."


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        if self.rating > 0:
            self.rating -= 1
        else:
            pass
        self.save()