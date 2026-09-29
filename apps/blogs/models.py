from django.db.models import (
    Model,
    CharField,
    SlugField,
    ForeignKey,
    TextField,
    ManyToManyField,
    DateTimeField,
    TextChoices,
    CASCADE,
    SET_NULL,
    UniqueConstraint,
)
from django.conf import settings


class Category(Model):
    """Category model."""

    MAX_NAME_LENGTH: int = 100

    name = CharField(max_length=MAX_NAME_LENGTH)
    slug = SlugField(default="")

    class Meta:
        constraints = [UniqueConstraint(fields=["slug"], name="unique_slug_category")]


class Tag(Model):
    """Tag model."""

    MAX_NAME_LENGTH: int = 50

    name = CharField(max_length=MAX_NAME_LENGTH)
    slug = SlugField(default="")

    class Meta:
        constraints = [UniqueConstraint(fields=["slug"], name="unique_slug_tag")]


class Statuses(TextChoices):
    DRAFT = "draft"
    PUBLISHED = "published"


class Post(Model):
    """Post model."""

    TITLE_MAX_LENGTH = 200
    STATUS_MAX_LENGTH = 10

    author = ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=CASCADE)
    title = CharField(max_length=TITLE_MAX_LENGTH)
    slug = SlugField()
    body = TextField(blank=True, default="")
    category = ForeignKey(to=Category, on_delete=SET_NULL, null=True)
    tags = ManyToManyField(to=Tag, blank=True, related_name="posts")
    status = CharField(max_length=STATUS_MAX_LENGTH, choices=Statuses.choices)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        constraints = [UniqueConstraint(fields=["slug"], name="unique_slug_post")]


class Comment(Model):
    post = ForeignKey(to=Post, on_delete=CASCADE)
    author = ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=CASCADE)
    body = TextField(blank=True, default="")
    created_at = DateTimeField(auto_now_add=True)
