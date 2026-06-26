from __future__ import annotations

from automation.config import settings
from automation.pages.etms.etms_pricing_workflow_list_page import EtmsPricingWorkflowListPage
from automation.pages.etms.etms_quotation_form_page import EtmsQuotationFormPage


class EtmsCustomerServiceWorkflowPage(EtmsPricingWorkflowListPage):
    """Customer Service workflow list pages — filter tabs, generic grid, optional empty state."""

    list_column_headers: tuple[str, ...] = ()
    performance_menu_suite: str = "customer_service_fcl"

    def list_table_selectors_for_tab(self, tab_key: str) -> list[str]:
        del tab_key
        list_body = self._list_portlet_body()
        return [
            f"xpath={list_body}//ngx-datatable//datatable-header-cell",
            f"xpath={list_body}//table//th",
            "xpath=//div[contains(@class,'m-portlet__body')]//ngx-datatable//datatable-header-cell",
            "xpath=//div[contains(@class,'m-portlet__body')]//table//th",
            "xpath=//ngx-datatable//datatable-header-cell",
        ]

    def _wait_for_tab_content_loaded(
        self,
        tab_key: str,
        min_rows: int,
        *,
        allow_no_data: bool,
    ) -> int:
        del tab_key
        tab_timeout = settings.tab_switch_timeout
        self._wait_for_loading_overlay_hidden(timeout=tab_timeout)
        self.wait_for_page_stable()
        if allow_no_data:
            return self.list_grid.wait_for_data_rows_or_no_data(
                min_rows=min_rows,
                table_selectors=None,
                timeout=tab_timeout,
            )
        return self.list_grid.wait_for_data_rows(
            min_rows=min_rows,
            table_selectors=None,
            timeout=tab_timeout,
        )

    def prepare_workflow_tab_performance(
        self,
        *,
        tab_key: str | None = None,
        min_rows: int = 1,
        allow_no_data: bool = False,
        first_page_step: bool = False,
    ) -> str:
        del min_rows, allow_no_data
        active_tab = tab_key or self.default_workflow_tab

        if active_tab in self.optional_tab_keys and self._is_on_list_page():
            if not self._is_tab_available(active_tab):
                return "skipped"

        if first_page_step and active_tab == self.default_workflow_tab:
            return "page_load"

        if not self._is_on_list_page():
            self._navigate_to_list_page()

        self._wait_for_loading_overlay_hidden()
        self.wait_for_page_stable()
        self._scroll_filter_tab_bar()
        return "click"


class EtmsFclBookingPage(EtmsCustomerServiceWorkflowPage):
    """FCL Booking — Customer Service > FCL > workflow tabs (All default)."""

    page_key = "fcl_booking"
    page_hash = "customer/fcl-booking"
    title = "FCL Booking"
    sidebar_menu_labels = ("FCL Booking",)
    performance_menu_suite = "customer_service_fcl"
    default_workflow_tab = "all"
    page_workflow_tab_keys = (
        "all",
        "new",
        "checking_info",
        "in_process",
        "bu_cancel",
        "customer_cancel",
        "finished",
    )


class EtmsContainerDepositManagementPage(EtmsCustomerServiceWorkflowPage):
    """Container Deposit Management — Customer Service > FCL > workflow tabs (New default)."""

    page_key = "container_deposit_management"
    page_hash = "customer/management-container-deposit"
    title = "Container Deposit Management"
    sidebar_menu_labels = ("Container Deposit Management",)
    performance_menu_suite = "customer_service_fcl"
    default_workflow_tab = "new"
    page_workflow_tab_keys = (
        "new",
        "accounting_deposit_paid",
        "handed_over_cs",
        "handed_over_ops",
        "handed_over_accounting",
        "finished",
    )


class EtmsLclFtlBookingPage(EtmsCustomerServiceWorkflowPage):
    """LCL/FTL Booking — workflow tabs (All default)."""

    page_key = "lcl_ftl_booking"
    page_hash = "customer/booking"
    title = "LCL/FTL Booking"
    sidebar_menu_labels = ("LCL/FTL Booking",)
    performance_menu_suite = "customer_service_lcl_ftl"
    default_workflow_tab = "all"
    page_workflow_tab_keys = (
        "all",
        "new",
        "checking_info",
        "assigned_to_driver",
        "arrived_pickup_place",
        "on_delivery",
        "arrived_delivery_place",
        "delivered",
        "finish",
        "cancel",
    )


class EtmsLclShipmentManagementPage(EtmsQuotationFormPage):
    """LCL Shipment Management — page load until View Report control is visible and enabled."""

    page_key = "lcl_shipment_management"
    page_hash = "customer/lcl-shipment-management"
    title = "LCL Shipment Management"
    sidebar_menu_labels = ("LCL Shipment Management",)
    ready_control_label = "View Report"


class EtmsSoaForOutsourcePage(EtmsCustomerServiceWorkflowPage):
    """SOA For Outsource — Customer Service > workflow tabs (All default)."""

    page_key = "soa_for_outsource"
    page_hash = "customer/soa-for-outsource"
    title = "SOA For Outsource"
    sidebar_menu_labels = ("SOA For Outsource",)
    performance_menu_suite = "customer_service_soa_outsource"
    default_workflow_tab = "all"
    page_workflow_tab_keys = (
        "all",
        "new",
        "accept",
        "reject",
    )
