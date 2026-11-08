from settings.conf import ENV_ID

from apps.auths.models import User
from apps.blogs.models import (
    Category, 
    Comment, 
    Post, 
    Tag,
    Statuses
)


def environment_callback(request):
    """Callback returning chosen environemt"""

    if ENV_ID == "local":  
        return ["Local", "warning"]  
    else:
        return ["Production", "danger"]

def dashboard_callback(request, context):

    total_users = len(User.objects.all())
    total_published_posts = Post.objects.filter(status=Statuses.PUBLISHED).count()
    total_drafted_posts = Post.objects.filter(status=Statuses.DRAFT).count()
    total_comments = len(Comment.objects.all())
    
    context.update(
        {
            "total_users": total_users,
            "total_published_posts": total_published_posts,
            "total_drafted_posts": total_drafted_posts,
            "total_comments": total_comments
        }
    )
    return context