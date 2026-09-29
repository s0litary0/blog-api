from decouple import config


SECRET_KEY = config("BLOG_SECRET_KEY", cast=str)