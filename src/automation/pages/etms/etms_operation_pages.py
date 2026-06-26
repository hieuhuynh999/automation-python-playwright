from __future__ import annotations

from automation.pages.etms.etms_customer_service_pages import EtmsCustomerServiceWorkflowPage


class EtmsUnlockTransportRequestPage(EtmsCustomerServiceWorkflowPage):
    """Unlock Transport Request — default Updating tab."""

    page_key = "unlock_transport_request"
    page_hash = "operation/common/unlock-transport"
    title = "Unlock Transport Request"
    sidebar_menu_labels = ("Unlock Transport Request",)
    performance_menu_suite = "operation_common"
    default_workflow_tab = "updating"
    page_workflow_tab_keys = (
        "updating",
        "pending",
        "accepted",
        "rejected",
    )


class EtmsConfirmEpodPage(EtmsCustomerServiceWorkflowPage):
    """Confirm ePOD — default New tab."""

    page_key = "confirm_epod"
    page_hash = "operation/common/confirm-pod"
    title = "Confirm ePOD"
    sidebar_menu_labels = ("Confirm ePOD",)
    performance_menu_suite = "operation_common"
    default_workflow_tab = "new"
    page_workflow_tab_keys = (
        "new",
        "accepted",
        "rejected",
        "revoked",
    )
