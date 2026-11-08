from unfold.admin import ModelAdmin
from unfold.decorators import display, action
from unfold.contrib.filters.admin import BooleanRadioFilter
from unfold.forms import AdminPasswordChangeForm

from django.contrib.admin import site, register
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from django.db.models.query import QuerySet
from django.db.models import Count
from django.http import HttpRequest

from .models import User
from .forms import CustomUserChangeForm, CustomUserCreationForm


site.unregister(Group)


@register(User)
class UserAdmin(ModelAdmin):
    """Unfolrd User ModelAdmin"""
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    change_password_form = AdminPasswordChangeForm

    list_display = [
        "header",
        "active_status",
        "staff_status",
        "number_of_posts"
    ]
    search_fields = [
        "email"
    ]
    list_filter = [
        ("is_active", BooleanRadioFilter),
        ("is_staff", BooleanRadioFilter)
    ]
    list_filter_submit = True
    fieldsets = [
        (
            "Personal info",
            {
                "fields": ["first_name", "last_name", "email", "password"]
            }
        ),
        (
            "Permissions",
            {
                "fields": ["is_active", "is_staff"]
            }
        ),
        (
            "Important dates",
            {
                "fields": []
            }
        )
    ]
    add_fieldsets = [
        (
            None,
            {
                "fields": ["first_name", "last_name", "email", "password1", "password2"]
            }
        )
    ]
    ordering = ["email"]
    actions = ["activate_users", "deactivate_users"]

    @action(description=_("Activate selected users"))
    def activate_users(self, request: HttpRequest, queryset: QuerySet):
        queryset.update(is_active=True)

    @action(description=_("Deactivate selected users"))
    def deactivate_users(self, request: HttpRequest, queryset: QuerySet):
        queryset.update(is_active=False)

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        queryset = super().get_queryset(request)
        return queryset.annotate(post_count=Count("posts"))

    @display(header=True)
    def header(self, obj: User):
        full_name = f"{obj.first_name} {obj.last_name}"
        initials = f"{obj.first_name[0]}.{obj.last_name[0]}"

        return [full_name, obj.email, initials]

    @display(
        description=_("Active status"), 
        label = {
            "True": "success",
            "False": "danger"
        })
    def active_status(self, obj: User):
        return str(obj.is_active)

    @display(
        description=_("Staff status"), 
        label = {
            "True": "success",
            "False": "info"
        })
    def staff_status(self, obj: User):
        return str(obj.is_staff)
    
    @display(
        description=_("Post count"), 
        label=True, 
        ordering="post_count"
    )
    def number_of_posts(self, obj: User):
        return obj.post_count
    
@register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    """Unfolrd Group ModelAdmin"""
    ...