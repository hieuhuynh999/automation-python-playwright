from __future__ import annotations

from automation.pages.etms.etms_pricing_workflow_list_page import PricingWorkflowTabConfig
from automation.pages.etms.etms_suite_workflow_page import (
    EtmsInPageTabMixin,
    EtmsSuiteWorkflowPage,
)

ACCOUNTING_EXTRA_TAB_CONFIGS: dict[str, PricingWorkflowTabConfig] = {
    "cost_accrual": PricingWorkflowTabConfig("cost_accrual", "Cost Accural"),
    "cost_kpi_reconciliation": PricingWorkflowTabConfig(
        "cost_kpi_reconciliation",
        "Cost KPI Reconciliation",
    ),
    "km_reconciliation": PricingWorkflowTabConfig("km_reconciliation", "KM Reconciliation"),
    "rejected_surcharge": PricingWorkflowTabConfig(
        "rejected_surcharge",
        "Rejected Surcharge",
    ),
    "revenue_accrual": PricingWorkflowTabConfig("revenue_accrual", "Revenue Accural"),
    "revenue_kpi_reconciliation": PricingWorkflowTabConfig(
        "revenue_kpi_reconciliation",
        "Revenue KPI Reconciliation",
    ),
}


class EtmsAccountingWorkflowPage(EtmsSuiteWorkflowPage):
    """Accounting workflow / list pages — filter or in-page tabs + generic grid."""

    performance_menu_suite: str = "accounting"
    menu_parent_label: str = "Accounting"
    list_column_headers: tuple[str, ...] = ()

    def _suite_tab_configs(self) -> dict[str, PricingWorkflowTabConfig]:
        return ACCOUNTING_EXTRA_TAB_CONFIGS


class EtmsAccountingInPageTabPage(EtmsInPageTabMixin, EtmsAccountingWorkflowPage):
    """Accounting screens whose tabs are in-page nav links (not ul.filter-tab)."""


class EtmsAccrualOfCostsPage(EtmsAccountingInPageTabPage):
    page_key = "accrual_of_costs"
    page_hash = "accounting/cost-accrual"
    title = "Accrual Of Costs"
    sidebar_menu_labels = ("Accrual Of Costs",)
    default_workflow_tab = "cost_accrual"
    page_workflow_tab_keys = (
        "cost_accrual",
        "cost_kpi_reconciliation",
        "km_reconciliation",
    )


class EtmsAccountingPaymentRequestPage(EtmsAccountingWorkflowPage):
    page_key = "accounting_payment_request"
    page_hash = "accounting/payment-request"
    title = "Payment Request"
    sidebar_menu_labels = ("Payment Request",)
    default_workflow_tab = "payment"
    page_workflow_tab_keys = (
        "payment",
        "rejected_surcharge",
    )


class EtmsRevenueAccrualPage(EtmsAccountingInPageTabPage):
    page_key = "revenue_accrual"
    page_hash = "accounting/revenue"
    title = "Revenue Accural"
    sidebar_menu_labels = ("Revenue Accural",)
    default_workflow_tab = "revenue_accrual"
    page_workflow_tab_keys = (
        "revenue_accrual",
        "revenue_kpi_reconciliation",
    )
