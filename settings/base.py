import os

from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from settings.conf import * # noqa


# -----------------------------------------------------
# Path
# -----------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_URLCONF = "settings.urls"
WSGI_APPLICATION = "settings.wsgi.application"
ASGI_APPLICATION = "settings.asgi.application"

# -----------------------------------------------------
# Apps
# -----------------------------------------------------
DJANGO_AND_THIRD_PARTY_APPS = [
    "unfold",  # before django.contrib.admin
    "unfold.contrib.filters",  # optional, if special filters are needed
    "unfold.contrib.forms",  # optional, if special form elements are needed
    "unfold.contrib.inlines",  # optional, if special inlines are needed
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]
PROJECT_APPS = [
    "apps.auths.apps.AuthsConfig",
    "apps.blogs.apps.BlogsConfig"
]
INSTALLED_APPS = DJANGO_AND_THIRD_PARTY_APPS + PROJECT_APPS

# -----------------------------------------------------
# Middleware / Templates / Validators
# -----------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR + "/templates"
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# -----------------------------------------------------
# Internalization
# -----------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# -----------------------------------------------------
# Static / Media
# -----------------------------------------------------
STATIC_URL = "static/"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "auths.User"

# -----------------------------------------------------
# Unfold
# -----------------------------------------------------
UNFOLD = {
    "SITE_TITLE": "Admin panel",
    "SITE_HEADER": "Blog Admin",
    "SITE_SUBHEADER": "Blog API admin panel",
    "SITE_SYMBOL": "speed",
    "ENVIRONMENT": "apps.blogs.callbacks.environment_callback",
    "DASHBOARD_CALLBACK": "apps.blogs.callbacks.dashboard_callback",
    "SITE_DROPDOWN": [
        {
            "icon": "commit",
            "title": _("GitHub"),
            "link": "https://github.com/s0litary0/blog-api",
            "attrs": {
                "target": "_blank"
            }
        },
        {
            "icon": "file_open",
            "title": _("Unfold docs"),
            "link": "https://unfoldadmin.com/docs/",
            "attrs": {
                "target": "_blank"
            }
        }
    ],
    "COMMAND": {
        "search_models": True,
        # "search_callback": "apps.blogs.callbacks.search_callback",
        "show_history": True
    },
    "SIDEBAR": {
        "show_search": True, 
        "show_all_applications": True,  
        "navigation": [
            {
                "title": _("Overview"),
                "separator": True, 
                "collapsible": False,  
                "items": [
                    {
                        "title": _("Dashboard"),
                        "icon": "dashboard",  # Supported icon set: https://fonts.google.com/icons
                        "link": reverse_lazy("admin:index"),
                        "link_attrs": {
                            "title": "Dashboard",
                        },
                    }
                ],
            },
            {
                "title": _("Content"),
                    "separator": True, 
                    "collapsible": False,  
                    "items": [
                        {
                            "title": _("Posts"),
                            "icon": "post",  # Supported icon set: https://fonts.google.com/icons
                            "link": reverse_lazy("admin:blogs_post_changelist"),
                            "link_attrs": {
                                "title": "Posts",
                            },
                        },
                        {
                            "title": _("Comments"),
                            "icon": "comment",  # Supported icon set: https://fonts.google.com/icons
                            "link": reverse_lazy("admin:blogs_comment_changelist"),
                            "link_attrs": {
                                "title": "Comments",
                            },
                            
                        },
                        {
                            "title": _("Categories"),
                            "icon": "category",  # Supported icon set: https://fonts.google.com/icons
                            "link": reverse_lazy("admin:blogs_category_changelist"),
                            "link_attrs": {
                                "title": "Categories",
                            },
                        },
                        {
                            "title": _("Tags"),
                            "icon": "tag",  # Supported icon set: https://fonts.google.com/icons
                            "link": reverse_lazy("admin:blogs_tag_changelist"),
                            "link_attrs": {
                                "title": "Tags",
                            },
                        }
                    ]
            },
            {
                "title": _("Users & Access"),
                    "separator": True, 
                    "collapsible": False,  
                    "items": [
                        {
                            "title": _("Users"),
                            "icon": "account_circle",  # Supported icon set: https://fonts.google.com/icons
                            "link": reverse_lazy("admin:auths_user_changelist"),
                            "link_attrs": {
                                "title": "Users",
                            },
                            "permission": lambda request: request.user.is_superuser,
                        }
                    ]
            }
        ],
    },
    "TABS": [
        {
            "models": [
                "blogs.post",
            ],
            "items": [
                {
                    "title": _("Draft"),
                    "link": reverse_lazy("admin:blogs_post_changelist"),
                },
                {
                    "title": _("Published"),
                    "link": reverse_lazy("admin:blogs_post_changelist"),
                },
            ],
        },
    ],
    "COLORS": {
        "primary": {
            "50":  "oklch(98.7% 0.022 95.277)",
            "100": "oklch(96.2% 0.059 95.617)",
            "200": "oklch(92.4% 0.12 95.746)",
            "300": "oklch(87.9% 0.169 91.605)",
            "400": "oklch(82.8% 0.189 84.429)",
            "500": "oklch(76.9% 0.188 70.08)",
            "600": "oklch(66.6% 0.179 58.318)",
            "700": "oklch(55.5% 0.163 48.998)",
            "800": "oklch(47.3% 0.137 46.201)",
            "900": "oklch(41.4% 0.112 45.904)",
            "950": "oklch(27.9% 0.077 45.635)",
        },
        "font": {
            "subtle-light": "var(--color-base-500)",  # text-base-500
            "subtle-dark": "var(--color-base-400)",  # text-base-400
            "default-light": "var(--color-base-600)",  # text-base-600
            "default-dark": "var(--color-base-300)",  # text-base-300
            "important-light": "var(--color-base-900)",  # text-base-900
            "important-dark": "var(--color-base-100)",  # text-base-100
        }
    }
}


