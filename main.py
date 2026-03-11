import os
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import boto3
from boto3.exceptions import S3UploadFailedError
from botocore.exceptions import ClientError

from config import (
    BACKUP_TASKS,
    DATABASE_CONNECTIONS,
    STORAGE,
    DatabaseDriver,
    StorageDriver,
)


def build_result_filename(base_name: str) -> str:
    utc_datetime = datetime.now(tz=UTC).strftime("%Y%m%d%H%M%S")
    return f"{base_name}-{utc_datetime}.sql"


def build_dump_command(command: str, db_conn: dict, output_file: str) -> str:
    extra_args = ""

    if db_conn["driver"] == DatabaseDriver.MYSQL:
        extra_args = f"-h {db_conn['host']} -P {db_conn['port']} -u {db_conn['user']} --result-file='{output_file}'"
    elif db_conn["driver"] == DatabaseDriver.PGSQL:
        extra_args = f"-h {db_conn['host']} -p {db_conn['port']} -U {db_conn['user']} -f '{output_file}'"

    return f"{command} {extra_args}".strip()


def build_db_password_env(db_conn: dict) -> dict[str, str]:
    env = os.environ.copy()
    driver = db_conn["driver"]

    if driver == DatabaseDriver.MYSQL:
        if db_conn.get("password"):
            env["MYSQL_PWD"] = db_conn["password"]
    elif driver == DatabaseDriver.PGSQL:
        if db_conn.get("password"):
            env["PGPASSWORD"] = db_conn["password"]

    return env


def upload_to_r2(config_info: dict, file_name: str, object_name: str) -> bool:
    client = boto3.client(
        "s3",
        endpoint_url=config_info["endpoint"],
        aws_access_key_id=config_info["key"],
        aws_secret_access_key=config_info["secret"],
        region_name="auto",
    )
    try:
        client.upload_file(file_name, config_info["bucket"], object_name)
    except ClientError:
        return False
    except S3UploadFailedError:
        return False
    return True


def upload_to_s3(config_info: dict, file_name: str, object_name: str) -> bool:
    client = boto3.client(
        "s3",
        region_name=config_info["region"],
        aws_access_key_id=config_info["key"],
        aws_secret_access_key=config_info["secret"],
    )
    try:
        client.upload_file(file_name, config_info["bucket"], object_name)
    except ClientError:
        return False
    except S3UploadFailedError:
        return False
    return True


def run_backup(task: dict) -> None:
    db_conn_name = task["db_connection"]
    base_dump_command = task["dump_command"]
    base_result_filename = task["result_filename"]

    db_conn = DATABASE_CONNECTIONS.get(db_conn_name)

    full_result_filename = build_result_filename(base_result_filename)
    save_file = str(Path(task["save_path"]) / full_result_filename)
    full_local_file = str(Path(STORAGE["local"]) / save_file)
    full_dump_command = build_dump_command(base_dump_command, db_conn, full_local_file)

    env = build_db_password_env(db_conn)
    Path(full_local_file).parent.mkdir(parents=True, exist_ok=True)

    try:
        subprocess.run(
            full_dump_command,
            shell=True,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            env=env,
        )
    except Exception:
        return

    for disk_name in STORAGE["remote"]["default"]:
        disk = STORAGE["remote"]["disks"].get(disk_name)
        if disk:
            if disk["driver"] == StorageDriver.S3:
                upload_to_s3(disk, full_local_file, save_file)
            elif disk["driver"] == StorageDriver.R2:
                upload_to_r2(disk, full_local_file, save_file)


def main() -> None:
    for task in BACKUP_TASKS:
        run_backup(task)


if __name__ == "__main__":
    main()
