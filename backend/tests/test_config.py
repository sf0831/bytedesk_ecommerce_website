import pytest
from pydantic import ValidationError

from app.config import Settings


def configuration(**values):
    return Settings(
        _env_file=None,
        app_env="production",
        postgres_db="store",
        postgres_user="store",
        postgres_host="postgres",
        postgres_password="test-only-password@:/%",
        **{"jwt_secret_key": "test-secret-for-configuration-32-characters", **values},
    )


def test_database_url_handles_special_characters():
    settings = configuration()
    assert settings.database_url.password == "test-only-password@:/%"
    assert "test-only-password" not in str(settings.database_url)


def test_wildcard_cors_is_rejected():
    with pytest.raises(ValidationError):
        configuration(cors_origins="*")


def test_placeholder_password_is_rejected():
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            app_env="production",
            postgres_db="store",
            postgres_user="store",
            postgres_password="replace-with-local-password",
        )


@pytest.mark.parametrize(
    "secret", ["", "short", "replace-with-a-random-secret-of-32-characters"]
)
def test_invalid_jwt_secret_rejected(secret):
    with pytest.raises(ValidationError):
        configuration(jwt_secret_key=secret)


def test_unsafe_algorithm_rejected():
    with pytest.raises(ValidationError):
        configuration(jwt_algorithm="none")


def test_missing_jwt_secret_rejected(monkeypatch):
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            postgres_db="store",
            postgres_user="store",
            postgres_password="safe-database-password",
        )
