from __future__ import annotations

from automation.pages.etms.etms_pricing_workflow_list_page import PricingWorkflowTabConfig
from automation.pages.etms.etms_suite_workflow_page import EtmsSuiteWorkflowPage

MANAGEMENT_EXTRA_TAB_CONFIGS: dict[str, PricingWorkflowTabConfig] = {
    "reversed": PricingWorkflowTabConfig("reversed", "Reversed"),
}


class EtmsManagementWorkflowPage(EtmsSuiteWorkflowPage):
    """Management workflow list pages — filter tabs + generic grid."""

    performance_menu_suite: str = "management"
    menu_parent_label: str = "Management"
    list_column_headers: tuple[str, ...] = ()

    def _suite_tab_configs(self) -> dict[str, PricingWorkflowTabConfig]:
        return MANAGEMENT_EXTRA_TAB_CONFIGS


class EtmsAuthorizationPage(EtmsManagementWorkflowPage):
    page_key = "authorization"
    page_hash = "management/authorization"
    title = "Authorization"
    sidebar_menu_labels = ("Authorization",)
    default_workflow_tab = "updating"
    page_workflow_tab_keys = (
        "updating",
        "pending",
        "accepted",
        "rejected",
        "expired",
        "reversed",
    )
