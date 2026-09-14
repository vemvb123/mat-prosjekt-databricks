import os
from pathlib import Path


def load_env_file() -> None:
    """Load simple KEY=value pairs from .env without requiring extra packages."""
    # Databricks and local runs can have different working directories, so try both.
    possible_paths = [
        Path.cwd() / ".env",
        Path(__file__).resolve().parent.parent / ".env",
    ]

    for env_path in possible_paths:
        if not env_path.exists():
            continue

        # Keep the parser simple: comments and empty lines are ignored.
        for line in env_path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue

            # Existing environment variables should win over values from .env.
            key, value = stripped.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))
        return


load_env_file()


def get_env(name: str, default: str | None = None) -> str:
    # Required values fail fast when .env is missing something the user must set.
    value = os.environ.get(name, default)
    if value is None:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


# Values that must normally be filled in by the user or deployment environment.
USER_EMAIL = get_env("USER_EMAIL")
WAREHOUSE_ID = get_env("WAREHOUSE_ID")

AZURE_STORAGE_ACCOUNT_URL = get_env("AZURE_STORAGE_ACCOUNT_URL")
AZURE_STORAGE_CREDENTIAL_NAME = get_env("AZURE_STORAGE_CREDENTIAL_NAME")
PRODUCTS_BLOB_NAME = get_env("PRODUCTS_BLOB_NAME")

# Stable project values. These can be overridden by environment variables,
# but users do not need to set them in .env for normal use.
PLATFORM_REST_BASE_URL = get_env(
    "PLATFORM_REST_BASE_URL",
    "https://platform-rest-prod.ngdata.no",
)
AZURE_STORAGE_CONTAINER = get_env("AZURE_STORAGE_CONTAINER", "raw")
AZURE_BLOB_PREFIX = get_env("AZURE_BLOB_PREFIX", "customer_support")
SCRAPE_FILENAME_PREFIX = get_env("SCRAPE_FILENAME_PREFIX", "weekly_data")
