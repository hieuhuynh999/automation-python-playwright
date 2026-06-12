from typing import Any, cast

from automation.db.connection import db_connection
from automation.logging import log_method


class QueryExecutor:
    @log_method("DB fetch all")
    def fetch_all(self, sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        with db_connection() as connection, connection.cursor() as cursor:
            cursor_any = cast(Any, cursor)
            cursor_any.execute(sql, params)
            columns = [column.name for column in cursor.description or []]
            return [dict(zip(columns, row, strict=False)) for row in cursor.fetchall()]

    @log_method("DB fetch one")
    def fetch_one(self, sql: str, params: tuple[Any, ...] = ()) -> dict[str, Any] | None:
        rows = self.fetch_all(sql, params)
        return rows[0] if rows else None

    @log_method("DB execute")
    def execute(self, sql: str, params: tuple[Any, ...] = ()) -> int:
        with db_connection() as connection, connection.cursor() as cursor:
            cursor_any = cast(Any, cursor)
            cursor_any.execute(sql, params)
            connection.commit()
            return cursor.rowcount
