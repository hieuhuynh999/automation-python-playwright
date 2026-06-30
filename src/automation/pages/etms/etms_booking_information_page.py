from __future__ import annotations

import time

from automation.config import settings
from automation.logging import log_method
from automation.pages.etms.etms_catalogue_menu_page import (
    _catalogue_submenu_link_by_label,
    _sidebar_child_link,
    _sidebar_link_by_href,
)
from automation.pages.etms.etms_catalogue_tabbed_list_page import (
    EtmsCatalogueTabConfig,
    EtmsCatalogueTabbedListPage,
)

ETMS_BOOKING_INFORMATION_TAB_CONFIGS: dict[str, EtmsCatalogueTabConfig] = {
    "goods_information": EtmsCatalogueTabConfig(
        tab_key="goods_information",
        tab_label="Goods Information",
        list_column_headers=("Partner", "Code"),
    ),
    "pickup_delivery_places": EtmsCatalogueTabConfig(
        tab_key="pickup_delivery_places",
        tab_label="Pickup/Delivery Places",
        list_column_headers=("Partner", "Place Name"),
    ),
    "shipment_note": EtmsCatalogueTabConfig(
        tab_key="shipment_note",
        tab_label="Shipment Note",
        list_column_headers=("Edit",),
    ),
    "project_vehicle": EtmsCatalogueTabConfig(
        tab_key="project_vehicle",
        tab_label="Project Vehicle",
        list_column_headers=("Customer", "Vehicle"),
    ),
}

DEFAULT_ETMS_BOOKING_INFORMATION_TAB = "goods_information"

_SHIPMENT_NOTE_ITEM_SELECTORS = [
    "xpath=//div[@class='row same-height-wrapper']//span[text()='Edit']",
    "xpath=//div[contains(@class,'same-height-wrapper')]//span[normalize-space()='Edit']",
]


class EtmsBookingInformationPage(EtmsCatalogueTabbedListPage):
    """Booking Information — Catalogue > Partner > tabbed list screens."""

    page_key = "booking_information"
    page_hash = "catalogue/customer-booking-info"
    title = "Booking Information"
    menu_li_id = "catCustomerBookingInfo"
    default_tab_key = DEFAULT_ETMS_BOOKING_INFORMATION_TAB
    tab_configs = ETMS_BOOKING_INFORMATION_TAB_CONFIGS
    _landing_tab_key = "goods_information"

    def _menu_selectors(self) -> list[str]:
        """Partner submenu leaf — scope under catPartners so sidebar click navigates."""
        title = self.title
        return list(
            dict.fromkeys(
                [
                    f"#{self.menu_li_id} > a.nav-link",
                    (
                        "xpath=//li[@id='catPartners']"
                        f"//li[@id='{self.menu_li_id}']//a[contains(@class,'nav-link')]"
                    ),
                    (
                        f"xpath=//li[@id='{self.menu_li_id}']"
                        f"//span[normalize-space()='{title}']"
                        "/ancestor::a[contains(@class,'nav-link')][1]"
                    ),
                    _sidebar_child_link("Partner", title),
                    _sidebar_link_by_href(self.page_hash),
                    (
                        "xpath=//a[contains(@class,'nav-link')]"
                        f"[.//span[normalize-space()='{title}']]"
                    ),
                    _catalogue_submenu_link_by_label(title),
                ]
            )
        )

    def _navigate_to_page(self, tab_key: str | None = None) -> None:
        self.open_partner_menu()
        super()._navigate_to_page(tab_key)

    def list_table_selectors_for_tab(self, tab_key: str) -> list[str]:
        if tab_key == "shipment_note":
            return list(_SHIPMENT_NOTE_ITEM_SELECTORS)
        config = self._tab_config(tab_key)
        first_header = config.list_column_headers[0]
        tab_label = config.tab_label
        return [
            f"xpath=//table[.//th[normalize-space()='{first_header}']]//th",
            (
                "xpath=//div[contains(@class,'nav-tabs')]"
                f"//a[contains(@class,'active') and normalize-space()='{tab_label}']"
                "/ancestor::div[contains(@class,'m-portlet') or contains(@class,'portlet')][1]"
                "//table//th"
            ),
            (
                f"xpath=//*[self::h3 or contains(@class,'page-title')]"
                f"[normalize-space()='{self.title}' or contains(normalize-space(),'{self.title}')]"
                "/ancestor::div[contains(@class,'m-portlet') or contains(@class,'portlet')][1]"
                "//table//th"
            ),
            f"xpath=//th[normalize-space()='{first_header}']",
        ]

    def _count_shipment_note_items(self) -> int:
        for selector in _SHIPMENT_NOTE_ITEM_SELECTORS:
            count = self.page.locator(selector).count()
            if count > 0:
                return count
        return 0

    def _wait_shipment_note_items(self, min_rows: int) -> int:
        timeout = settings.browser_timeout
        deadline = time.monotonic() + timeout / 1000
        while time.monotonic() < deadline:
            count = self._count_shipment_note_items()
            if count >= min_rows:
                return count
            self.page.wait_for_timeout(settings.polling_interval)
        raise AssertionError(
            "Booking Information Shipment Note list not loaded — expected at least "
            f"{min_rows} visible 'Edit' item(s) after {timeout}ms. "
            f"Found: {self._count_shipment_note_items()}."
        )

    def _ensure_tab_active(self, tab_key: str) -> None:
        """Goods Information is the landing tab — skip click when page opens on it."""
        if tab_key == self._landing_tab_key:
            return
        self._activate_tab(tab_key)

    def _wait_tab_grid(self, tab_key: str, min_rows: int) -> None:
        if tab_key == "shipment_note":
            self._wait_shipment_note_items(min_rows)
            return
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
        if tab_key == "shipment_note":
            return self._count_shipment_note_items()
        return super().count_data_rows_for_tab(tab_key)

    @log_method("Click Booking Information menu")
    def click_menu(
        self,
        tab_key: str = DEFAULT_ETMS_BOOKING_INFORMATION_TAB,
    ) -> EtmsBookingInformationPage:
        self.open_partner_menu()
        self._navigate_to_page()
        self._ensure_tab_active(tab_key)
        self._wait_tab_grid(tab_key, min_rows=1)
        return self
