from collections.abc import Iterator
from contextlib import contextmanager

import psycopg
from psycopg import Connection

from automation.config import settings


@contextmanager
def db_connection() -> Iterator[Connection]:
    if not settings.db_url:
        raise RuntimeError("Set DB_URL to use database helpers")
    with psycopg.connect(
        settings.db_url,
        user=settings.db_username,
        password=settings.db_password,
    ) as connection:
        yield connection
