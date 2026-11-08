import json
from unfold.components import BaseComponent

from django.db.models import Count

from apps.blogs.models import Category, Post, Statuses
from apps.auths.models import User


class BaseBarChartComponent(BaseComponent):

    MAX_HEIGHT: int = 320

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)

        labels = Category.objects.annotate(post_count=Count("posts"))

        context.update(
            {
                "height": self.MAX_HEIGHT,
                "data": json.dumps(
                    {
                        "labels": [label.name for label in labels],
                        "datasets": [
                            {
                                "data": [label.post_count for label in labels],
                                "type": "bar",
                                "backgroundColor": "var(--color-primary-200)",
                            },
                            
                        ],
                    }
                ),
            }
        )
        return context


class BaseTableComponent(BaseComponent):
     def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)

        top_5_users = User.objects.annotate(post_count=Count("posts")).order_by("-post_count")[:5]

        context.update(
            {
                "table": {
                    "collapsible": True,
                    "headers": ["First name", "Last name", "Email", "Post count"],
                    "rows": [
                        [user.first_name, user.last_name, user.email, user.post_count] 
                        for user in top_5_users 
                    ],
                }
            }
        )

        return context


class BaseProgressBarComponent(BaseComponent):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        published_count: int = Post.objects.filter(status=Statuses.PUBLISHED).count()
        total_count: int = Post.objects.count()

        context.update(
            {
                "title": "Published vs Draft",
                "description": f"Total: {published_count / total_count * 100}",
                "value": published_count / total_count * 100,
            }
        )

        return context