from __future__ import annotations

from dataclasses import dataclass

from automation.config import settings
from automation.pages.common.list_grid_component import ListGridComponent
from automation.pages.etms.etms_catalogue_menu_page import EtmsCatalogueMenuPage


@dataclass(frozen=True)
class EtmsCatalogueTabConfig:
    tab_key: str
    tab_label: str
    list_column_headers: tuple[str, ...]


class EtmsCatalogueTabbedListPage(EtmsCatalogueMenuPage):
    """Base for catalogue screens with in-page tabs (Administrative Units, Zone Code, …)."""

    page_key: str
    page_hash: str
    title: str
    menu_li_id: str
    default_tab_key: str
    tab_configs: dict[str, EtmsCatalogueTabConfig]
    list_title_selectors: list[str]

    def __init__(self, page) -> None:
        super().__init__(page)
        self._list_grid = ListGridComponent(self, f"{self.title} list grid")

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
            f"a[href*='{self.page_hash}']",
        ]

    def _tab_config(self, tab_key: str) -> EtmsCatalogueTabConfig:
        if tab_key not in self.tab_configs:
            known = ", ".join(sorted(self.tab_configs))
            raise ValueError(f"Unknown {self.title} tab '{tab_key}'. Known: {known}")
        return self.tab_configs[tab_key]

    def _tab_selectors(self, tab_label: str) -> list[str]:
        raise NotImplementedError(f"{type(self).__name__} must implement _tab_selectors()")

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

    def _navigate_to_page(self) -> None:
        self._click_sidebar_link(
            self._menu_selectors(),
            f"{self.title} menu",
        )
        self.page.wait_for_url(
            lambda url: self.page_hash in url.lower().replace("_", "-"),
            timeout=settings.page_load_timeout,
        )
        self.wait_for_page_stable()
        self.wait_for_visible(
            self.list_title_selectors,
            f"{self.title} page title",
        )

    def _activate_tab(self, tab_key: str) -> EtmsCatalogueTabConfig:
        config = self._tab_config(tab_key)
        tab_link = self.wait_for_visible(
            self._tab_selectors(config.tab_label),
            f"{self.title} tab {config.tab_label}",
        )
        tab_link.scroll_into_view_if_needed()
        self.wait_for_page_stable()
        tab_link.click(force=True)
        self.wait_for_page_stable()
        return config

    def _wait_tab_grid(self, tab_key: str, min_rows: int) -> None:
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
        self.list_grid.wait_for_data_rows(
            min_rows=min_rows,
            table_selectors=table_selectors,
        )

    def count_data_rows_for_tab(self, tab_key: str) -> int:
        return self.list_grid.count_data_rows(
            table_selectors=self.list_table_selectors_for_tab(tab_key),
        )
