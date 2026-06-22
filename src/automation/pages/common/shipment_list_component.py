from __future__ import annotations

import time

from automation.config import settings
from automation.logging import log_method
from automation.pages.common.base_component import BaseComponent

_PORTLET_BODY = "//div[contains(@class,'m-portlet__body')]"


class ShipmentListComponent(BaseComponent):
    """Services documentation — card list (shipment-item-wrapper)."""

    loading_overlay_selectors = [
        ".m-blockui",
        ".block-ui-wrapper.block-ui-active",
        "xpath=//div[contains(@class,'block-ui') and contains(@class,'active')]",
        "xpath=//div[contains(@class,'loading-mask')]",
        ".ng-progress-bar[active='true']",
    ]

    empty_state_selectors = [
        f"xpath={_PORTLET_BODY}//*[contains(normalize-space(),'No data to display')]",
        f"xpath={_PORTLET_BODY}//*[contains(normalize-space(),'No records')]",
        f"xpath={_PORTLET_BODY}//*[contains(normalize-space(),'No data available')]",
    ]

    @log_method("Wait for shipment list items")
    def wait_for_items(
        self,
        item_selectors: list[str],
        item_name: str,
        min_items: int = 1,
        timeout: int | None = None,
    ) -> None:
        timeout = timeout or settings.browser_timeout
        deadline = time.monotonic() + timeout / 1000

        while time.monotonic() < deadline:
            overlay = self._owner.find_visible(self.loading_overlay_selectors)
            if overlay is not None:
                self.page.wait_for_timeout(settings.polling_interval)
                continue

            loaded = self._count_loaded_items(item_selectors)
            if loaded >= min_items:
                return

            if loaded == 0 and self._owner.find_visible(self.empty_state_selectors) is not None:
                raise AssertionError(
                    f"{item_name} is empty — 'No data' message displayed, "
                    f"expected at least {min_items} shipment item(s)."
                )

            self.page.wait_for_timeout(settings.polling_interval)

        raise AssertionError(
            f"{item_name} data not loaded — expected at least {min_items} "
            f"visible shipment item(s) with content after {timeout}ms. "
            f"Found: {self._count_loaded_items(item_selectors)}."
        )

    def _count_loaded_items(self, item_selectors: list[str]) -> int:
        for selector in item_selectors:
            items = self.page.locator(selector)
            count = items.count()
            if count == 0:
                continue

            loaded = 0
            for index in range(min(count, 50)):
                item = items.nth(index)
                try:
                    if not item.is_visible():
                        continue
                    if len(item.inner_text().strip()) >= 2:
                        loaded += 1
                except Exception:
                    continue

            if loaded > 0:
                return loaded

        return 0
