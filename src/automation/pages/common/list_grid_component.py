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
    ) -> None:
        timeout = timeout or settings.browser_timeout
        for column in expected_columns:
            column_selectors = [
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
            self._owner.wait_for_visible(
                column_selectors,
                f"Table column: {column}",
                timeout=timeout,
            )

    @log_method("Wait for list grid data rows")
    def wait_for_data_rows(
        self,
        min_rows: int = 1,
        timeout: int | None = None,
    ) -> None:
        timeout = timeout or settings.browser_timeout
        deadline = time.monotonic() + timeout / 1000

        while time.monotonic() < deadline:
            row_count = self._count_loaded_data_rows()
            cell_count = self._count_loaded_data_cells()
            if row_count >= min_rows or cell_count >= min_rows:
                return

            if (
                row_count == 0
                and cell_count == 0
                and self._owner.find_visible(self.empty_state_selectors) is not None
            ):
                raise AssertionError(
                    "List grid is empty — 'No data' message displayed in portlet, "
                    f"expected at least {min_rows} row(s) with cell content."
                )

            self.page.wait_for_timeout(settings.polling_interval)

        raise AssertionError(
            "List grid data not loaded — expected at least "
            f"{min_rows} visible row(s) with cell content after {timeout}ms. "
            f"Rows with text: {self._count_loaded_data_rows()}, "
            f"cells with text: {self._count_loaded_data_cells()}."
        )

    def _count_loaded_data_cells(self) -> int:
        loaded = 0
        for selector in self.grid_cell_selectors:
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

    def _count_loaded_data_rows(self) -> int:
        for selector in self.grid_row_selectors:
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
