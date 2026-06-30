from __future__ import annotations

from automation.pages.etms.etms_customer_service_pages import EtmsCustomerServiceWorkflowPage
from automation.pages.etms.etms_pricing_workflow_list_page import (
    PRICING_WORKFLOW_TAB_CONFIGS,
    PricingWorkflowTabConfig,
)

MATERIAL_WORKFLOW_TAB_CONFIGS: dict[str, PricingWorkflowTabConfig] = {
    **PRICING_WORKFLOW_TAB_CONFIGS,
    "not_sent_request": PricingWorkflowTabConfig("not_sent_request", "Not Sent Request"),
}


class EtmsMaterialWorkflowPage(EtmsCustomerServiceWorkflowPage):
    """Material Management workflow list pages — filter tabs + generic grid."""

    performance_menu_suite: str = "material_management"
    list_column_headers: tuple[str, ...] = ()

    def _tab_config(self, tab_key: str) -> PricingWorkflowTabConfig:
        if tab_key in MATERIAL_WORKFLOW_TAB_CONFIGS:
            return MATERIAL_WORKFLOW_TAB_CONFIGS[tab_key]
        return super()._tab_config(tab_key)


class EtmsImportMaterialPage(EtmsMaterialWorkflowPage):
    page_key = "import_material"
    page_hash = "material/import-material-management"
    title = "Import Material"
    sidebar_menu_labels = ("Import Material",)
    default_workflow_tab = "not_sent_request"
    page_workflow_tab_keys = (
        "not_sent_request",
        "pending",
        "accepted",
        "rejected",
    )


class EtmsExportMaterialPage(EtmsMaterialWorkflowPage):
    page_key = "export_material"
    page_hash = "material/export-material-management"
    title = "Export Material"
    sidebar_menu_labels = ("Export Material",)
    default_workflow_tab = "not_sent_request"
    page_workflow_tab_keys = (
        "not_sent_request",
        "pending",
        "accepted",
        "rejected",
    )
