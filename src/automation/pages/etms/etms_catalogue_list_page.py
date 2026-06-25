from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from automation.config import settings
from automation.logging import log_method
from automation.pages.common.list_grid_component import ListGridComponent
from automation.pages.etms.etms_catalogue_menu_page import EtmsCatalogueMenuPage

EtmsCatalogueSuite = Literal["transport_network", "partner"]


@dataclass(frozen=True)
class EtmsCatalogueListPageConfig:
    page_key: str
    title: str
    page_hash: str
    menu_li_id: str
    list_column_headers: tuple[str, ...]
    catalogue_suite: EtmsCatalogueSuite = "transport_network"


TRANSPORT_NETWORK_LIST_PAGE_CONFIGS: dict[str, EtmsCatalogueListPageConfig] = {
    "places": EtmsCatalogueListPageConfig(
        page_key="places",
        title="Places",
        page_hash="catalogue/other-place",
        menu_li_id="catOtherPlace",
        list_column_headers=("Code", "Name (VI)"),
    ),
    "distance_between_places": EtmsCatalogueListPageConfig(
        page_key="distance_between_places",
        title="Distance Between Places",
        page_hash="catalogue/distance-between-places",
        menu_li_id="catPlaceDistance",
        list_column_headers=("Place From", "Place To"),
    ),
    "route_information": EtmsCatalogueListPageConfig(
        page_key="route_information",
        title="Route Information",
        page_hash="catalogue/route-infomation",
        menu_li_id="catRoute",
        list_column_headers=("Code", "Place From"),
    ),
    "transit_route": EtmsCatalogueListPageConfig(
        page_key="transit_route",
        title="Transit Route",
        page_hash="catalogue/transit-route",
        menu_li_id="catTransitRouteMiddlePlace",
        list_column_headers=("Code", "POL"),
    ),
    "hub": EtmsCatalogueListPageConfig(
        page_key="hub",
        title="Hub",
        page_hash="catalogue/hub",
        menu_li_id="sysHub",
        list_column_headers=("Code", "Name (VI)"),
    ),
    "branch": EtmsCatalogueListPageConfig(
        page_key="branch",
        title="Branch",
        page_hash="catalogue/branch",
        menu_li_id="sysBranch",
        list_column_headers=("Code", "Name (VI)"),
    ),
    "route_project_information": EtmsCatalogueListPageConfig(
        page_key="route_project_information",
        title="Route Project Information",
        page_hash="catalogue/route-project",
        menu_li_id="catRouteProject",
        list_column_headers=("Customer", "Project Code"),
    ),
}

PARTNER_LIST_PAGE_CONFIGS: dict[str, EtmsCatalogueListPageConfig] = {
    "partner_group": EtmsCatalogueListPageConfig(
        page_key="partner_group",
        title="Partner Group",
        page_hash="catalogue/partner-group",
        menu_li_id="catPartnerGroup",
        list_column_headers=("Code", "Group name (VI)"),
        catalogue_suite="partner",
    ),
    "partner_list": EtmsCatalogueListPageConfig(
        page_key="partner_list",
        title="Partner list",
        page_hash="catalogue/partner-list",
        menu_li_id="catPartner",
        list_column_headers=("Partner Group", "ID"),
        catalogue_suite="partner",
    ),
    "bank_account": EtmsCatalogueListPageConfig(
        page_key="bank_account",
        title="Bank Account",
        page_hash="catalogue/partner-account-bank",
        menu_li_id="catAccountBankOfPartner",
        list_column_headers=("Partner Group", "Partner Name"),
        catalogue_suite="partner",
    ),
    "booking_information": EtmsCatalogueListPageConfig(
        page_key="booking_information",
        title="Booking Information",
        page_hash="catalogue/customer-booking-info",
        menu_li_id="catCustomerBookingInfo",
        list_column_headers=("Partner", "Code"),
        catalogue_suite="partner",
    ),
}

CATALOGUE_LIST_PAGE_CONFIGS: dict[str, EtmsCatalogueListPageConfig] = {
    **TRANSPORT_NETWORK_LIST_PAGE_CONFIGS,
    **PARTNER_LIST_PAGE_CONFIGS,
}


class EtmsCatalogueListPage(EtmsCatalogueMenuPage):
    """Generic catalogue list page — Transport Network or Partner submenu."""

    def __init__(self, page, page_key: str) -> None:
        super().__init__(page)
        if page_key not in CATALOGUE_LIST_PAGE_CONFIGS:
            known = ", ".join(sorted(CATALOGUE_LIST_PAGE_CONFIGS))
            raise ValueError(f"Unknown catalogue list page_key '{page_key}'. Known: {known}")
        self._config = CATALOGUE_LIST_PAGE_CONFIGS[page_key]
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

    def _open_catalogue_suite_menu(self) -> None:
        if self._config.catalogue_suite == "partner":
            self.open_partner_menu()
        else:
            self.open_transport_network_menu()

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

    def _navigate_to_list_page(self) -> None:
        self._click_sidebar_link(
            self._menu_selectors(),
            f"{self._config.title} menu",
        )
        self.page.wait_for_url(
            lambda url: self.page_hash in url.lower().replace("_", "-"),
            timeout=settings.page_load_timeout,
        )
        self.wait_for_page_stable()

    def _wait_for_list_grid(self, min_rows: int) -> None:
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

    @log_method("Click catalogue list menu")
    def click_menu(self) -> EtmsCatalogueListPage:
        self._open_catalogue_suite_menu()
        self._navigate_to_list_page()
        self._wait_for_list_grid(min_rows=1)
        return self

    def load_page_for_performance(self, min_rows: int = 1) -> EtmsCatalogueListPage:
        """Click menu and wait for table — used by performance tests (no POM step logs)."""
        self._navigate_to_list_page()
        self._wait_for_list_grid(min_rows)
        return self


# Backward-compatible aliases (deprecated — prefer EtmsCatalogueListPage*)
EtmsTransportNetworkListPage = EtmsCatalogueListPage
EtmsPartnerListPage = EtmsCatalogueListPage
TransportNetworkListPageConfig = EtmsCatalogueListPageConfig
PartnerListPageConfig = EtmsCatalogueListPageConfig
