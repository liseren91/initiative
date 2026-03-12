from app.core.config import _ensure_asyncpg_url


def test_ensure_asyncpg_url_converts_sslmode_require_to_ssl_require() -> None:
    source = (
        "postgresql://user:pass@db.example.com:5432/app"
        "?sslmode=require&channel_binding=require"
    )

    result = _ensure_asyncpg_url(source)

    assert result.startswith("postgresql+asyncpg://")
    assert "ssl=require" in result
    assert "sslmode=" not in result
    assert "channel_binding=" not in result


def test_ensure_asyncpg_url_preserves_existing_ssl_param() -> None:
    source = "postgresql://user:pass@db.example.com:5432/app?ssl=verify-full&sslmode=require"

    result = _ensure_asyncpg_url(source)

    assert "ssl=verify-full" in result
    assert "ssl=require" not in result
