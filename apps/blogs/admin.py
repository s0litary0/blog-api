from typing import Any
from unfold.admin import ModelAdmin, TabularInline
from unfold.sections import TableSection
from unfold.contrib.filters.admin import (
    RangeDateTimeFilter,
    FieldTextFilter,
    AutocompleteSelectFilter,
    ChoicesDropdownFilter,
    RelatedDropdownFilter,
    MultipleRelatedDropdownFilter
)
from unfold.contrib.forms.widgets import WysiwygWidget
from unfold.decorators import display, action
from unfold.enums import ActionVariant
from unfold.components import register_component

from django.urls import reverse_lazy
from django.contrib.admin import register
from django.utils.translation import gettext_lazy as _
from django.db.models import Count, TextField
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponseRedirect

from .models import (
    Category,
    Tag,
    Comment,
    Post,
    Statuses
)
from .components import BaseBarChartComponent, BaseTableComponent, BaseProgressBarComponent


class CategoryPostsTableSection(TableSection):
    """Unfold Category related Posts expandable table section"""

    TABLE_HEIGHT: int = 300

    verbose_name = _("Category posts")
    height = TABLE_HEIGHT
    related_name = "posts"
    fields = ["pk", "title", "author"]


class PostCommentsTableSection(TableSection):
    """Unfold Post related Comments expandable table section"""

    TABLE_HEIGHT: int = 300

    verbose_name = _("Post comments")
    height = TABLE_HEIGHT
    related_name = "comment_set"
    fields = ["pk", "author", "body"]


class CommentsTabularInline(TabularInline):
    model = Comment
    fields = ["author", "body"]
    extra = 0
    per_page = 10


@register(Category)
class CategoryAdmin(ModelAdmin):
    """Unfolrd Category ModelAdmin"""
    
    search_fields = ["name"]
    search_help_text = "Search by category name"
    list_display = ["name", "slug", "number_of_posts"]
    warn_unsaved_form = True
    list_fullwidth = True
    prepopulated_fields = {
        "slug": ("name", )
    }
    list_sections = [
        CategoryPostsTableSection
    ]

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        queryset = super().get_queryset(request)

        return queryset.annotate(post_count=Count("posts"))
    
    @display(label=True, ordering="post_count")
    def number_of_posts(self, obj: Category):
        return obj.post_count

@register(Tag)
class TagAdmin(ModelAdmin):
    """Unfolrd User ModelAdmin"""

    search_fields = ["name"]
    search_help_text = "Search by tag name"
    list_display = ["name", "slug", "number_of_posts"]
    warn_unsaved_form = True
    list_fullwidth = True
    prepopulated_fields = {
        "slug": ("name", )
    }

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        queryset = super().get_queryset(request)

        return queryset.annotate(post_count=Count("posts"))
    
    @display(label=True, ordering="post_count")
    def number_of_posts(self, obj: Tag):
        return obj.post_count


@register(Post)
class PostAdmin(ModelAdmin):
    """Unfolrd Post ModelAdmin"""

    search_fields = [
        "title",
        "body",
        "author__email"
    ]
    list_display = [
        "header",
        "post_status",
        "category__name",
        "comment_count",
        "post_tags",
        "created_at"
    ]
    list_select_related = ["author", "category"]
    list_filter = [
        ("status", ChoicesDropdownFilter),
        ("category", RelatedDropdownFilter),
        ("tags", MultipleRelatedDropdownFilter),
        ("author", AutocompleteSelectFilter),
        ("created_at", RangeDateTimeFilter)
    ]
    list_filter_submit = True
    actions = ["move_to_drafts", "publish_selected"]
    actions_list = ["publish_all_drafts"]
    actions_row = ["publish_draft_post"]
    actions_detail = ["view_post_comments"]
    actions_submit_line = ["save_and_publish"]
    list_sections = [
        PostCommentsTableSection
    ]
    autocomplete_fields = ["author", "category", "tags"]
    prepopulated_fields = {"slug": ["title"]}
    readonly_fields = [
        "created_at",
        "updated_at"
    ]
    formfield_overrides = {
        TextField: {
            "widget": WysiwygWidget
        }
    }
    inlines = [CommentsTabularInline]
    fieldsets = [
        (
            "Content",
            {
                "fields": ["title", "slug", "body"]
            }
        ),
        (
            "Classification",
            {
                "fields": ["category", "tags", "status"]
            }
        ),
        (
            "Meta",
            {
                "fields": ["author", "created_at", "updated_at"]
            }
        )
    ]
    warn_unsaved_form = True

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        queryset = super().get_queryset(request)
        return queryset.annotate(comment_count=Count("comment"))

    @display(
        description=_("Header"),
        header=True
    )
    def header(self, obj: Post):
        return [obj.title, obj.author]

    @display(
        description=_("Status"),
        label = {
            Statuses.DRAFT: "warning",
            Statuses.PUBLISHED: "success"
        }
    )
    def post_status(self, obj: Post) -> str:
        return obj.status

    @display(
        description=_("Comments count")
    )
    def comment_count(self, obj: Post):
        return obj.comment_count

    @display(
        dropdown=True
    )
    def post_tags(self, obj: Post):
        return {
            "title": "Tags dropdown",
            "striped": True,  
            "height": 200,  
            "width": 240,  
            "items": [
                {
                    "title": tag.name,
                }
                for tag in obj.tags.all()
            ],
        }

    @action(
        description=_("Publish selected")
    )
    def publish_selected(self, request: HttpRequest, queryset: QuerySet):
        queryset.update(status=Statuses.PUBLISHED)

    @action(
        description=_("Move to drafts")
    )
    def move_to_drafts(self, request: HttpRequest, queryset: QuerySet):
        queryset.update(status=Statuses.DRAFT)

    @action(
        description=_("Publish all drafts"),
        variant=ActionVariant.PRIMARY
    )
    def publish_all_drafts(self, request: HttpRequest):
        Post.objects.filter(status=Statuses.DRAFT).update(status=Statuses.PUBLISHED)
        return HttpResponseRedirect(reverse_lazy("admin:blogs_post_changelist"))

    @action(
        description=_("Change status"),
        variant=ActionVariant.INFO
    )
    def publish_draft_post(self, request: HttpRequest, object_id: int):
        obj = Post.objects.get(id=object_id)
        if obj.status == Statuses.DRAFT:
            obj.status = Statuses.PUBLISHED
        else:
            obj.status = Statuses.DRAFT

        obj.save()
        return HttpResponseRedirect(reverse_lazy("admin:blogs_post_changelist"))

    @action(
        description=_("View post comments")
    )
    def view_post_comments(self, request: HttpRequest, object_id: int):
        return HttpResponseRedirect(reverse_lazy("admin:blogs_comment_changelist") + f"?post__id__exact={object_id}")

    @action(
        description=_("Save and publish")
    )
    def save_and_publish(self, request: HttpRequest, obj: Post):
        obj.status = Statuses.PUBLISHED
        obj.save()

@register(Comment)
class CommentAdmin(ModelAdmin):
    """Unfolrd Comment ModelAdmin"""

    SHORTENED_BODY_LENGTH: int = 20

    list_display = [
        "post_title",
        "author",
        "shortened_body",
        "created_at"
    ]
    search_fields = [
        "body",
        "author__email",
        "post__title"
    ]
    list_filter = [
        ("post", AutocompleteSelectFilter), 
        ("author", AutocompleteSelectFilter), 
        ("created_at", RangeDateTimeFilter)
    ]
    autocomplete_fields = [
        "post",
        "author"
    ]
    list_filter_submit = True
    list_select_related = ["author", "post"]

    @display(ordering="title")
    def post_title(self, obj: Comment):
        return obj.post.title

    @display(ordering="body")
    def shortened_body(self, obj: Comment):
        return obj.body[:self.SHORTENED_BODY_LENGTH] + "..."


@register_component
class BarChartComponent(BaseBarChartComponent):
    ...


@register_component
class TableComponent(BaseTableComponent):
    ...


@register_component
class ProgressBarComponent(BaseProgressBarComponent):
    ...