from __future__ import annotations

from dataclasses import dataclass

from automation.config import settings
from automation.logging import log_method
from automation.pages.common.list_grid_component import ListGridComponent
from automation.pages.etms.etms_catalogue_menu_page import EtmsCatalogueMenuPage


@dataclass(frozen=True)
class PartnerListPageConfig:
    page_key: str
    title: str
    page_hash: str
    menu_li_id: str
    list_column_headers: tuple[str, ...]


PARTNER_LIST_PAGE_CONFIGS: dict[str, PartnerListPageConfig] = {
    "partner_group": PartnerListPageConfig(
        page_key="partner_group",
        title="Partner Group",
        page_hash="catalogue/partner-group",
        menu_li_id="catPartnerGroup",
        list_column_headers=("Code", "Group name (VI)"),
    ),
    "partner_list": PartnerListPageConfig(
        page_key="partner_list",
        title="Partner list",
        page_hash="catalogue/partner-list",
        menu_li_id="catPartner",
        list_column_headers=("Partner Group", "ID"),
    ),
    "bank_account": PartnerListPageConfig(
        page_key="bank_account",
        title="Bank Account",
        page_hash="catalogue/partner-account-bank",
        menu_li_id="catAccountBankOfPartner",
        list_column_headers=("Partner Group", "Partner Name"),
    ),
    "booking_information": PartnerListPageConfig(
        page_key="booking_information",
        title="Booking Information",
        page_hash="catalogue/customer-booking-info",
        menu_li_id="catCustomerBookingInfo",
        list_column_headers=("Partner", "Code"),
    ),
}


class EtmsPartnerListPage(EtmsCatalogueMenuPage):
    """Generic list page — Catalogue > Partner > {title}."""

    def __init__(self, page, page_key: str) -> None:
        super().__init__(page)
        if page_key not in PARTNER_LIST_PAGE_CONFIGS:
            known = ", ".join(sorted(PARTNER_LIST_PAGE_CONFIGS))
            raise ValueError(f"Unknown Partner page_key '{page_key}'. Known: {known}")
        self._config = PARTNER_LIST_PAGE_CONFIGS[page_key]
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

    @log_method("Click Partner list menu")
    def click_menu(self) -> EtmsPartnerListPage:
        self.open_partner_menu()
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

    def load_page_for_performance(self, min_rows: int = 1) -> EtmsPartnerListPage:
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
