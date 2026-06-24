from __future__ import annotations

from dataclasses import dataclass

from automation.config import settings
from automation.logging import log_method
from automation.pages.common.list_grid_component import ListGridComponent
from automation.pages.etms.etms_catalogue_menu_page import EtmsCatalogueMenuPage


@dataclass(frozen=True)
class TransportNetworkListPageConfig:
    page_key: str
    title: str
    page_hash: str
    menu_li_id: str
    list_column_headers: tuple[str, ...]


TRANSPORT_NETWORK_LIST_PAGE_CONFIGS: dict[str, TransportNetworkListPageConfig] = {
    "route_information": TransportNetworkListPageConfig(
        page_key="route_information",
        title="Route Information",
        page_hash="catalogue/route-infomation",
        menu_li_id="catRoute",
        list_column_headers=("Code", "Place From"),
    ),
    "transit_route": TransportNetworkListPageConfig(
        page_key="transit_route",
        title="Transit Route",
        page_hash="catalogue/transit-route",
        menu_li_id="catTransitRouteMiddlePlace",
        list_column_headers=("Code", "POL"),
    ),
    "hub": TransportNetworkListPageConfig(
        page_key="hub",
        title="Hub",
        page_hash="catalogue/hub",
        menu_li_id="sysHub",
        list_column_headers=("Code", "Name (VI)"),
    ),
    "branch": TransportNetworkListPageConfig(
        page_key="branch",
        title="Branch",
        page_hash="catalogue/branch",
        menu_li_id="sysBranch",
        list_column_headers=("Code", "Name (VI)"),
    ),
    "administrative_units": TransportNetworkListPageConfig(
        page_key="administrative_units",
        title="Administrative Units",
        page_hash="catalogue/administrative-units",
        menu_li_id="catAdministrativeUnit",
        list_column_headers=("Code", "Name (VI)"),
    ),
    "zone_code": TransportNetworkListPageConfig(
        page_key="zone_code",
        title="Zone Code",
        page_hash="catalogue/zone-code",
        menu_li_id="catZoneCode",
        list_column_headers=("Code", "Type"),
    ),
    "route_project_information": TransportNetworkListPageConfig(
        page_key="route_project_information",
        title="Route Project Information",
        page_hash="catalogue/route-project",
        menu_li_id="catRouteProject",
        list_column_headers=("Customer", "Project Code"),
    ),
}


class EtmsTransportNetworkListPage(EtmsCatalogueMenuPage):
    """Generic list page — Catalogue > Transport Network > {title}."""

    def __init__(self, page, page_key: str) -> None:
        super().__init__(page)
        if page_key not in TRANSPORT_NETWORK_LIST_PAGE_CONFIGS:
            known = ", ".join(sorted(TRANSPORT_NETWORK_LIST_PAGE_CONFIGS))
            raise ValueError(f"Unknown Transport Network page_key '{page_key}'. Known: {known}")
        self._config = TRANSPORT_NETWORK_LIST_PAGE_CONFIGS[page_key]
        self.page_key = page_key
        self.page_hash = self._config.page_hash

    @property
    def list_grid(self) -> ListGridComponent:
        attr = f"_list_grid_{self.page_key}"
        if not hasattr(self, attr):
            setattr(
                self,
                attr,
                ListGridComponent(self, f"{self._config.title} list grid"),
            )
        return getattr(self, attr)

    @property
    def list_table_selectors(self) -> list[str]:
        return self._list_table_selectors()

    def _menu_selectors(self) -> list[str]:
        title = self._config.title
        menu_li_id = self._config.menu_li_id
        page_hash = self._config.page_hash
        return [
            f"#{menu_li_id} > a.nav-link",
            (
                f"xpath=//li[@id='{menu_li_id}']"
                f"//span[normalize-space()='{title}']"
                "/ancestor::a[contains(@class,'nav-link')][1]"
            ),
            f"a[href*='{page_hash}']",
        ]

    def _list_title_selectors(self) -> list[str]:
        title = self._config.title
        return [
            f"xpath=//h3[normalize-space()='{title}']",
            f"h3:has-text('{title}')",
            f".page-title:has-text('{title}')",
            f"xpath=//*[contains(@class,'page-title') and normalize-space()='{title}']",
            (
                "xpath=//*[contains(@class,'page-title') "
                f"and contains(normalize-space(),'{title}')]"
            ),
        ]

    def _list_table_selectors(self) -> list[str]:
        title = self._config.title
        first_header = self._config.list_column_headers[0]
        return [
            f"xpath=//table[.//th[normalize-space()='{first_header}']]//th",
            (
                f"xpath=//*[self::h3 or contains(@class,'page-title')]"
                f"[normalize-space()='{title}' or contains(normalize-space(),'{title}')]"
                "/ancestor::div[contains(@class,'m-portlet') or contains(@class,'portlet')][1]"
                "//table//th"
            ),
            f"xpath=//th[normalize-space()='{first_header}']",
        ]

    @log_method("Click Transport Network list menu")
    def click_menu(self) -> EtmsTransportNetworkListPage:
        self.open_transport_network_menu()
        self._click_sidebar_link(
            self._menu_selectors(),
            f"{self._config.title} menu",
        )
        self.page.wait_for_url(
            lambda url: self.page_hash in url.lower().replace("_", "-"),
            timeout=settings.page_load_timeout,
        )
        self.wait_for_page_stable()
        return self

    def load_page_for_performance(self, min_rows: int = 1) -> EtmsTransportNetworkListPage:
        """Click menu and wait for table — used by performance tests (no POM step logs)."""
        self._click_sidebar_link(
            self._menu_selectors(),
            f"{self._config.title} menu",
        )
        self.page.wait_for_url(
            lambda url: self.page_hash in url.lower().replace("_", "-"),
            timeout=settings.page_load_timeout,
        )
        self.wait_for_page_stable()
        self.wait_for_visible(
            self._list_title_selectors(),
            f"{self._config.title} page title",
        )
        self.list_grid.wait_until_ready(
            self.list_table_selectors,
            f"{self._config.title} table",
        )
        self.list_grid.verify_column_headers(
            list(self._config.list_column_headers),
            table_selectors=self.list_table_selectors,
        )
        self.list_grid.wait_for_data_rows(
            min_rows=min_rows,
            table_selectors=self.list_table_selectors,
        )
        return self
