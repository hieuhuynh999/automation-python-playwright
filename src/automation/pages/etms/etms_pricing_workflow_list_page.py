from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass

from automation.config import settings
from automation.logging import log_method, logger
from automation.pages.common.list_grid_component import ListGridComponent
from automation.pages.etms.etms_catalogue_menu_page import (
    EtmsCatalogueMenuPage,
    _catalogue_submenu_link_by_label,
    _sidebar_link_by_href,
    etms_page_title_selectors,
    etms_pricing_filter_tab_selectors,
)


@dataclass(frozen=True)
class PricingWorkflowTabConfig:
    tab_key: str
    tab_label: str


PRICING_WORKFLOW_TAB_CONFIGS: dict[str, PricingWorkflowTabConfig] = {
    "updating": PricingWorkflowTabConfig("updating", "Updating"),
    "pending": PricingWorkflowTabConfig("pending", "Pending"),
    "accepted": PricingWorkflowTabConfig("accepted", "Accepted"),
    "active_bookable": PricingWorkflowTabConfig("active_bookable", "Active - Bookable"),
    "rejected": PricingWorkflowTabConfig("rejected", "Rejected"),
    "revoked": PricingWorkflowTabConfig("revoked", "Revoked"),
    "expired": PricingWorkflowTabConfig("expired", "Expired"),
    "all": PricingWorkflowTabConfig("all", "All"),
    "new": PricingWorkflowTabConfig("new", "New"),
    "checking_info": PricingWorkflowTabConfig("checking_info", "Checking Info"),
    "in_process": PricingWorkflowTabConfig("in_process", "In Process"),
    "bu_cancel": PricingWorkflowTabConfig("bu_cancel", "BU Cancel"),
    "customer_cancel": PricingWorkflowTabConfig("customer_cancel", "Customer Cancel"),
    "finished": PricingWorkflowTabConfig("finished", "Finished"),
    "accounting_deposit_paid": PricingWorkflowTabConfig(
        "accounting_deposit_paid",
        "Accounting - Deposit Paid",
    ),
    "handed_over_cs": PricingWorkflowTabConfig(
        "handed_over_cs",
        "Handed Over to CS/Messenger",
    ),
    "handed_over_ops": PricingWorkflowTabConfig(
        "handed_over_ops",
        "Handed Over to OPS/Customer",
    ),
    "handed_over_accounting": PricingWorkflowTabConfig(
        "handed_over_accounting",
        "Handed Over to Accounting",
    ),
    "assigned_to_driver": PricingWorkflowTabConfig(
        "assigned_to_driver",
        "Assigned To Driver",
    ),
    "arrived_pickup_place": PricingWorkflowTabConfig(
        "arrived_pickup_place",
        "Arrived Pickup Place",
    ),
    "on_delivery": PricingWorkflowTabConfig("on_delivery", "On Delivery"),
    "arrived_delivery_place": PricingWorkflowTabConfig(
        "arrived_delivery_place",
        "Arrived Delivery Place",
    ),
    "delivered": PricingWorkflowTabConfig("delivered", "Delivered"),
    "finish": PricingWorkflowTabConfig("finish", "Finish"),
    "cancel": PricingWorkflowTabConfig("cancel", "Cancel"),
    "accept": PricingWorkflowTabConfig("accept", "Accept"),
    "reject": PricingWorkflowTabConfig("reject", "Reject"),
}

DEFAULT_PRICING_WORKFLOW_TAB = "updating"


def _performance_menu_opener(method_name: str) -> Callable[[EtmsCatalogueMenuPage], None]:
    def opener(nav_page: EtmsCatalogueMenuPage) -> None:
        getattr(nav_page, method_name)()

    return opener


_PERFORMANCE_MENU_SUITE_OPENERS: dict[str, Callable[[EtmsCatalogueMenuPage], None]] = {
    "common": _performance_menu_opener("open_pricing_common_menu"),
    "fcl": _performance_menu_opener("open_pricing_fcl_menu"),
    "lcl": _performance_menu_opener("open_pricing_lcl_menu"),
    "distribution": _performance_menu_opener("open_pricing_distribution_menu"),
    "pricing_report": _performance_menu_opener("open_pricing_report_menu"),
    "quotation": _performance_menu_opener("open_quotation_menu"),
    "customer_service_fcl": _performance_menu_opener("open_customer_service_fcl_menu"),
    "customer_service_lcl_ftl": _performance_menu_opener("open_customer_service_lcl_ftl_menu"),
    "customer_service_soa_outsource": _performance_menu_opener(
        "open_customer_service_soa_outsource_menu"
    ),
    "operation_common": _performance_menu_opener("open_operation_common_menu"),
    "operation_fcl": _performance_menu_opener("open_operation_fcl_menu"),
    "operation_lcl_ftl": _performance_menu_opener("open_operation_lcl_ftl_menu"),
}


class EtmsPricingWorkflowListPage(EtmsCatalogueMenuPage):
    """Pricing > Common list pages with workflow filter-tab (button/span on VFC)."""

    page_key: str
    page_hash: str
    title: str
    menu_li_id: str = ""
    sidebar_menu_labels: tuple[str, ...] = ()
    list_column_headers: tuple[str, ...] = ("Code",)
    optional_tab_keys: tuple[str, ...] = ()
    page_workflow_tab_keys: tuple[str, ...] = ()
    pricing_menu_suite: str = "common"
    default_workflow_tab: str = "updating"

    @property
    def performance_menu_suite(self) -> str:
        """Suite key for sidebar submenu navigation during performance tests."""
        override = self.__class__.__dict__.get("performance_menu_suite")
        if isinstance(override, str):
            return override
        return self.pricing_menu_suite

    loading_overlay_selectors = [
        ".m-blockui",
        ".block-ui-wrapper.block-ui-active",
        "xpath=//div[contains(@class,'block-ui') and contains(@class,'active')]",
        ".ng-progress-bar[active='true']",
    ]

    def __init__(self, page) -> None:
        super().__init__(page)
        self._list_grid = ListGridComponent(self, f"{self.title} list grid")

    def _menu_selectors(self) -> list[str]:
        labels = self.sidebar_menu_labels or (self.title,)
        selectors: list[str] = []
        if self.menu_li_id:
            selectors.append(f"#{self.menu_li_id} > a.nav-link")
            selectors.append(
                (
                    f"xpath=//li[@id='{self.menu_li_id}']"
                    f"//span[normalize-space()='{labels[0]}']"
                    "/ancestor::a[contains(@class,'nav-link')][1]"
                )
            )
        for label in labels:
            selectors.extend(
                [
                    _catalogue_submenu_link_by_label(label),
                    (
                        "xpath=//a[contains(@class,'nav-link')]"
                        f"[.//span[normalize-space()='{label}']]"
                    ),
                ]
            )
        selectors.append(_sidebar_link_by_href(self.page_hash))
        return list(dict.fromkeys(selectors))

    def _open_pricing_suite_menu(self) -> None:
        opener = _PERFORMANCE_MENU_SUITE_OPENERS.get(self.performance_menu_suite)
        if opener is None:
            self.open_pricing_common_menu()
            return
        opener(self)

    def _navigate_to_list_page(self) -> None:
        self._click_sidebar_link(
            self._menu_selectors(),
            f"{self.title} menu",
        )
        self._wait_for_url_hash(self.page_hash)
        self.wait_for_page_stable()
        self.wait_for_visible(
            self.page_title_selectors,
            f"{self.title} page title",
        )

    @property
    def list_grid(self) -> ListGridComponent:
        return self._list_grid

    @property
    def page_title_selectors(self) -> list[str]:
        return etms_page_title_selectors(self.title)

    @property
    def list_table_selectors(self) -> list[str]:
        return self.list_table_selectors_for_tab(self.default_workflow_tab)

    def _tab_config(self, tab_key: str) -> PricingWorkflowTabConfig:
        if self.page_workflow_tab_keys and tab_key not in self.page_workflow_tab_keys:
            known = ", ".join(self.page_workflow_tab_keys)
            raise ValueError(
                f"Tab '{tab_key}' not on {self.title}. Available: {known}"
            )
        if tab_key not in PRICING_WORKFLOW_TAB_CONFIGS:
            known = ", ".join(sorted(PRICING_WORKFLOW_TAB_CONFIGS))
            raise ValueError(f"Unknown workflow tab '{tab_key}'. Known: {known}")
        return PRICING_WORKFLOW_TAB_CONFIGS[tab_key]

    def _list_portlet_root(self) -> str:
        return (
            f"//*[contains(@class,'page-title') and contains(normalize-space(),'{self.title}')]"
            "/ancestor::div[contains(@class,'m-portlet') or contains(@class,'portlet')][1]"
        )

    def _list_portlet_body(self) -> str:
        return (
            f"{self._list_portlet_root()}"
            "//div[contains(@class,'m-portlet__body') or contains(@class,'portlet__body')]"
        )

    def _scroll_filter_tab_bar(self) -> None:
        bar_selectors = [
            f"xpath={self._list_portlet_body()}//ul[contains(@class,'filter-tab')]",
            f"xpath={self._list_portlet_root()}//ul[contains(@class,'filter-tab')]",
            "xpath=//ul[contains(@class,'filter-tab')]",
        ]
        bar = self.find_visible(bar_selectors)
        if bar is not None:
            bar.evaluate(
                "(el) => { el.scrollLeft = el.scrollWidth; }",
            )
            self.page.wait_for_timeout(settings.polling_interval)

    def list_table_selectors_for_tab(self, tab_key: str) -> list[str]:
        first_header = self.list_column_headers[0]
        tab_label = self._tab_config(tab_key).tab_label
        list_body = self._list_portlet_body()
        return [
            (
                "xpath=//th[contains(@id,'PriceRouteCost') "
                "and span[normalize-space()='Code']]"
            ),
            f"xpath=//table[.//th[normalize-space()='{first_header}']]//th",
            (
                "xpath=//ul[contains(@class,'filter-tab')]"
                f"//li[contains(@class,'active')]"
                f"//*[self::button or self::span or self::a]"
                f"[normalize-space()='{tab_label}' or .//span[normalize-space()='{tab_label}']]"
                "/ancestor::div[contains(@class,'m-portlet') or contains(@class,'portlet')][1]"
                "//table//th"
            ),
            f"xpath={list_body}//table//th",
            f"xpath=//th[normalize-space()='{first_header}']",
        ]

    def _filter_tab_selectors(self, tab_label: str) -> list[str]:
        list_body = self._list_portlet_body()
        portlet = self._list_portlet_root()
        scoped = etms_pricing_filter_tab_selectors(tab_label)
        title = self.title
        return [
            *scoped,
            f"xpath={list_body}//ul[contains(@class,'filter-tab')]"
            f"//button[normalize-space()='{tab_label}']",
            f"xpath={portlet}//ul[contains(@class,'filter-tab')]"
            f"//span[normalize-space()='{tab_label}']",
            (
                f"xpath=//*[contains(@class,'page-title') and contains(normalize-space(),'{title}')]"
                "/ancestor::div[contains(@class,'m-portlet') or contains(@class,'portlet')][1]"
                f"//button[normalize-space()='{tab_label}']"
            ),
            (
                f"xpath=//*[contains(@class,'page-title') and contains(normalize-space(),'{title}')]"
                "/ancestor::div[contains(@class,'m-portlet') or contains(@class,'portlet')][1]"
                f"//span[normalize-space()='{tab_label}']"
            ),
            (
                f"xpath=//ul[contains(@class,'filter-tab')]"
                f"//a[normalize-space()='{tab_label}']"
            ),
            (
                f"xpath=//ul[contains(@class,'filter-tab')]"
                f"//a[.//span[normalize-space()='{tab_label}']]"
            ),
            f"text='{tab_label}'",
        ]
        if "Active - Bookable" in tab_label or tab_label == "Active - Bookable":
            selectors.extend(
                [
                    (
                        "xpath=//ul[contains(@class,'filter-tab')]"
                        "//button[contains(normalize-space(),'Active') "
                        "and contains(normalize-space(),'Bookable')]"
                    ),
                    (
                        "xpath=//ul[contains(@class,'filter-tab')]"
                        "//span[contains(normalize-space(),'Active') "
                        "and contains(normalize-space(),'Bookable')]"
                    ),
                ]
            )
        return selectors

    def _is_on_list_page(self) -> bool:
        url = self.current_url.lower().replace("_", "-")
        return self.page_hash in url and self.find_visible(
            self.page_title_selectors,
        ) is not None

    def _is_filter_tab_active(self, tab_label: str) -> bool:
        lit = tab_label.strip()
        active_selectors = [
            (
                "xpath=//ul[contains(@class,'filter-tab')]"
                "//li[contains(@class,'active')]"
                f"//*[self::button or self::span or self::a]"
                f"[normalize-space()='{lit}' or .//span[normalize-space()='{lit}']]"
            ),
            (
                "xpath=//ul[contains(@class,'filter-tab')]"
                f"//button[contains(@class,'active') and "
                f"(normalize-space()='{lit}' or .//span[normalize-space()='{lit}'])]"
            ),
            (
                "xpath=//ul[contains(@class,'filter-tab')]"
                f"//a[contains(@class,'active') and normalize-space()='{lit}']"
            ),
            (
                f"xpath=//button[contains(@class,'active') and normalize-space()='{lit}']"
            ),
        ]
        return self.find_visible(active_selectors) is not None

    def _wait_for_loading_overlay_hidden(self, timeout: int | None = None) -> None:
        timeout = timeout or settings.browser_timeout
        deadline = time.monotonic() + timeout / 1000
        while time.monotonic() < deadline:
            if self.find_visible(self.loading_overlay_selectors) is None:
                return
            self.page.wait_for_timeout(settings.polling_interval)

    def _wait_for_filter_tab_active(self, tab_label: str, timeout: int | None = None) -> bool:
        timeout = timeout or settings.tab_switch_timeout
        deadline = time.monotonic() + timeout / 1000
        while time.monotonic() < deadline:
            if self._is_filter_tab_active(tab_label):
                return True
            self.page.wait_for_timeout(settings.polling_interval)
        return False

    def _wait_for_tab_content_loaded(
        self,
        tab_key: str,
        min_rows: int,
        *,
        allow_no_data: bool,
    ) -> int:
        table_selectors = self.list_table_selectors_for_tab(tab_key)
        config = self._tab_config(tab_key)
        tab_timeout = settings.tab_switch_timeout
        self._wait_for_loading_overlay_hidden(timeout=tab_timeout)
        self.list_grid.wait_until_ready(
            table_selectors,
            f"{self.title} {config.tab_label} table",
            timeout=tab_timeout,
        )
        self.list_grid.verify_column_headers(
            list(self.list_column_headers),
            table_selectors=table_selectors,
        )
        if allow_no_data:
            return self.list_grid.wait_for_data_rows_or_no_data(
                min_rows=min_rows,
                table_selectors=table_selectors,
                timeout=tab_timeout,
            )
        return self.list_grid.wait_for_data_rows(
            min_rows=min_rows,
            table_selectors=table_selectors,
            timeout=tab_timeout,
        )

    @log_method("Open pricing list page via sidebar menu")
    def open_via_sidebar_menu(self) -> EtmsPricingWorkflowListPage:
        self._open_pricing_suite_menu()
        self._navigate_to_list_page()
        return self

    def _is_tab_available(self, tab_key: str) -> bool:
        tab_label = self._tab_config(tab_key).tab_label
        self._scroll_filter_tab_bar()
        return self.find_visible(self._filter_tab_selectors(tab_label)) is not None

    @log_method("Click workflow filter tab")
    def click_workflow_tab(
        self,
        tab_key: str,
        *,
        force: bool = False,
    ) -> EtmsPricingWorkflowListPage:
        config = self._tab_config(tab_key)
        tab_label = config.tab_label

        if tab_key in self.optional_tab_keys and not self._is_tab_available(tab_key):
            logger.info(
                "Optional tab '{}' not available on {} — skip click",
                tab_label,
                self.title,
            )
            return self

        self.list_grid.wait_until_ready(
            self.list_table_selectors_for_tab(tab_key),
            f"{self.title} table",
        )
        self._wait_for_loading_overlay_hidden()

        if not force and self._is_filter_tab_active(tab_label):
            self._wait_for_tab_content_loaded(
                tab_key,
                min_rows=0,
                allow_no_data=True,
            )
            return self

        self._perform_tab_click(tab_key)
        self._wait_for_loading_overlay_hidden()

        if not self._wait_for_filter_tab_active(tab_label):
            logger.info(
                "Tab '{}' active class not detected — verify grid content instead",
                tab_label,
            )

        return self

    def _perform_tab_click(self, tab_key: str) -> None:
        """Click workflow tab only — no pre-click grid settle (used by performance timer)."""
        tab_label = self._tab_config(tab_key).tab_label
        self._scroll_filter_tab_bar()
        tab = self.wait_for_visible(
            self._filter_tab_selectors(tab_label),
            f"{self.title} tab {tab_label}",
        )
        tab.scroll_into_view_if_needed()
        tab.click(force=True)

    @log_method("Prepare workflow tab for performance measurement")
    def prepare_workflow_tab_performance(
        self,
        *,
        tab_key: str | None = None,
        min_rows: int = 1,
        allow_no_data: bool = False,
        first_page_step: bool = False,
    ) -> str:
        """Settle before perf timer. Returns 'page_load', 'click', or 'skipped'.

        Default workflow tab on the first step of each page: timer measures sidebar
        page click → data. Other tabs: timer measures tab click → data only.
        """
        del min_rows, allow_no_data
        active_tab = tab_key or self.default_workflow_tab

        if active_tab in self.optional_tab_keys and self._is_on_list_page():
            if not self._is_tab_available(active_tab):
                logger.info(
                    "Optional tab '{}' skipped for performance on {}",
                    self._tab_config(active_tab).tab_label,
                    self.title,
                )
                return "skipped"

        if first_page_step and active_tab == self.default_workflow_tab:
            return "page_load"

        if not self._is_on_list_page():
            self._navigate_to_list_page()

        self._wait_for_loading_overlay_hidden()
        self.list_grid.wait_until_ready(
            self.list_table_selectors_for_tab(active_tab),
            f"{self.title} table",
        )
        self._scroll_filter_tab_bar()
        return "click"

    def run_workflow_tab_performance_measurement(
        self,
        *,
        tab_key: str | None = None,
        min_rows: int = 1,
        allow_no_data: bool = False,
        mode: str = "click",
    ) -> None:
        """Timed segment: page sidebar click or tab click → grid data or 'No Data'."""
        if mode == "skipped":
            return

        active_tab = tab_key or self.default_workflow_tab
        if mode == "page_load":
            self._navigate_to_list_page()
        elif mode == "click":
            self._perform_tab_click(active_tab)

        self._wait_for_tab_content_loaded(
            active_tab,
            min_rows,
            allow_no_data=allow_no_data,
        )

    def count_data_rows_for_tab(self, tab_key: str) -> int:
        if self.list_grid.is_no_data_displayed(
            table_selectors=self.list_table_selectors_for_tab(tab_key),
        ):
            return 0
        return self.list_grid.count_data_rows(
            table_selectors=self.list_table_selectors_for_tab(tab_key),
        )

    def has_no_data_for_tab(self, tab_key: str) -> bool:
        return self.list_grid.is_no_data_displayed(
            table_selectors=self.list_table_selectors_for_tab(tab_key),
        )

    def confirm_grid_loaded(
        self,
        min_rows: int = 1,
        *,
        tab_key: str | None = None,
        allow_no_data: bool = False,
    ) -> EtmsPricingWorkflowListPage:
        active_tab = tab_key or self.default_workflow_tab
        self._wait_for_loading_overlay_hidden()
        self._wait_for_tab_content_loaded(
            active_tab,
            min_rows,
            allow_no_data=allow_no_data,
        )
        return self

    def prepare_for_performance(
        self,
        *,
        tab_key: str | None = None,
        min_rows: int = 1,
        allow_no_data: bool = False,
        first_page_step: bool = False,
    ) -> str:
        return self.prepare_workflow_tab_performance(
            tab_key=tab_key,
            min_rows=min_rows,
            allow_no_data=allow_no_data,
            first_page_step=first_page_step,
        )

    def run_performance_measurement(
        self,
        *,
        tab_key: str | None = None,
        min_rows: int = 1,
        allow_no_data: bool = False,
        mode: str = "click",
    ) -> None:
        self.run_workflow_tab_performance_measurement(
            tab_key=tab_key,
            min_rows=min_rows,
            allow_no_data=allow_no_data,
            mode=mode,
        )

    def load_page_for_performance(
        self,
        min_rows: int = 1,
        *,
        tab_key: str | None = None,
        allow_no_data: bool = False,
    ) -> EtmsPricingWorkflowListPage:
        mode = self.prepare_for_performance(
            tab_key=tab_key,
            min_rows=min_rows,
            allow_no_data=allow_no_data,
        )
        if mode == "skipped":
            return self
        self.run_performance_measurement(
            tab_key=tab_key,
            min_rows=min_rows,
            allow_no_data=allow_no_data,
            mode=mode,
        )
        return self

    def wait_before_next_pricing_navigation(self) -> EtmsPricingWorkflowListPage:
        self._wait_for_loading_overlay_hidden()
        self.wait_for_page_stable()
        return self


class EtmsCostOfRouteWorkflowPage(EtmsPricingWorkflowListPage):
    """Cost Of Route — Pricing > Common > workflow tabs (performance)."""

    page_key = "cost_of_route"
    page_hash = "pricing/cost-of-route"
    title = "Cost Of Route"
    sidebar_menu_labels = ("Cost Of Route",)
    list_column_headers = ("Code",)


class EtmsPriceTollBuyingPage(EtmsPricingWorkflowListPage):
    """Price Toll Buying — Pricing > Common > workflow tabs (performance)."""

    page_key = "price_toll_buying"
    page_hash = "pricing/toll-buying"
    title = "Price Toll Buying"
    sidebar_menu_labels = ("Price Toll Buying", "Toll Buying")
    list_column_headers = ("Code",)
    optional_tab_keys = ("expired",)

    @property
    def page_title_selectors(self) -> list[str]:
        from automation.pages.etms.etms_catalogue_menu_page import etms_page_title_selectors

        titles = ("Price Toll Buying", "Toll Buying")
        selectors: list[str] = []
        for label in titles:
            selectors.extend(etms_page_title_selectors(label))
        return list(dict.fromkeys(selectors))


class EtmsFclRateCardListPage(EtmsPricingWorkflowListPage):
    """FCL Rate Card List — default tab Pending; includes Active - Bookable."""

    page_key = "fcl_rate_card_list"
    page_hash = "pricing/fcl/fcl-rate-card-list"
    title = "FCL Rate Card List"
    sidebar_menu_labels = ("FCL Rate Card List",)
    list_column_headers = ("Code",)
    pricing_menu_suite = "fcl"
    default_workflow_tab = "pending"
    page_workflow_tab_keys = (
        "updating",
        "pending",
        "accepted",
        "active_bookable",
        "rejected",
        "revoked",
    )


class EtmsFclBuyingPricePage(EtmsPricingWorkflowListPage):
    """FCL Buying Price — Pricing > FCL Pricing."""

    page_key = "fcl_buying_price"
    page_hash = "pricing/fcl/fcl-buying"
    title = "FCL Buying Price"
    sidebar_menu_labels = ("FCL Buying Price",)
    list_column_headers = ("Code",)
    pricing_menu_suite = "fcl"
    page_workflow_tab_keys = (
        "updating",
        "pending",
        "accepted",
        "rejected",
        "revoked",
    )


class EtmsFclRentingContainerPage(EtmsPricingWorkflowListPage):
    """Renting Container FCL — Pricing > FCL Pricing."""

    page_key = "fcl_renting_container"
    page_hash = "pricing/fcl/fcl-renting-container"
    title = "Renting Container FCL"
    sidebar_menu_labels = ("Renting Container FCL",)
    list_column_headers = ("Code",)
    pricing_menu_suite = "fcl"
    page_workflow_tab_keys = (
        "updating",
        "pending",
        "accepted",
        "rejected",
        "expired",
        "revoked",
    )


class EtmsFclRentingVehiclePage(EtmsPricingWorkflowListPage):
    """Renting vehicle — Pricing > FCL Pricing."""

    page_key = "fcl_renting_vehicle"
    page_hash = "pricing/fcl/fcl-renting-vehicle"
    title = "Renting vehicle"
    sidebar_menu_labels = ("Renting vehicle", "Renting Vehicle")
    list_column_headers = ("Code",)
    pricing_menu_suite = "fcl"
    page_workflow_tab_keys = (
        "updating",
        "pending",
        "accepted",
        "rejected",
        "expired",
        "revoked",
    )

    @property
    def page_title_selectors(self) -> list[str]:
        titles = ("Renting vehicle", "Renting Vehicle")
        selectors: list[str] = []
        for label in titles:
            selectors.extend(etms_page_title_selectors(label))
        return list(dict.fromkeys(selectors))


class EtmsLclRateCardPage(EtmsPricingWorkflowListPage):
    """3. LCL Rate Card — Pricing > LCL Pricing."""

    page_key = "lcl_rate_card"
    page_hash = "pricing/rate-card-list"
    title = "3. LCL Rate Card"
    sidebar_menu_labels = ("3. LCL Rate Card", "LCL Rate Card")
    list_column_headers = ("Code",)
    pricing_menu_suite = "lcl"
    page_workflow_tab_keys = (
        "updating",
        "pending",
        "accepted",
        "rejected",
        "revoked",
    )

    @property
    def page_title_selectors(self) -> list[str]:
        titles = ("3. LCL Rate Card", "LCL Rate Card")
        selectors: list[str] = []
        for label in titles:
            selectors.extend(etms_page_title_selectors(label))
        return list(dict.fromkeys(selectors))


class EtmsLclBuyingPage(EtmsPricingWorkflowListPage):
    """LCL Buying — Pricing > LCL Pricing."""

    page_key = "lcl_buying"
    page_hash = "pricing/buying"
    title = "LCL Buying"
    sidebar_menu_labels = ("LCL Buying",)
    list_column_headers = ("Code",)
    pricing_menu_suite = "lcl"
    page_workflow_tab_keys = (
        "updating",
        "pending",
        "accepted",
        "rejected",
        "revoked",
    )


class EtmsDistributionRateCardPage(EtmsPricingWorkflowListPage):
    """2. Distribution Rate Card — Pricing > Distribution Pricing."""

    page_key = "distribution_rate_card"
    page_hash = "pricing/dtb/dtb-rate-card-list"
    title = "2. Distribution Rate Card"
    sidebar_menu_labels = ("2. Distribution Rate Card", "Distribution Rate Card")
    list_column_headers = ("Code",)
    pricing_menu_suite = "distribution"
    page_workflow_tab_keys = (
        "updating",
        "pending",
        "accepted",
        "active_bookable",
        "rejected",
        "revoked",
    )

    @property
    def page_title_selectors(self) -> list[str]:
        from automation.pages.etms.etms_catalogue_menu_page import etms_page_title_selectors

        titles = ("2. Distribution Rate Card", "Distribution Rate Card")
        selectors: list[str] = []
        for label in titles:
            selectors.extend(etms_page_title_selectors(label))
        return list(dict.fromkeys(selectors))


class EtmsDistributionBuyingPage(EtmsPricingWorkflowListPage):
    """Distribution Buying — Pricing > Distribution Pricing."""

    page_key = "distribution_buying"
    page_hash = "pricing/buying-per-trip-v2"
    title = "Distribution Buying"
    sidebar_menu_labels = ("Distribution Buying",)
    list_column_headers = ("Code",)
    pricing_menu_suite = "distribution"
    page_workflow_tab_keys = (
        "updating",
        "pending",
        "accepted",
        "rejected",
        "revoked",
    )


class EtmsCommissionRateCardPage(EtmsPricingWorkflowListPage):
    """Commission Rate Card — Pricing > workflow tabs (Updating default)."""

    page_key = "commission_rate_card"
    page_hash = "pricing/commission-rate-card"
    title = "Commission Rate Card"
    sidebar_menu_labels = ("Commission Rate Card",)
    list_column_headers = ("Code",)
    pricing_menu_suite = "pricing_report"
    page_workflow_tab_keys = (
        "updating",
        "pending",
        "accepted",
        "rejected",
    )


class EtmsFclQuotationListPage(EtmsPricingWorkflowListPage):
    """FCL Quotation List — Quotation > workflow tabs (Pending default)."""

    page_key = "fcl_quotation_list"
    page_hash = "pricing/fcl/fcl-quotation-list"
    title = "FCL Quotation List"
    sidebar_menu_labels = ("FCL Quotation List",)
    list_column_headers = ("Code",)
    pricing_menu_suite = "quotation"
    default_workflow_tab = "pending"
    page_workflow_tab_keys = (
        "pending",
        "accepted",
        "rejected",
        "revoked",
    )
