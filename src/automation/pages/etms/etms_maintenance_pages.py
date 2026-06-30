from __future__ import annotations

from automation.pages.etms.etms_customer_service_pages import EtmsCustomerServiceWorkflowPage
from automation.pages.etms.etms_pricing_workflow_list_page import (
    PRICING_WORKFLOW_TAB_CONFIGS,
    PricingWorkflowTabConfig,
)

MAINTENANCE_WORKFLOW_TAB_CONFIGS: dict[str, PricingWorkflowTabConfig] = {
    **PRICING_WORKFLOW_TAB_CONFIGS,
    "latest_vehicle_odometer": PricingWorkflowTabConfig(
        "latest_vehicle_odometer",
        "Latest Vehicle Odometer",
    ),
    "vehicle_need_repair": PricingWorkflowTabConfig(
        "vehicle_need_repair",
        "Vehicle Need Repair",
    ),
    "not_send_request": PricingWorkflowTabConfig("not_send_request", "Not Send Request"),
    "waiting_fleet_manager_approval": PricingWorkflowTabConfig(
        "waiting_fleet_manager_approval",
        "Waiting Fleet Manager Approval",
    ),
    "waiting_director_approval": PricingWorkflowTabConfig(
        "waiting_director_approval",
        "Waiting Director Approval",
    ),
    "payment": PricingWorkflowTabConfig("payment", "Payment"),
    "rejected_request": PricingWorkflowTabConfig("rejected_request", "Rejected Request"),
    "month_plan": PricingWorkflowTabConfig("month_plan", "Month Plan"),
    "annual_plan": PricingWorkflowTabConfig("annual_plan", "Annual Plan"),
    "maintenance_type": PricingWorkflowTabConfig("maintenance_type", "Maintenance Type"),
    "repair_type": PricingWorkflowTabConfig("repair_type", "Repair Type"),
}


class EtmsMaintenanceWorkflowPage(EtmsCustomerServiceWorkflowPage):
    """Maintenance and Repair workflow list pages — filter tabs + generic grid."""

    performance_menu_suite: str = "maintenance_and_repair"
    list_column_headers: tuple[str, ...] = ()

    def _tab_config(self, tab_key: str) -> PricingWorkflowTabConfig:
        if tab_key in MAINTENANCE_WORKFLOW_TAB_CONFIGS:
            return MAINTENANCE_WORKFLOW_TAB_CONFIGS[tab_key]
        return super()._tab_config(tab_key)


class EtmsVehicleNeedMaintainingPage(EtmsMaintenanceWorkflowPage):
    page_key = "vehicle_need_maintaining"
    page_hash = "maintenance/main-vehicle-need-repair"
    title = "Vehicle need maintaining"
    sidebar_menu_labels = ("Vehicle need maintaining",)
    default_workflow_tab = "latest_vehicle_odometer"
    page_workflow_tab_keys = (
        "latest_vehicle_odometer",
        "vehicle_need_repair",
    )


class EtmsMrRequestPage(EtmsMaintenanceWorkflowPage):
    page_key = "mr_request"
    page_hash = "maintenance/maintenance-request"
    title = "M&R Request"
    sidebar_menu_labels = ("M&R Request",)
    default_workflow_tab = "not_send_request"
    page_workflow_tab_keys = (
        "not_send_request",
        "waiting_fleet_manager_approval",
        "waiting_director_approval",
        "accepted",
        "rejected",
        "revoked",
    )


class EtmsMaintenanceSettlementPage(EtmsMaintenanceWorkflowPage):
    page_key = "maintenance_settlement"
    page_hash = "maintenance/maintenance-vehicle"
    title = "Maintenance Settlement"
    sidebar_menu_labels = ("Maintenance Settlement",)
    default_workflow_tab = "not_send_request"
    page_workflow_tab_keys = (
        "not_send_request",
        "waiting_fleet_manager_approval",
        "waiting_director_approval",
        "accepted",
        "rejected",
    )


class EtmsMrPaymentRequestPage(EtmsMaintenanceWorkflowPage):
    page_key = "mr_payment_request"
    page_hash = "maintenance/main-payment-request"
    title = "M&R Payment Request"
    sidebar_menu_labels = ("M&R Payment Request",)
    default_workflow_tab = "payment"
    page_workflow_tab_keys = (
        "payment",
        "rejected_request",
    )


class EtmsVehicleMrPlanPage(EtmsMaintenanceWorkflowPage):
    page_key = "vehicle_mr_plan"
    page_hash = "maintenance/maintenance-vehicle-mr-plan"
    title = "Vehicle M&R Plan"
    sidebar_menu_labels = ("Vehicle M&R Plan",)
    default_workflow_tab = "month_plan"
    page_workflow_tab_keys = (
        "month_plan",
        "annual_plan",
    )


class EtmsMrTypePage(EtmsMaintenanceWorkflowPage):
    page_key = "mr_type"
    page_hash = "maintenance/maintenance-and-repair-type"
    title = "M&R Type"
    sidebar_menu_labels = ("M&R Type",)
    default_workflow_tab = "maintenance_type"
    page_workflow_tab_keys = (
        "maintenance_type",
        "repair_type",
    )
