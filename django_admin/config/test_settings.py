from .settings import *  # noqa: F403

# Fast local checks; PostgreSQL checks use the default settings in Compose.
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
