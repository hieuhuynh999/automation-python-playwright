from __future__ import annotations

from automation.pages.etms.etms_catalogue_menu_page import (
    etms_in_page_tab_selectors,
    etms_sidebar_menu_selectors,
    is_etms_in_page_tab_active,
)
from automation.pages.etms.etms_customer_service_pages import EtmsCustomerServiceWorkflowPage
from automation.pages.etms.etms_pricing_workflow_list_page import (
    PRICING_WORKFLOW_TAB_CONFIGS,
    PricingWorkflowTabConfig,
)


class EtmsSuiteWorkflowPage(EtmsCustomerServiceWorkflowPage):
    """Workflow list page under a named sidebar suite (Accounting, System, Management, …)."""

    menu_parent_label: str = ""
    list_column_headers: tuple[str, ...] = ()

    def _menu_selectors(self) -> list[str]:
        labels = self.sidebar_menu_labels or (self.title,)
        return etms_sidebar_menu_selectors(
            self.menu_parent_label,
            labels,
            self.page_hash,
        )

    def _tab_config(self, tab_key: str) -> PricingWorkflowTabConfig:
        extra = self._suite_tab_configs()
        if tab_key in extra:
            return extra[tab_key]
        return super()._tab_config(tab_key)

    def _suite_tab_configs(self) -> dict[str, PricingWorkflowTabConfig]:
        """Override in subclasses to register suite-specific workflow tabs."""
        return {}


class EtmsInPageTabMixin:
    """Mixin — in-page nav tabs (not ul.filter-tab)."""

    def _scroll_filter_tab_bar(self) -> None:
        return

    def _filter_tab_selectors(self, tab_label: str) -> list[str]:
        return etms_in_page_tab_selectors(tab_label)

    def _is_filter_tab_active(self, tab_label: str) -> bool:
        return is_etms_in_page_tab_active(self, tab_label)


class EtmsInPageTabWorkflowPage(EtmsInPageTabMixin, EtmsSuiteWorkflowPage):
    """Suite workflow page with in-page tab navigation."""


def merge_workflow_tab_configs(
    *extra: dict[str, PricingWorkflowTabConfig],
) -> dict[str, PricingWorkflowTabConfig]:
    """Build a tab-config dict from PRICING_WORKFLOW_TAB_CONFIGS + suite-specific entries."""
    merged = dict(PRICING_WORKFLOW_TAB_CONFIGS)
    for block in extra:
        merged.update(block)
    return merged
