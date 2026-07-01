from __future__ import annotations

from dataclasses import dataclass

from automation.pages.common.list_grid_component import ListGridComponent
from automation.pages.etms.etms_catalogue_menu_page import (
    EtmsCatalogueMenuPage,
    _catalogue_submenu_link_by_label,
    _sidebar_link_by_href,
    etms_in_page_tab_selectors,
    etms_page_title_selectors,
)

@dataclass(frozen=True)
class EtmsCatalogueTabConfig:
    tab_key: str
    tab_label: str
    list_column_headers: tuple[str, ...]
    page_hash: str | None = None
    sidebar_menu_label: str | None = None


class EtmsCatalogueTabbedListPage(EtmsCatalogueMenuPage):
    """Base for catalogue screens with in-page tabs (Administrative Units, Zone Code, …)."""

    page_key: str
    page_hash: str
    title: str
    menu_li_id: str
    default_tab_key: str
    tab_configs: dict[str, EtmsCatalogueTabConfig]
    list_title_selectors: list[str] | None = None

    def __init__(self, page) -> None:
        super().__init__(page)
        self._list_grid = ListGridComponent(self, f"{self.title} list grid")

    @property
    def page_title_selectors(self) -> list[str]:
        if self.list_title_selectors is not None:
            return self.list_title_selectors
        return etms_page_title_selectors(self.title)

    @property
    def list_grid(self) -> ListGridComponent:
        return self._list_grid

    @property
    def list_table_selectors(self) -> list[str]:
        return self.list_table_selectors_for_tab(self.default_tab_key)

    def _menu_selectors(self) -> list[str]:
        return [
            f"#{self.menu_li_id} > a.nav-link",
            (
                f"xpath=//li[@id='{self.menu_li_id}']"
                f"//span[normalize-space()='{self.title}']"
                "/ancestor::a[contains(@class,'nav-link')][1]"
            ),
            _catalogue_submenu_link_by_label(self.title),
            (
                "xpath=//a[contains(@class,'nav-link')]"
                f"[.//span[normalize-space()='{self.title}']]"
            ),
            _sidebar_link_by_href(self.page_hash),
        ]

    def _tab_config(self, tab_key: str) -> EtmsCatalogueTabConfig:
        if tab_key not in self.tab_configs:
            known = ", ".join(sorted(self.tab_configs))
            raise ValueError(f"Unknown {self.title} tab '{tab_key}'. Known: {known}")
        return self.tab_configs[tab_key]

    def page_hash_for_tab(self, tab_key: str) -> str:
        config = self._tab_config(tab_key)
        return config.page_hash or self.page_hash

    def page_title_for_tab(self, tab_key: str) -> str:
        config = self._tab_config(tab_key)
        return config.sidebar_menu_label or config.tab_label or self.title

    def _tab_uses_sidebar_nav(self, tab_key: str) -> bool:
        config = self._tab_config(tab_key)
        return bool(config.sidebar_menu_label and config.page_hash)

    def _tab_selectors(self, tab_label: str) -> list[str]:
        return etms_in_page_tab_selectors(tab_label)

    def list_table_selectors_for_tab(self, tab_key: str) -> list[str]:
        config = self._tab_config(tab_key)
        first_header = config.list_column_headers[0]
        return [
            f"xpath=//table[.//th[normalize-space()='{first_header}']]//th",
            (
                f"xpath=//*[self::h3 or contains(@class,'page-title')]"
                f"[normalize-space()='{self.title}' or contains(normalize-space(),'{self.title}')]"
                "/ancestor::div[contains(@class,'m-portlet') or contains(@class,'portlet')][1]"
                "//table//th"
            ),
            f"xpath=//th[normalize-space()='{first_header}']",
        ]

    def _navigate_to_page_hash(
        self,
        page_hash: str,
        menu_selectors: list[str],
        menu_name: str,
        title: str,
    ) -> None:
        self._click_sidebar_link(menu_selectors, menu_name)
        self._wait_for_url_hash(page_hash)
        self.wait_for_page_stable()
        self.wait_for_visible(
            etms_page_title_selectors(title),
            f"{title} page title",
        )

    def _navigate_to_page(self, tab_key: str | None = None) -> None:
        active = tab_key or self.default_tab_key
        if self._tab_uses_sidebar_nav(active):
            config = self._tab_config(active)
            self._navigate_to_page_hash(
                config.page_hash,
                [
                    _catalogue_submenu_link_by_label(config.sidebar_menu_label),
                    (
                        "xpath=//a[contains(@class,'nav-link')]"
                        f"[.//span[normalize-space()='{config.sidebar_menu_label}']]"
                    ),
                    _sidebar_link_by_href(config.page_hash),
                ],
                f"{config.sidebar_menu_label} menu",
                config.tab_label,
            )
            return

        self._navigate_to_page_hash(
            self.page_hash,
            self._menu_selectors(),
            f"{self.title} menu",
            self.title,
        )

    def _activate_tab(self, tab_key: str) -> EtmsCatalogueTabConfig:
        config = self._tab_config(tab_key)
        tab_link = self.wait_for_visible(
            self._tab_selectors(config.tab_label),
            f"{self.title} tab {config.tab_label}",
        )
        tab_link.evaluate(
            "(el) => el.scrollIntoView({ block: 'center', inline: 'nearest' })"
        )
        tab_link.scroll_into_view_if_needed()
        self.wait_for_page_stable()
        tab_link.click(force=True)
        self.wait_for_page_stable()
        return config

    def _wait_tab_grid(
        self,
        tab_key: str,
        min_rows: int,
        *,
        allow_no_data: bool = False,
    ) -> None:
        config = self._tab_config(tab_key)
        table_selectors = self.list_table_selectors_for_tab(tab_key)
        self.list_grid.wait_until_ready(
            table_selectors,
            f"{self.title} {config.tab_label} table",
        )
        self.list_grid.verify_column_headers(
            list(config.list_column_headers),
            table_selectors=table_selectors,
        )
        if allow_no_data:
            self.list_grid.wait_for_data_rows_or_no_data(
                min_rows=min_rows,
                table_selectors=table_selectors,
            )
        else:
            self.list_grid.wait_for_data_rows(
                min_rows=min_rows,
                table_selectors=table_selectors,
            )

    def count_data_rows_for_tab(self, tab_key: str) -> int:
        return self.list_grid.count_data_rows(
            table_selectors=self.list_table_selectors_for_tab(tab_key),
        )

    def confirm_grid_loaded(
        self,
        min_rows: int = 1,
        *,
        tab_key: str | None = None,
        allow_no_data: bool = False,
    ) -> EtmsCatalogueTabbedListPage:
        """Re-verify tab grid is ready — call before navigating to the next catalogue page."""
        active_tab = tab_key or self.default_tab_key
        self.wait_before_next_catalogue_navigation()
        self._wait_tab_grid(active_tab, min_rows, allow_no_data=allow_no_data)
        return self

    def _is_tab_active(self, tab_key: str) -> bool:
        config = self._tab_config(tab_key)
        tab_label = config.tab_label
        active_selector = (
            "xpath=//div[contains(@class,'nav-tabs')]"
            f"//a[contains(@class,'active') and normalize-space()='{tab_label}']"
        )
        return self.page.locator(active_selector).count() > 0

    def _active_tab_key(self) -> str | None:
        for key in self.tab_configs:
            if self._is_tab_active(key):
                return key
        return None

    def _is_on_list_page(self) -> bool:
        hash_fragment = self.page_hash.lower().replace("_", "-")
        return hash_fragment in self.current_url.lower().replace("_", "-")

    def prepare_for_performance(
        self,
        *,
        tab_key: str | None = None,
        min_rows: int = 1,
        allow_no_data: bool = False,
        first_page_step: bool = False,
    ) -> str:
        """Settle before perf timer. Returns 'page_load', 'click', or 'skipped'.

        Default tab on the first step of each page: timer measures sidebar page
        click → data. Other tabs: timer measures tab click → data only.
        """
        active_tab = tab_key or self.default_tab_key

        if first_page_step and active_tab == self.default_tab_key:
            return "page_load"

        if not self._is_on_list_page():
            self._navigate_to_page(active_tab)

        self.wait_before_next_catalogue_navigation()

        current_tab = self._active_tab_key()
        if current_tab is not None:
            self.list_grid.wait_until_ready(
                self.list_table_selectors_for_tab(current_tab),
                f"{self.title} table",
            )
        return "click"

    def _perform_tab_click(self, tab_key: str) -> None:
        """Click in-page tab only — no pre-click grid settle (used by performance timer)."""
        config = self._tab_config(tab_key)
        tab_link = self.wait_for_visible(
            self._tab_selectors(config.tab_label),
            f"{self.title} tab {config.tab_label}",
        )
        tab_link.evaluate(
            "(el) => el.scrollIntoView({ block: 'center', inline: 'nearest' })"
        )
        tab_link.scroll_into_view_if_needed()
        tab_link.click(force=True)

    def run_performance_measurement(
        self,
        *,
        tab_key: str | None = None,
        min_rows: int = 1,
        allow_no_data: bool = False,
        mode: str = "click",
    ) -> None:
        """Timed segment: sidebar page click or tab click → grid data displayed."""
        if mode == "skipped":
            return
        active_tab = tab_key or self.default_tab_key
        if mode == "page_load":
            self._navigate_to_page(active_tab)
        elif mode == "click":
            self._perform_tab_click(active_tab)
        self._wait_tab_grid(active_tab, min_rows, allow_no_data=allow_no_data)

    def load_page_for_performance(
        self,
        min_rows: int = 1,
        *,
        tab_key: str | None = None,
        allow_no_data: bool = False,
        first_page_step: bool = False,
    ) -> EtmsCatalogueTabbedListPage:
        mode = self.prepare_for_performance(
            tab_key=tab_key,
            min_rows=min_rows,
            allow_no_data=allow_no_data,
            first_page_step=first_page_step,
        )
        self.run_performance_measurement(
            tab_key=tab_key,
            min_rows=min_rows,
            mode=mode,
        )
        return self
