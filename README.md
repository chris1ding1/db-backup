# DB Backup

A database backup tool that dumps MySQL/PostgreSQL databases and uploads to S3/R2.

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- `mysqldump` and/or `pg_dump` installed locally

## Setup

```bash
uv sync

cp .env.example .env
# Edit .env with your database and storage credentials
```

## Configuration

Edit `BACKUP_TASKS` in `config.py` to define your backup tasks:

```python
DATABASE_CONNECTIONS: dict[str, dict] = {
    "mysql-1": {
        "driver": DatabaseDriver.MYSQL,
        "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER"),
        "password": os.getenv("MYSQL_PASSWORD"),
    },
    "pgsql-1": {
        "driver": DatabaseDriver.PGSQL,
        "host": os.getenv("PGSQL_HOST", "127.0.0.1"),
        "port": int(os.getenv("PGSQL_PORT", "5432")),
        "user": os.getenv("PGSQL_USER"),
        "password": os.getenv("PGSQL_PASSWORD"),
    },
}

DATABASE_CONNECTIONS: dict[str, dict] = {
    {
        "db_connection": "mysql-1",       # Connection name defined in DATABASE_CONNECTIONS
        "dump_command": "mysqldump my_database",
        "result_filename": "production.my_database",
        "save_path": "my_database",     # Subdirectory under backup/
    },
    # ...
]
```

## Usage

```bash
uv run python main.py
```

## Storage

Backup files are saved locally to `backup/` and optionally uploaded to remote storage (S3, Cloudflare R2) based on `STORAGE_REMOTE_DEFAULT` in `.env`.

## GitHub Actions

The included workflow runs backups on a monthly schedule. Configure your credentials via repository secrets and variables.
