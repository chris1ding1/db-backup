import os
from enum import StrEnum
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


class StorageDriver(StrEnum):
    R2 = "r2"
    S3 = "s3"


class DatabaseDriver(StrEnum):
    MYSQL = "mysql"
    PGSQL = "pgsql"


load_dotenv()


DATABASE_CONNECTIONS: dict[str, dict] = {
    "mysql": {
        "driver": DatabaseDriver.MYSQL,
        "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER"),
        "password": os.getenv("MYSQL_PASSWORD"),
    },
    "pgsql": {
        "driver": DatabaseDriver.PGSQL,
        "host": os.getenv("PGSQL_HOST", "127.0.0.1"),
        "port": int(os.getenv("PGSQL_PORT", "5432")),
        "user": os.getenv("PGSQL_USER"),
        "password": os.getenv("PGSQL_PASSWORD"),
    },
}

STORAGE: dict[str, Any] = {
    "local": str(Path(__file__).resolve().parent / "backup"),
    "remote": {
        "default": list(
            dict.fromkeys(
                s for s in os.getenv("STORAGE_REMOTE_DEFAULT", "").split(",") if s
            )
        ),
        "disks": {
            "r2": {
                "driver": StorageDriver.R2,
                "endpoint": "https://"
                + os.getenv("CLOUDFLARE_ACCOUNT_ID")
                + ".r2.cloudflarestorage.com",
                "bucket": os.getenv("CLOUDFLARE_BUCKET"),
                "key": os.getenv("CLOUDFLARE_ACCESS_KEY_ID"),
                "secret": os.getenv("CLOUDFLARE_SECRET_ACCESS_KEY"),
            },
            "s3": {
                "driver": StorageDriver.S3,
                "bucket": os.getenv("AWS_BUCKET"),
                "region": os.getenv("AWS_DEFAULT_REGION"),
                "key": os.getenv("AWS_ACCESS_KEY_ID"),
                "secret": os.getenv("AWS_SECRET_ACCESS_KEY"),
            },
        },
    },
}

BACKUP_TASKS: list[str, dict] = []
