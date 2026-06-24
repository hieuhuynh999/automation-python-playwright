from __future__ import annotations

import time

from automation.config import settings
from automation.logging import log_method
from automation.pages.common.base_component import BaseComponent

_PORTLET_BODY = "//div[contains(@class,'m-portlet__body')]"


class ListGridComponent(BaseComponent):
    """ngx-datatable / HTML table — wait for load and verify headers + rows."""

    loading_overlay_selectors = [
        ".m-blockui",
        ".block-ui-wrapper.block-ui-active",
        "xpath=//div[contains(@class,'block-ui') and contains(@class,'active')]",
        "xpath=//div[contains(@class,'loading-mask')]",
        ".ng-progress-bar[active='true']",
    ]

    grid_row_selectors = [
        "xpath=//div[contains(@class,'m-portlet__body')]//datatable-body//datatable-row-wrapper",
        "xpath=//div[contains(@class,'m-portlet__body')]//ngx-datatable//datatable-row-wrapper",
        "xpath=//div[contains(@class,'m-portlet__body')]//table//tbody//tr[td]",
        "xpath=//datatable-body//datatable-row-wrapper",
        "xpath=//table//tbody//tr[td]",
    ]

    grid_cell_selectors = [
        "xpath=//div[contains(@class,'m-portlet__body')]//div[contains(@class,'datatable-body-cell')]",
        "xpath=//div[contains(@class,'m-portlet__body')]//datatable-body-cell",
        "xpath=//div[contains(@class,'m-portlet__body')]//table//tbody//td",
    ]

    empty_state_selectors = [
        f"xpath={_PORTLET_BODY}//*[contains(normalize-space(),'No data to display')]",
        f"xpath={_PORTLET_BODY}//*[contains(normalize-space(),'No records')]",
        f"xpath={_PORTLET_BODY}//*[contains(normalize-space(),'No data available')]",
    ]

    @staticmethod
    def _prefix_from_selector(sel: str) -> str | None:
        if sel.startswith("xpath=//table[.//th"):
            return sel.removesuffix("//th") if sel.endswith("//th") else sel
        if sel.startswith("xpath=//th[normalize-space()="):
            column = sel.split("normalize-space()='", 1)[1].split("']", 1)[0]
            return f"xpath=//table[.//th[normalize-space()='{column}']]"
        if sel.startswith("xpath=") and "//table//th" in sel and "ancestor::div" in sel:
            # Prefer the table element — portlet wrapper may not contain tbody rows.
            return sel.rsplit("//table//th", 1)[0] + "//table"
        return None

    def _active_table_scope_prefix(self, table_selectors: list[str] | None) -> str | None:
        if not table_selectors:
            return None
        # Prefer explicit table[.//th] scope — most reliable for eTMS HTML tables.
        for sel in table_selectors:
            if sel.startswith("xpath=//table[.//th") and self._owner.find_visible([sel]) is not None:
                return self._prefix_from_selector(sel)
        for sel in table_selectors:
            if self._owner.find_visible([sel]) is None:
                continue
            return self._prefix_from_selector(sel)
        return None

    def _scoped_row_selectors(self, table_selectors: list[str] | None) -> list[str]:
        prefix = self._active_table_scope_prefix(table_selectors)
        if prefix:
            return [
                f"{prefix}//tbody//tr[td]",
                f"{prefix}//datatable-body//datatable-row-wrapper",
                f"{prefix}//ngx-datatable//datatable-row-wrapper",
            ]
        return self.grid_row_selectors

    def _scoped_cell_selectors(self, table_selectors: list[str] | None) -> list[str]:
        prefix = self._active_table_scope_prefix(table_selectors)
        if prefix:
            return [
                f"{prefix}//tbody//td",
                f"{prefix}//div[contains(@class,'datatable-body-cell')]",
                f"{prefix}//datatable-body-cell",
            ]
        return self.grid_cell_selectors

    def _scoped_empty_state_selectors(self, table_selectors: list[str] | None) -> list[str]:
        prefix = self._active_table_scope_prefix(table_selectors)
        if prefix:
            return [
                f"{prefix}//*[contains(normalize-space(),'No data to display')]",
                f"{prefix}//*[contains(normalize-space(),'No records')]",
                f"{prefix}//*[contains(normalize-space(),'No data available')]",
            ]
        return self.empty_state_selectors

    def _scoped_column_selectors(
        self,
        column: str,
        table_selectors: list[str] | None,
    ) -> list[str]:
        prefix = self._active_table_scope_prefix(table_selectors)
        if prefix:
            return [
                f"{prefix}//th[normalize-space()='{column}']",
                (
                    f"{prefix}//*[contains(@class,'datatable-header-cell-label')]"
                    f"[normalize-space()='{column}']"
                ),
            ]
        return [
            (
                "xpath=//div[contains(@class,'m-portlet__body')]"
                f"//th[normalize-space()='{column}']"
            ),
            (
                "xpath=//div[contains(@class,'m-portlet__body')]"
                f"//*[contains(@class,'datatable-header-cell-label')]"
                f"[normalize-space()='{column}']"
            ),
            f"xpath=//th[normalize-space()='{column}']",
            f"th:has-text('{column}')",
        ]

    @log_method("Wait for list grid ready")
    def wait_until_ready(
        self,
        table_selectors: list[str],
        table_name: str,
        timeout: int | None = None,
    ) -> None:
        timeout = timeout or settings.browser_timeout
        deadline = time.monotonic() + timeout / 1000
        while time.monotonic() < deadline:
            overlay = self._owner.find_visible(self.loading_overlay_selectors)
            table = self._owner.find_visible(table_selectors)
            if overlay is None and table is not None:
                return
            self.page.wait_for_timeout(settings.polling_interval)
        self._owner.wait_for_visible(table_selectors, table_name, timeout=timeout)

    @log_method("Verify list grid column headers")
    def verify_column_headers(
        self,
        expected_columns: list[str],
        timeout: int | None = None,
        table_selectors: list[str] | None = None,
    ) -> None:
        timeout = timeout or settings.browser_timeout
        for column in expected_columns:
            column_selectors = self._scoped_column_selectors(column, table_selectors)
            self._owner.wait_for_visible(
                column_selectors,
                f"Table column: {column}",
                timeout=timeout,
            )

    def count_data_rows(self, table_selectors: list[str] | None = None) -> int:
        """Count visible data rows/cells scoped to the target list table."""
        row_selectors = self._scoped_row_selectors(table_selectors)
        cell_selectors = self._scoped_cell_selectors(table_selectors)
        row_count = self._count_loaded_data_rows(row_selectors)
        if row_count > 0:
            return row_count
        return self._count_loaded_data_cells(cell_selectors)

    @log_method("Wait for list grid data rows")
    def wait_for_data_rows(
        self,
        min_rows: int = 1,
        timeout: int | None = None,
        table_selectors: list[str] | None = None,
    ) -> int:
        timeout = timeout or settings.browser_timeout
        deadline = time.monotonic() + timeout / 1000
        row_selectors = self._scoped_row_selectors(table_selectors)
        cell_selectors = self._scoped_cell_selectors(table_selectors)
        empty_state_selectors = self._scoped_empty_state_selectors(table_selectors)

        while time.monotonic() < deadline:
            row_count = self._count_loaded_data_rows(row_selectors)
            cell_count = self._count_loaded_data_cells(cell_selectors)
            loaded = max(row_count, cell_count)
            if loaded >= min_rows:
                return loaded

            if (
                row_count == 0
                and cell_count == 0
                and self._owner.find_visible(empty_state_selectors) is not None
            ):
                raise AssertionError(
                    "List grid is empty — 'No data' message displayed in portlet, "
                    f"expected at least {min_rows} row(s) with cell content."
                )

            self.page.wait_for_timeout(settings.polling_interval)

        row_count = self._count_loaded_data_rows(row_selectors)
        cell_count = self._count_loaded_data_cells(cell_selectors)
        raise AssertionError(
            "List grid data not loaded — expected at least "
            f"{min_rows} visible row(s) with cell content after {timeout}ms. "
            f"Rows with text: {row_count}, cells with text: {cell_count}."
        )

    def _count_loaded_data_cells(self, cell_selectors: list[str] | None = None) -> int:
        selectors = cell_selectors or self.grid_cell_selectors
        loaded = 0
        for selector in selectors:
            cells = self.page.locator(selector)
            count = cells.count()
            if count == 0:
                continue

            for index in range(min(count, 50)):
                cell = cells.nth(index)
                try:
                    if not cell.is_visible():
                        continue
                    text = cell.inner_text().strip()
                    if len(text) >= 2:
                        loaded += 1
                except Exception:
                    continue

            if loaded > 0:
                return loaded

        return 0

    def _count_loaded_data_rows(self, row_selectors: list[str] | None = None) -> int:
        selectors = row_selectors or self.grid_row_selectors
        for selector in selectors:
            rows = self.page.locator(selector)
            count = rows.count()
            if count == 0:
                continue

            loaded = 0
            for index in range(count):
                row = rows.nth(index)
                try:
                    if not row.is_visible():
                        continue
                    text = row.inner_text().strip()
                    # Skip skeleton/placeholder rows (checkbox-only or whitespace).
                    if len(text) >= 2:
                        loaded += 1
                except Exception:
                    continue
            if loaded > 0:
                return loaded

        return 0
