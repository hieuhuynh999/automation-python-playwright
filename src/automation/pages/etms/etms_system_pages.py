from __future__ import annotations

from automation.pages.etms.etms_performance_control_page import EtmsPerformanceControlPage
from automation.pages.etms.etms_pricing_workflow_list_page import PricingWorkflowTabConfig
from automation.pages.etms.etms_suite_workflow_page import (
    EtmsInPageTabMixin,
    EtmsSuiteWorkflowPage,
)

SYSTEM_EXTRA_TAB_CONFIGS: dict[str, PricingWorkflowTabConfig] = {
    "role": PricingWorkflowTabConfig("role", "Role"),
    "permission_of_role": PricingWorkflowTabConfig("permission_of_role", "Permission of Role"),
    "etms_log": PricingWorkflowTabConfig("etms_log", "eTMS Log"),
    "mobile_log": PricingWorkflowTabConfig("mobile_log", "Mobile Log"),
    "bravo_log": PricingWorkflowTabConfig("bravo_log", "Bravo Log"),
    "petrolimex_log": PricingWorkflowTabConfig("petrolimex_log", "Petrolimex Log"),
    "approval_workflow": PricingWorkflowTabConfig("approval_workflow", "Approval Workflow"),
    "approval_object": PricingWorkflowTabConfig("approval_object", "Approval Object"),
    "approval_position": PricingWorkflowTabConfig("approval_position", "Approval Position"),
}

GUIDE_STYLE_CONTROL_LABELS: dict[str, str] = {
    "add_new": "+ Add new",
    "button_style": "Button style",
}


class EtmsSystemWorkflowPage(EtmsSuiteWorkflowPage):
    """System workflow list pages — filter or in-page tabs + generic grid."""

    performance_menu_suite: str = "system"
    menu_parent_label: str = "System"
    list_column_headers: tuple[str, ...] = ()

    def _suite_tab_configs(self) -> dict[str, PricingWorkflowTabConfig]:
        return SYSTEM_EXTRA_TAB_CONFIGS


class EtmsSystemInPageTabPage(EtmsInPageTabMixin, EtmsSystemWorkflowPage):
    """System screens whose tabs are in-page nav links (not ul.filter-tab)."""


class EtmsSystemRolePage(EtmsSystemWorkflowPage):
    """System > Role — tabs Role (default) and Permission of Role."""

    page_key = "role"
    page_hash = "system/role"
    title = "Role"
    sidebar_menu_labels = ("Role",)
    default_workflow_tab = "role"
    page_workflow_tab_keys = ("role", "permission_of_role")


class EtmsUserLogPage(EtmsSystemWorkflowPage):
    page_key = "user_log"
    page_hash = "system/user-log"
    title = "User Log"
    sidebar_menu_labels = ("User Log",)
    default_workflow_tab = "etms_log"
    page_workflow_tab_keys = (
        "etms_log",
        "mobile_log",
        "bravo_log",
        "petrolimex_log",
    )


class EtmsApprovalWorkflowConfigurationPage(EtmsSystemInPageTabPage):
    page_key = "approval_workflow_configuration"
    page_hash = "system/approval-workflow-configuration"
    title = "Approval Workflow Configuration"
    sidebar_menu_labels = ("Approval Workflow Configuration",)
    default_workflow_tab = "approval_workflow"
    page_workflow_tab_keys = (
        "approval_workflow",
        "approval_object",
        "approval_position",
    )


class EtmsGuideStylePage(EtmsPerformanceControlPage):
    """System > Guide Style — verify style-guide controls visible and enabled."""

    page_key = "guide_style"
    page_hash = "system/guide-style"
    title = "Guide Style"
    sidebar_menu_labels = ("Guide Style",)
    menu_parent_label: str = "System"
    performance_menu_suite: str = "system"

    def _control_label(self, control_key: str | None) -> str:
        key = control_key or "add_new"
        if key not in GUIDE_STYLE_CONTROL_LABELS:
            known = ", ".join(sorted(GUIDE_STYLE_CONTROL_LABELS))
            raise ValueError(f"Unknown Guide Style control '{key}'. Known: {known}")
        return GUIDE_STYLE_CONTROL_LABELS[key]

    def _control_selectors(self, control_key: str | None) -> list[str]:
        key = control_key or "add_new"
        label = self._control_label(key)
        if key == "add_new":
            return [
                (
                    "xpath=//div[contains(@class,'wms-page-body')]"
                    f"//button[contains(normalize-space(),'{label}') "
                    "and not(@disabled) and not(contains(@class,'disabled'))]"
                ),
                (
                    "xpath=//div[contains(@class,'page-content')]"
                    f"//button[contains(normalize-space(),'{label}') "
                    "and not(@disabled) and not(contains(@class,'disabled'))]"
                ),
            ]
        return [
            (
                "xpath=//div[contains(@class,'wms-page-body')]"
                f"//a[contains(@class,'btn')][normalize-space()='{label}' "
                "and not(contains(@class,'disabled'))]"
            ),
            (
                "xpath=//div[contains(@class,'page-content')]"
                f"//a[contains(@class,'btn')][normalize-space()='{label}' "
                "and not(contains(@class,'disabled'))]"
            ),
        ]
