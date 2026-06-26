from __future__ import annotations

from automation.pages.etms.etms_catalogue_menu_page import (
    _catalogue_submenu_link_by_label,
    _sidebar_child_link,
    _sidebar_link_by_href,
)
from automation.pages.etms.etms_quotation_form_page import EtmsQuotationFormPage

_OPERATION_MENU_PARENT = "Operation"


class EtmsOperationLclFtlActionPage(EtmsQuotationFormPage):
    """Operation > LCL/FTL action pages — scoped sidebar links under Operation."""

    def _menu_selectors(self) -> list[str]:
        labels = self.sidebar_menu_labels
        selectors: list[str] = []
        for label in labels:
            selectors.extend(
                [
                    _sidebar_child_link(_OPERATION_MENU_PARENT, label),
                    _catalogue_submenu_link_by_label(label),
                    (
                        "xpath=//a[contains(@class,'nav-link')]"
                        f"[.//span[normalize-space()='{label}']]"
                    ),
                ]
            )
        selectors.append(_sidebar_link_by_href(self.page_hash))
        return list(dict.fromkeys(selectors))


class EtmsLclFtlCheckOutPage(EtmsOperationLclFtlActionPage):
    """Operation > LCL/FTL > 7.Check Out — ready when Check Out control is enabled."""

    page_key = "lcl_ftl_check_out"
    page_hash = "operation/lcl/check-out"
    title = "7.Check Out"
    sidebar_menu_labels = ("7.Check Out",)
    ready_control_label = "Check Out"


class EtmsLclFtlCheckInPage(EtmsOperationLclFtlActionPage):
    """Operation > LCL/FTL > 9.Check In — ready when Clear Input control is enabled."""

    page_key = "lcl_ftl_check_in"
    page_hash = "operation/lcl/check-in"
    title = "9.Check In"
    sidebar_menu_labels = ("9.Check In",)
    ready_control_label = "Clear Input"


class EtmsLclFtlUnbagPage(EtmsOperationLclFtlActionPage):
    """Operation > LCL/FTL > 11.Unbag — ready when Check item control is enabled."""

    page_key = "lcl_ftl_unbag"
    page_hash = "operation/lcl/unbagging"
    title = "11.Unbag"
    sidebar_menu_labels = ("11.Unbag",)
    ready_control_label = "Check item"
