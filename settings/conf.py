from decouple import config
from datetime import timedelta


SECRET_KEY = config("BLOG_SECRET_KEY", cast=str)
ENV_ID = config("BLOG_ENV_ID", cast=str)


# -----------------------------------------------------
# Django REST Framework settings
# -----------------------------------------------------

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        # TODO: change to IsAuthenticated
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}

# -----------------------------------------------------
# Simple JWT settings
# -----------------------------------------------------
ACCESS_TOKEN_LIFETIME: timedelta = timedelta(minutes=15)
REFRESH_TOKEN_LIFETIME: timedelta = timedelta(days=1)

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": ACCESS_TOKEN_LIFETIME,
    "REFRESH_TOKEN_LIFETIME": REFRESH_TOKEN_LIFETIME,
    "SIGNING_KEY": SECRET_KEY,
    # "AUTH_HEADER_TYPES": ("JWT",), 
}