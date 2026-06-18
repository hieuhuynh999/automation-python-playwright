import time

from playwright.sync_api import Locator, Page

from automation.config import settings
from automation.logging import log_method, logger


class BasePage:
    def __init__(self, page: Page):
        self.page = page

    @property
    def current_url(self) -> str:
        return self.page.url

    @log_method("Open URL")
    def open_url(self, url: str) -> None:
        self.page.goto(url, wait_until="domcontentloaded")
        self.wait_for_dom_content_loaded()

    @log_method("Wait for DOM content loaded")
    def wait_for_dom_content_loaded(self) -> None:
        self.page.wait_for_load_state("domcontentloaded")

    @log_method("Wait for page stable")
    def wait_for_page_stable(self) -> "BasePage":
        self.wait_for_dom_content_loaded()
        self.page.wait_for_function(
            "() => document.readyState === 'complete'",
            timeout=settings.page_load_timeout,
        )
        if settings.navigation_settle_ms > 0:
            self.page.wait_for_timeout(settings.navigation_settle_ms)
        return self

    @log_method("Wait for element visible")
    def wait_for_visible(
        self,
        selectors: list[str],
        element_name: str,
        timeout: int | None = None,
    ) -> Locator:

        timeout = timeout or settings.browser_timeout

        deadline = time.monotonic() + timeout / 1000

        while time.monotonic() < deadline:
            locator = self.find_visible(selectors)

            if locator:
                logger.info(f"Element visible: {element_name}")

                return locator

            self.page.wait_for_timeout(settings.polling_interval)

        raise AssertionError(self._build_wait_error(element_name, selectors, timeout))

    def _build_wait_error(
        self,
        element_name: str,
        selectors: list[str],
        timeout: int,
    ) -> str:
        selector_list = "\n".join(f"  - {selector}" for selector in selectors)
        return (
            f"Element '{element_name}' not visible after {timeout}ms.\n"
            f"Tried selectors:\n{selector_list}"
        )

    def find_visible(
        self,
        selectors: list[str],
    ) -> Locator | None:

        for selector in selectors:
            locator = self.page.locator(selector).first

            try:
                if locator.is_visible():
                    logger.info(f"Found element by selector: {selector}")

                    return locator

            except Exception:
                logger.debug(f"Selector not found: {selector}")

        return None
