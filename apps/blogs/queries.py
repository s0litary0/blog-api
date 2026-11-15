from typing import Any
from re import escape
from datetime import date

from django.db.models import (
    QuerySet,
    Q,
    F,
    Value,
    Count,
    Max,
    Min,
    Avg,
    Case,
    When,
    Prefetch,
    Subquery,
    Exists,
    OuterRef,
)
from django.db.models.functions import Coalesce, Concat, TruncMonth
from django.utils import timezone as django_timezone
from django.utils.text import slugify

from apps.auths.models import User
from apps.blogs.models import Category, Tag, Post, Comment


# Level 1 — First Queries


def categories_by_name() -> QuerySet[Category]:
    """Get all categories, sorted by name A → Z"""

    return Category.objects.all().order_by("name")


def published_posts() -> QuerySet[Post]:
    """Get published posts, newest first"""

    return Post.objects.filter(status=Post.Statuses.PUBLISHED).order_by("-created_at")


def newest_published_posts() -> QuerySet[Post]:
    """Get the 5 newest published posts."""

    return Post.objects.filter(status=Post.Statuses.PUBLISHED).order_by("-created_at")[
        :5
    ]


def post_by_slug(slug: str) -> Post | None:
    """Get the post with this slug, or None if there is no such post. No exceptions"""

    try:
        return Post.objects.get(slug=slug)
    except Post.DoesNotExist:
        return None


def active_users_count() -> int:
    """Get number of active users. Staff users are not counted"""

    return User.objects.filter(is_staff=False).count()


def has_drafts() -> bool:
    """True if there is at least one draft post"""

    return Post.objects.filter(status=Post.Statuses.DRAFT).exists()


def published_posts_page(page: int) -> QuerySet[Post]:
    """
    One page of published posts, newest first.
    10 posts per page: page 1 is posts 1–10, page 2 is posts 11–20.
    """

    POSTS_PER_PAGE: int = 10

    return Post.objects.filter(status=Post.Statuses.PUBLISHED).order_by("-created_at")[
        (page - 1) * POSTS_PER_PAGE : (page - 1) * POSTS_PER_PAGE + POSTS_PER_PAGE
    ]


# Level 2 — Field Lookups


def posts_with_word_in_title(word: str) -> QuerySet[Post]:
    """Posts whose title contains word. Letter case does not matter."""

    return Post.objects.filter(title__iregex=rf"\b{escape(word)}\b")


def users_with_email_domain(domain: str) -> QuerySet[User]:
    """Users whose email ends with @ + domain, for example domain="example.com"""

    return User.objects.filter(email__iendswith=f"@{domain}")


def posts_without_category() -> QuerySet[Post]:
    """Posts that have no category."""

    return Post.objects.filter(category__isnull=True)


def categories_by_slugs(slugs: list[str]) -> QuerySet[Category]:
    """Categories whose slug is in the list slugs."""

    return Category.objects.filter(slug__in=slugs)


def posts_in_month(year: int, month: int) -> QuerySet[Post]:
    """Posts created in this month of this year."""

    return Post.objects.filter(created_at__year=year, created_at__month=month)


def posts_last_days(days: int) -> QuerySet[Post]:
    """Posts created in the last days days."""

    start = (django_timezone.now() - django_timezone.timedelta(days=days)).date()
    return Post.objects.filter(created_at__date__gte=start)


def posts_between(start: date, end: date) -> QuerySet[Post]:
    """
    Posts created from start to end.
    Posts from the start day and from the end day are both included.
    """

    return Post.objects.filter(created_at__date__range=(start, end))


# Level 3 — Queries Across Relations


def author_published_posts(email: str) -> QuerySet[Post]:
    """Published posts of the author with this email. Letter case of the email does not matter."""

    # return User.objects.get(email__iexact=email).posts | post_set
    return Post.objects.filter(author__email__iexact=email)


def posts_with_tag(tag_slug: str) -> QuerySet[Post]:
    """Posts that have the tag with this slug."""

    return Post.objects.filter(tags__slug=tag_slug).distinct()


def comments_in_category(category_slug: str) -> QuerySet[Comment]:
    """Comments on posts of the category with this slug."""

    return Comment.objects.filter(post__category__slug=category_slug).distinct()


def users_with_published_posts() -> QuerySet[User]:
    """Users who have at least one published post. Every user appears once."""

    return User.objects.filter(posts__status=Post.Statuses.PUBLISHED).distinct()


def posts_without_tags() -> QuerySet[Post]:
    """Posts that have no tags."""

    return Post.objects.filter(tags__isnull=True).distinct()


def users_without_comments() -> QuerySet[User]:
    """Users who have never written a comment."""

    return User.objects.filter(comment__isnull=True).distinct()


def posts_with_both_tags(first_slug: str, second_slug: str) -> QuerySet[Post]:
    """Posts that have both tags. A post with only one of them is not included."""

    return (
        Post.objects.filter(tags__slug=first_slug)
        .filter(tags__slug=second_slug)
        .distinct()
    )


# Level 4 — Q and F


def search_posts(text: str) -> QuerySet[Post]:
    """Posts that have text in the title or in the body. Letter case does not matter."""

    return Post.objects.filter(Q(title__icontains=text) | Q(body__icontains=text))


def published_posts_missing_info() -> QuerySet[Post]:
    """Published posts that have no category or no tags. Every post appears once."""

    return Post.objects.filter(
        Q(category__isnull=True) | Q(tags__isnull=True)
    ).distinct()


def edited_posts() -> QuerySet[Post]:
    """Posts that were edited more than 1 hour after they were created."""

    UPDATED_PERIOD_HOURS: int = 1

    return Post.objects.filter(
        updated_at__gt=F("created_at")
        + django_timezone.timedelta(hours=UPDATED_PERIOD_HOURS)
    )


def comments_by_post_author() -> QuerySet[Comment]:
    """Comments that the author of the post wrote under their own post."""

    return Comment.objects.filter(author=F("post__author"))


def comments_before_post() -> QuerySet[Comment]:
    """Comments created before their post. Must be empty if Part 1 is correct."""

    return Comment.objects.filter(created_at__lt=F("post__created_at"))


# Level 5 — values and values_list


def published_authors_emails() -> list[str]:
    """Emails of authors who have published posts. Unique, sorted A → Z. A plain list of strings."""

    return list(
        User.objects.filter(posts__status=Post.Statuses.PUBLISHED)
        .values_list("email", flat=True)
        .order_by("email")
        .distinct()
    )


def published_posts_overview() -> list[dict[str, Any]]:
    """
    One dict for each published post with exactly three keys:
    title, author_email, category_name.
    If a post has no category, category_name is "Uncategorized".
    """

    NO_CATEGORY_NAME: str = "Uncategorized"

    return list(
        Post.objects.filter(status=Post.Statuses.PUBLISHED).values(
            "title",
            author_email=F("author__email"),
            category_name=Coalesce("category__name", Value(NO_CATEGORY_NAME)),
        )
    )


# Level 6 — aggregate


def posts_stats() -> dict[str, Any]:
    """
    In one SQL query: the number of all posts, of published posts and of drafts,
    and the date of the first and of the last post.
    Keys: total, published, drafts, first_post_at, last_post_at.
    """

    return Post.objects.aggregate(
        total=Count("id"),
        published=Count("id", filter=Q(status=Post.Statuses.PUBLISHED)),
        drafts=Count("id", filter=Q(status=Post.Statuses.DRAFT)),
        first_post_at=Min("created_at"),
        last_post_at=Max("created_at"),
    )


def average_comments_per_post() -> float:
    """
    The average number of comments on a published post,
    rounded to 2 digits after the point.
    Posts with 0 comments count too.
    If there are no posts, return 0.0.
    """

    return round(
        Post.objects.filter(status=Post.Statuses.PUBLISHED)
        .annotate(comment_count=Count("comment"))
        .aggregate(comment_number_avg=Avg("comment_count", default=0))[
            "comment_number_avg"
        ],
        ndigits=2,
    )


# Level 7 — annotate


def categories_with_post_count() -> QuerySet[Category]:
    """Every category with post_count. Most posts first. Same count → sort by name."""

    return Category.objects.annotate(post_count=Count("posts")).order_by(
        "post_count", "name"
    )


def categories_with_published_count() -> QuerySet[Category]:
    """
    Every category with published_count, the number of its published posts.
    Categories with 0 published posts must be in the result too.
    """

    return Category.objects.annotate(
        published_count=Count("posts", filter=Q(posts__status=Post.Statuses.PUBLISHED))
    )


def top_authors() -> QuerySet[User]:
    """The top 5 users by number of published posts, with published_count."""

    return User.objects.annotate(
        published_count=Count("posts", filter=Q(posts__status=Post.Statuses.PUBLISHED))
    )[:5]


def popular_tags(min_posts: int) -> QuerySet[Tag]:
    """Tags used in at least min_posts posts, with post_count."""

    return Tag.objects.annotate(post_count=Count("posts")).filter(
        post_count__gte=min_posts
    )


def posts_per_status() -> list[dict[str, Any]]:
    """
    The number of posts for each status:
    [{"status": "draft", "count": 30},
    {"status": "published", "count": 70}].
    """

    return list(Post.objects.values("status").annotate(count=Count("id")))


def users_activity() -> QuerySet[User]:
    """Every user with post_count and comment_count. Both numbers must be correct."""

    return User.objects.annotate(
        post_count=Count("posts", distinct=True),
        comment_count=Count("comment", distinct=True),
    )


# Level 8 — Database Functions and Conditions


def search_users_by_full_name(text: str) -> QuerySet[User]:
    """
    Users whose full name ("First Last") contains text.
    Letter case does not matter. A search for "john smi" finds John Smith.
    Every user has full_name.
    """

    return User.objects.annotate(
        full_name=Concat("first_name", Value(" "), "last_name")
    ).filter(full_name__icontains=text)


def published_posts_per_month() -> list[dict[str, Any]]:
    """
    The number of published posts in each month:
    [{"month": ..., "count": 7}, ...], oldest month first.
    """

    return list(
        Post.objects.filter(status=Post.Statuses.PUBLISHED)
        .annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(count=Count("id"))
    )


def posts_with_popularity() -> QuerySet[Post]:
    """
    Every post with comment_count and popularity:
    "hot" for 10 comments or more, "normal" for 3 or more, "quiet" for less.
    """

    HOT_COMMENT_COUNT: int = 10
    NORMAL_COMMENT_COUNT: int = 3
    HOT_COMMENT: str = "hot"
    NORMAL_COMMENT: str = "normal"
    QUIET_COMMENT: str = "quiet"

    return Post.objects.annotate(comment_count=Count("comment")).annotate(
        popularity=Case(
            When(comment_count__gte=HOT_COMMENT_COUNT, then=Value(HOT_COMMENT)),
            When(comment_count__gte=NORMAL_COMMENT_COUNT, then=Value(NORMAL_COMMENT)),
            default=Value(QUIET_COMMENT),
        )
    )


# Level 9 — Changing Data


def get_or_create_tag(name: str) -> tuple[Tag, bool]:
    """
    Return the tag with this name. Create it (slug from the name) if it does not exist.
    The bool is True if the tag was created. Calling it twice must not create a second tag.
    """

    slug = slugify(name)
    return Tag.objects.get_or_create(name=name, slug=slug)


def publish_old_drafts(days: int) -> int:
    """All drafts older than days days become published, with one SQL query. Return how many posts changed."""

    current_datetime = django_timezone.now()
    start = current_datetime - django_timezone.timedelta(days=days)
    return Post.objects.filter(status=Post.Statuses.DRAFT, created_at__lt=start).update(
        status=Post.Statuses.PUBLISHED,
        updated_at=current_datetime,
    )


def tag_category_posts(category_slug: str, tag_slug: str) -> int:
    """
    Add the tag to every post of the category.
    A post that already has this tag must not get it twice.
    Return the number of posts in the category.
    """
    tag = Tag.objects.get(slug=tag_slug)
    posts = Post.objects.filter(category__slug=category_slug)

    for post in posts:
        post.tags.add(tag)
    return len(posts)


def merge_categories(source_slug: str, target_slug: str) -> int:
    """
    Move all posts of the source category to the target category,
    then delete the source category. Return how many posts moved.
    """
    category = Category.objects.get(slug=target_slug)

    posts_moved: int = Post.objects.filter(category__slug=source_slug).update(
        category=category
    )
    Category.objects.filter(slug=source_slug).delete()
    return posts_moved


def delete_inactive_users_comments() -> int:
    """Delete all comments written by inactive users. Return how many were deleted."""

    return Comment.objects.filter(author__is_active=False).delete()[0]


# Level 10 — select_related and prefetch_related


def published_feed() -> list[str]:
    """
    The 50 newest published posts as lines
    "title | author email | category name"
    (Uncategorized if there is no category).
    Exactly 1 SQL query.
    """

    PUBLISHED_POSTS_COUNT: int = 50
    NO_CATEGORY_NAME: str = 'Uncategorized'

    newest_published_posts = (
        Post.objects.select_related("author", "category")
        .values(
            "title", author_email=F("author__email"), category_name=F("category__name")
        )
        .filter(status=Post.Statuses.PUBLISHED)
        .order_by("-created_at")[:PUBLISHED_POSTS_COUNT]
    )

    return [
        f"{post['title']} | {post['author_email']} | {post['category_name'] or NO_CATEGORY_NAME}"
        for post in newest_published_posts
    ]


def newest_posts_with_tags() -> list[str]:
    """The 20 newest posts as lines "title: tag1, tag2". At most 2 SQL queries."""

    NEWEST_POSTS_COUNT: int = 20

    newest_posts = Post.objects.prefetch_related("tags").order_by("-created_at")[
        :NEWEST_POSTS_COUNT
    ]

    return [
        f"{post.title}: {', '.join([tag.name for tag in post.tags.all()])}"
        for post in newest_posts
    ]


def categories_with_published_posts() -> dict[str, list[str]]:
    """
    {category name: [titles of its published posts, newest first]}
    for every category. No drafts. At most 2 SQL queries.
    """
    published_posts = Post.objects.filter(status=Post.Statuses.PUBLISHED).order_by(
        "-created_at"
    )
    prefetch = Prefetch("posts", queryset=published_posts, to_attr="published_posts")
    categories = Category.objects.prefetch_related(prefetch).all()

    return {
        category.name: [post.title for post in category.published_posts]
        for category in categories
    }


# Level 11 — Subquery and Exists


def posts_with_last_comment() -> QuerySet[Post]:
    """
    Published posts. Each has last_comment:
    the body of its newest comment (None if there are no comments).
    """
    newest_comments = Comment.objects.filter(post=OuterRef("pk")).order_by(
        "-created_at"
    )
    return Post.objects.filter(status=Post.Statuses.PUBLISHED).annotate(
        last_comment=Subquery(newest_comments.values("body")[:1])
    )


def posts_with_staff_comments() -> QuerySet[Post]:
    """Posts with at least one comment from a staff user. Use Exists, not distinct()."""

    comments = Comment.objects.filter(post=OuterRef("pk"), author__is_staff=True)
    return Post.objects.filter(Exists(comments))


def users_with_draft_as_latest_post() -> QuerySet[User]:
    """Users whose newest post is a draft. Each user has latest_post_status."""

    newest_posts = Post.objects.filter(author=OuterRef("pk")).order_by("-created_at")
    return User.objects.annotate(
        latest_post_status=Subquery(newest_posts.values("status")[:1])
    ).filter(latest_post_status=Post.Statuses.DRAFT)


QUERIES = {
    1: categories_by_name,
    2: published_posts,
    3: newest_published_posts,
    4: post_by_slug,
    5: active_users_count,
    6: has_drafts,
    7: published_posts_page,
    8: posts_with_word_in_title,
    9: users_with_email_domain,
    10: posts_without_category,
    11: categories_by_slugs,
    12: posts_in_month,
    13: posts_last_days,
    14: posts_between,
    15: author_published_posts,
    16: posts_with_tag,
    17: comments_in_category,
    18: users_with_published_posts,
    19: posts_without_tags,
    20: users_without_comments,
    21: posts_with_both_tags,
    22: search_posts,
    23: published_posts_missing_info,
    24: edited_posts,
    25: comments_by_post_author,
    26: comments_before_post,
    27: published_authors_emails,
    28: published_posts_overview,
    29: posts_stats,
    30: average_comments_per_post,
    31: categories_with_post_count,
    32: categories_with_published_count,
    33: top_authors,
    34: popular_tags,
    35: posts_per_status,
    36: users_activity,
    37: search_users_by_full_name,
    38: published_posts_per_month,
    39: posts_with_popularity,
    40: get_or_create_tag,
    41: publish_old_drafts,
    42: tag_category_posts,
    43: merge_categories,
    44: delete_inactive_users_comments,
    45: published_feed,
    46: newest_posts_with_tags,
    47: categories_with_published_posts,
    48: posts_with_last_comment,
    49: posts_with_staff_comments,
    50: users_with_draft_as_latest_post
}
