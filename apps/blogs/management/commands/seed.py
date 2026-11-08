from typing import Any
from random import choice, sample, randint, random
from time import perf_counter
from faker import Faker

from django.core.management.base import BaseCommand, CommandParser, CommandError
from django.contrib.auth.hashers import make_password
from django.utils.text import slugify

from apps.auths.models import User
from apps.blogs.models import (
    Post,
    Statuses,
    Tag,
    Comment,
    Category,
)


class Command(BaseCommand):
    """Seed Command to fill all project tables with fake data"""

    help = "Fill all tables with data"

    DEFAULT_USERS: int = 20
    DEFAULT_POSTS: int = 100
    DEFAULT_COMMENTS: int = 500
    DEFAULT_PASSWORD: str = "12345"
    EMAIL_DOMENS = [
        "kbtu.kz",
        "gmail.com",
        "mail.ru"
    ] 
    CATEGORIES_NAMES = [
        "Python",
        "Django",
        "DevOps",
        "Web Development",
        "Databases",
        "Testing",
        "Security",
        "Architecture",
    ]
    TAGS_NAMES = [
        "ORM",
        "Async",
        "REST API",
        "Docker",
        "Kubernetes",
        "CI/CD",
        "PostgreSQL",
        "Redis",
        "Celery",
        "Pytest",
        "Authentication",
        "Middleware",
        "Signals",
        "Forms",
        "Templates",
        "Performance",
        "Logging",
        "Deployment",
        "GraphQL",
        "WebSockets",
    ]

    def __delete_existing_data(self) -> None:
        """Delete existing data from all tables except superusers"""

        Comment.objects.all().delete()
        Post.objects.all().delete()
        Tag.objects.all().delete()
        Category.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()


    def __create_users(self, users_count: int, faker: Faker) -> int:
        """Create users and return number of created users"""

        if users_count < 0:
            raise CommandError("Users count must be >= 0")

        SEED_PASSWORD = make_password(self.DEFAULT_PASSWORD)
        
        users_to_create: list[User] = []
        used_emails: set[str] = set(User.objects.values_list("email", flat=True))

        for _ in range(users_count):
            first_name, last_name = faker.first_name(), faker.last_name()
            email: str = ".".join([first_name, last_name]).lower() + "@" + choice(self.EMAIL_DOMENS)

            if email in used_emails:
                continue

            is_active: bool = choice([True, False])
            is_staff: bool = choice([True, False])
            
            users_to_create.append(
                User(
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=SEED_PASSWORD,
                    is_active=is_active,
                    is_staff=is_staff
                )
            )
            used_emails.add(email)

        created_users_count: int = len(User.objects.bulk_create(users_to_create))
        return created_users_count

    def __create_categories(self) -> int:
        """Create categories and return number of created categories"""

        categories_to_create: list[Category] = []
        used_categories: set[str] = set(Category.objects.values_list("slug", flat=True))

        for name in self.CATEGORIES_NAMES:
            slug = slugify(name)

            if slug in used_categories:
                continue

            categories_to_create.append(
                Category(
                    name=name,
                    slug=slug
                )
            )
            used_categories.add(slug)

        created_categories_count: int = len(Category.objects.bulk_create(categories_to_create))
        return created_categories_count

    def __create_tags(self) -> int:
        """Create tags and return number of created tags"""

        tags_to_create: list[Tag] = []
        used_tags: set[str] = set(Tag.objects.values_list("slug", flat=True))

        for name in self.TAGS_NAMES:
            slug = slugify(name)
            
            if slug in used_tags:
                continue

            tags_to_create.append(
                Tag(
                    name=name,
                    slug=slug
                )
            )
            used_tags.add(slug)

        created_tags_count: int = len(Tag.objects.bulk_create(tags_to_create))
        return created_tags_count

    def __create_posts(self, posts_count: int, faker: Faker) -> int:
        """Create posts and return number of created posts"""

        MAX_POST_TAGS: int = 5
        MAX_POST_PARAGRPAHS: int = 5
        BEING_PUBLISHED_CHANCE: float = 0.7
        HAVING_CATEGORY_CHANCE: float = 0.9

        if posts_count < 0:
            raise CommandError("Posts count must be >= 0")

        posts_to_create: list[Post] = []
        used_slugs: set[str] = set(Post.objects.values_list("slug", flat=True))
        available_authors: list[User] = list(User.objects.all())
        available_tags: list[Tag] = list(Tag.objects.all())
        available_categories: list[Category] = list(Category.objects.all())

        if len(available_authors) <= 0: 
            raise CommandError("No authors exists to create post")

        for _ in range(posts_count):
            author: User = choice(available_authors)
            title: str = faker.sentence()
            slug: str = slugify(title)

            if slug in used_slugs:
                slug_count: int = 1
                while slug in used_slugs:
                    slug_count += 1
                    slug = slugify(f"{slug}-{slug_count}")

            body: str = "\n".join(faker.paragraphs(nb=randint(1, MAX_POST_PARAGRPAHS)))

            category: Category | None = None
            if random() < HAVING_CATEGORY_CHANCE:
                category = choice(available_categories)

            status: Statuses = Statuses.DRAFT
            if random() < BEING_PUBLISHED_CHANCE:
                status = Statuses.PUBLISHED   

            used_slugs.add(slug)

            posts_to_create.append(
                Post(
                    author=author,
                    title=title,
                    slug=slug,
                    body=body,
                    category=category,
                    status=status,
                )
            )

        created_posts: list[Post] = Post.objects.bulk_create(posts_to_create)

        for post in created_posts:
            tags: list[Tag] = sample(available_tags, k=randint(0, MAX_POST_TAGS))

            post.tags.set(tags)

        return len(created_posts)

    def __create_comments(self, comments_count: int, faker: Faker) -> int:
        """Create comments and return number of created comments"""

        if comments_count < 0:
            raise CommandError("Comments count must be >= 0")

        MAX_COMMENT_SENTENCES: int = 3

        comments_to_create: list[Comment] = []
        # duplicated comments are allowed
        # used_comments: set[tuple[int, int]] = set(Comment.objects.values_list("post", "author"))
        available_authors: list[User] = list(User.objects.all())
        available_posts: list[Post] = list(Post.objects.filter(status=Statuses.PUBLISHED))

        if len(available_authors) <= 0:
            raise CommandError("No authors exists to leave comment")
        if len(available_posts) <= 0:
            raise CommandError("No posts exists to leave comment")

        for _ in range(comments_count):
            post: Post = choice(available_posts)
            author: User = choice(available_authors)
            body: str = " ".join(faker.sentences(randint(1, MAX_COMMENT_SENTENCES)))

            comments_to_create.append(
                Comment(
                    post=post,
                    author=author,
                    body=body
                )
            )

        created_comments_count: int = len(Comment.objects.bulk_create(comments_to_create))
        return created_comments_count

    def add_arguments(self, parser: CommandParser) -> None:
        """Recieve command arguments"""
        parser.add_argument(
            "--users",
            type=int,
            default=self.DEFAULT_USERS,
            help="Number of users to create"
        )
        parser.add_argument(
            "--posts",
            type=int,
            default=self.DEFAULT_POSTS,
            help="Number of posts to create"
        )
        parser.add_argument(
            "--comments",
            type=int,
            default=self.DEFAULT_COMMENTS,
            help="Number of comments to create"
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete existing data before seeding"
        )

    def handle(self, *args: Any, **options: Any):
        """Command entry point"""

        start: float = perf_counter()
        faker: Faker = Faker()
    
        users_count: int = options["users"]
        posts_count: int = options["posts"]
        comments_count: int = options["comments"]
        shouldClear: bool = options["clear"]

        if shouldClear:
            self.__delete_existing_data()

        created_users_count: int = self.__create_users(users_count=users_count, faker=faker)
        created_categories_count: int = self.__create_categories()
        created_tags_count: int = self.__create_tags()
        created_posts_count: int = self.__create_posts(posts_count=posts_count, faker=faker)
        created_comments_count: int = self.__create_comments(comments_count=comments_count, faker=faker)

        end: float = perf_counter()

        message: str = f"""
Users:\t\t{created_users_count} created
Categories:\t{created_categories_count} created
Tags:\t\t{created_tags_count} created
Posts:\t\t{created_posts_count} created
Comments:\t{created_comments_count} created
Done in:\t{end - start} 
        """

        self.stdout.write(self.style.SUCCESS(message))