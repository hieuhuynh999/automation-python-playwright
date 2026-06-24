from __future__ import annotations

import re
import time
from typing import Any

from automation.config import settings
from automation.logging import log_method, logger
from automation.pages.base_page import BasePage
from automation.pages.common.list_grid_component import ListGridComponent
from automation.pages.common.ng_select_component import NgSelectComponent


class EtmsCostOfRoutePage(BasePage):
    """Cost Of Route — menu search, Choose Route popup, surcharge generate, save."""

    menu_search_input_selectors = [
        "input[placeholder*='Search for']",
        "input[placeholder*='Search']",
        ".ftl-main-header input[type='text']",
        "input.form-control[placeholder*='Search']",
    ]

    menu_search_icon_selectors = [
        "button:has(i.fa-search)",
        "xpath=//button[.//i[contains(@class,'fa-search')]]",
        ".fa-search",
        "xpath=//*[contains(@class,'search')]//i[contains(@class,'search')]",
    ]

    menu_result_selectors = [
        "xpath=//*[contains(@class,'dropdown-menu')]//*[normalize-space()='Cost Of Route']",
        "xpath=//*[contains(@class,'search-result')]//*[normalize-space()='Cost Of Route']",
        "a:has-text('Cost Of Route')",
        "text=Cost Of Route",
    ]

    list_page_hash = "cost-of-route"

    list_title_selectors = [
        "xpath=//h3[normalize-space()='Cost Of Route']",
        "h3:has-text('Cost Of Route')",
        "xpath=//*[contains(@class,'page-title') and contains(normalize-space(),'Cost Of Route')]",
    ]

    list_table_selectors = [
        (
            "xpath=//th[contains(@id,'PriceRouteCost') "
            "and span[normalize-space()='Code']]"
        ),
        "xpath=//th[contains(normalize-space(),'Route')]",
        "xpath=//table[.//th[contains(@id,'PriceRouteCost')]]//th",
    ]

    add_new_button_selectors = [
        "button[title='Add new Cost of Route']",
        "xpath=//button[@title='Add new Cost of Route']",
        "[title='Add new Cost of Route']",
        "button:has-text('Add New')",
        "xpath=//button[normalize-space()='Add New']",
        "button.btn-ftl-primary:has-text('Add New')",
    ]

    choose_route_popup_selectors = [
        "xpath=//div[contains(@class,'modal') and contains(@class,'show') and .//*[contains(normalize-space(),'Choose Route')]]",
        ".modal.show:has-text('Choose Route')",
        "xpath=//*[contains(@class,'modal-title') and contains(normalize-space(),'Choose Route')]/ancestor::div[contains(@class,'modal')]",
    ]

    choose_route_code_filter_selectors = [
        (
            "xpath=//div[contains(@class,'modal-body')]"
            "//tr[contains(@class,'filter-row')]"
            "/td[count("
            "//div[contains(@class,'modal-body')]"
            "//th[normalize-space()='Code']/preceding-sibling::th"
            ")+1]//input"
        ),
    ]

    list_route_code_filter_selectors = [
        (
            "xpath=//th[contains(@id,'PriceRouteCost') and contains(@id,'cRouteCode')]"
            "/ancestor::table[1]"
            "//tr[contains(@class,'filter-row')]"
            "/td[count("
            "ancestor::table[1]"
            "//th[contains(@id,'PriceRouteCost') and contains(@id,'cRouteCode')]"
            "/preceding-sibling::th)+1]//input"
        ),
        (
            "xpath=//*[contains(@class,'page-title') and contains(normalize-space(),'Cost Of Route')]"
            "/ancestor::div[contains(@class,'m-portlet') or contains(@class,'portlet')][1]"
            "//div[contains(@class,'m-portlet__body') or contains(@class,'portlet__body')]"
            "//tr[contains(@class,'filter-row')]"
            "/td[count("
            "//*[contains(@class,'page-title') and contains(normalize-space(),'Cost Of Route')]"
            "/ancestor::div[contains(@class,'m-portlet') or contains(@class,'portlet')][1]"
            "//div[contains(@class,'m-portlet__body') or contains(@class,'portlet__body')]"
            "//th[normalize-space()='Route Code']/preceding-sibling::th"
            ")+1]//input"
        ),
        (
            "xpath=//div[contains(@class,'m-portlet__body')]"
            "//tr[contains(@class,'filter-row')]"
            "/td[count("
            "//div[contains(@class,'m-portlet__body')]"
            "//th[normalize-space()='Route Code']/preceding-sibling::th"
            ")+1]//input"
        ),
        (
            "xpath=//tr[contains(@class,'filter-row')]"
            "/td[count(//th[normalize-space()='Route Code']/preceding-sibling::th)+1]//input"
        ),
    ]

    choose_button_selectors = [
        "xpath=//div[contains(@class,'modal') and contains(@class,'show') and .//*[contains(normalize-space(),'Choose Route')]]//button[normalize-space()='Choose']",
        "xpath=//div[contains(@class,'modal') and contains(@class,'show')]//button[normalize-space()='Choose']",
        "button:has-text('Choose')",
    ]

    add_form_title_selectors = [
        "xpath=//*[contains(normalize-space(),'Add New Cost Of Route')]",
        "xpath=//*[contains(normalize-space(),'Cost Of Route')]",
        "h4:has-text('Add New Cost Of Route')",
        "h3:has-text('Add New Cost Of Route')",
    ]

    modify_page_hash = "cost-of-route/modify"
    detail_page_hash_markers = ("/detail", "/view")

    surcharge_section_selectors = [
        "xpath=//*[contains(normalize-space(),'Surcharge List')]",
        "text=Surcharge List",
    ]

    generate_button_selectors = [
        "xpath=//*[contains(normalize-space(),'Surcharge List')]/ancestor::div[contains(@class,'portlet') or contains(@class,'card') or contains(@class,'panel')][1]//button[normalize-space()='Generate']",
        "xpath=//button[normalize-space()='Generate']",
        "button:has-text('Generate')",
    ]

    save_button_selectors = [
        "xpath=//button[normalize-space()='Save']",
        "button.btn-ftl-primary:has-text('Save')",
        "button:has-text('Save')",
    ]

    _surcharge_section_xpath = (
        "//*[contains(normalize-space(),'Surcharge List')]"
        "/ancestor::div[contains(@class,'portlet') or contains(@class,'card') "
        "or contains(@class,'panel') or contains(@class,'m-portlet')][1]"
    )

    total_price_label_selectors = [
        f"xpath={_surcharge_section_xpath}//*[contains(normalize-space(),'Total (Price)')]",
        "xpath=//*[contains(@class,'datatable-header-cell-label') and contains(.,'Total (Price)')]",
        "xpath=//datatable-header-cell[contains(.,'Total (Price)')]",
        "xpath=//th[contains(.,'Total (Price)')]",
        "xpath=//*[contains(normalize-space(),'Total (Price)')]",
        "text=Total (Price)",
    ]

    delete_action_selectors = [
        "a.btn.btn-ftl-icon.text-danger[title='Delete']",
        "a.btn-ftl-icon.text-danger[title='Delete']",
        "a[id*='btnButtonRowDelete']",
        "a[title='Delete'].btn-ftl-icon:has(i.icon-trash-2)",
        "xpath=//a[@title='Delete' and contains(@class,'btn-ftl-icon') and contains(@class,'text-danger')]",
        "xpath=//a[contains(@id,'btnButtonRowDelete')]",
        "[title='Delete']",
    ]

    delete_confirm_message = "Do you want delete?"

    delete_confirm_popup_selectors = [
        f"xpath=//*[contains(normalize-space(),'{delete_confirm_message}')]",
        "xpath=//*[contains(.,'Do you want delete')]",
        ".swal2-popup:has-text('Do you want delete')",
    ]

    delete_confirm_ok_selectors = [
        "xpath=//span[normalize-space()='OK']",
        (
            "xpath=//*[contains(.,'Do you want delete')]"
            "/ancestor::div[contains(@class,'modal') or contains(@class,'swal2-popup')][1]"
            "//span[normalize-space()='OK']"
        ),
        ".swal2-popup .swal2-confirm",
        "button.swal2-confirm",
    ]

    accepted_tab_selectors = [
        "xpath=//ul[contains(@class,'nav-tabs')]//a[normalize-space()='Accepted']",
        "xpath=//a[contains(@class,'nav-link') and normalize-space()='Accepted']",
        "xpath=//*[contains(@class,'nav-link') and contains(normalize-space(),'Accepted')]",
    ]

    copy_action_selectors = [
        "a.btn-ftl-icon[title='Copy']",
        "a[id*='btnButtonRowCopy']",
        "a[title='Copy'].btn-ftl-icon",
        "a.btn-ftl-icon:has(i.icon-copy)",
        "a.btn-ftl-icon:has(i.fa-copy)",
        "xpath=//a[@title='Copy' and contains(@class,'btn-ftl-icon')]",
        "xpath=//a[contains(@id,'btnButtonRowCopy')]",
        "xpath=//a[contains(@title,'Copy') and contains(@class,'btn-ftl-icon')]",
        "xpath=//a[contains(@class,'btn-ftl-icon') and .//i[contains(@class,'copy')]]",
        "[title*='Copy']",
    ]

    copy_confirm_message = "Do you want COPY this 'Cost Of Route'?"

    copy_confirm_popup_selectors = [
        f"xpath=//*[contains(normalize-space(),\"{copy_confirm_message}\")]",
        "xpath=//*[contains(.,\"Do you want COPY this\")]",
        ".swal2-popup:has-text('Do you want COPY')",
    ]

    copy_confirm_ok_selectors = [
        "xpath=//span[normalize-space()='OK']",
        (
            "xpath=//*[contains(.,'Do you want COPY')]"
            "/ancestor::div[contains(@class,'modal') or contains(@class,'swal2-popup')][1]"
            "//span[normalize-space()='OK']"
        ),
        ".swal2-popup .swal2-confirm",
        "button.swal2-confirm",
    ]

    copy_confirm_cancel_selectors = [
        "xpath=//span[normalize-space()='Cancel']",
        (
            "xpath=//*[contains(.,'Do you want COPY')]"
            "/ancestor::div[contains(@class,'modal') or contains(@class,'swal2-popup')][1]"
            "//span[normalize-space()='Cancel']"
        ),
        ".swal2-popup .swal2-cancel",
        "button.swal2-cancel",
        "button:has-text('Cancel')",
    ]

    send_request_action_selectors = [
        (
            "xpath=//div[contains(@class,'dropdown-menu') and contains(@class,'show')]"
            "//a[@title='Send Request']"
        ),
        (
            "xpath=//ul[contains(@class,'dropdown-menu') and contains(@class,'show')]"
            "//a[@title='Send Request']"
        ),
        "a.btn-ftl-icon[title='Send Request']",
        "a[id*='btnButtonRowSendRequest']",
        "a[title='Send Request'].btn-ftl-icon",
        "a.btn-ftl-icon:has(i.icon-send)",
        "xpath=//a[@title='Send Request' and contains(@class,'btn-ftl-icon')]",
        "xpath=//a[contains(@id,'btnButtonRowSendRequest')]",
        "xpath=//a[contains(@class,'btn-ftl-icon') and .//i[contains(@class,'send')]]",
        "[title='Send Request']",
    ]

    reject_action_selectors = [
        "a.btn-ftl-icon[title='Reject']",
        "a[id*='btnButtonRowReject']",
        "a[title='Reject'].btn-ftl-icon",
        "xpath=//a[@title='Reject' and contains(@class,'btn-ftl-icon')]",
        "xpath=//a[contains(@id,'btnButtonRowReject')]",
        "[title='Reject']",
    ]

    send_request_confirm_selectors = [
        (
            "xpath=//*[contains(normalize-space(),'Request Approval')]"
            "/ancestor::div[contains(@class,'modal') or contains(@class,'swal2-popup')][1]"
            "//button[normalize-space()='Send Request' or .//span[normalize-space()='Send Request']]"
        ),
        "xpath=//button[normalize-space()='Send Request']",
        "xpath=//span[normalize-space()='Send Request']",
        ".swal2-popup button.swal2-confirm",
        "button.swal2-confirm",
    ]

    send_request_cancel_selectors = [
        (
            "xpath=//*[contains(normalize-space(),'Request Approval')]"
            "/ancestor::div[contains(@class,'modal') or contains(@class,'swal2-popup')][1]"
            "//button[normalize-space()='Cancel' or .//span[normalize-space()='Cancel']]"
        ),
        (
            "xpath=//*[contains(normalize-space(),'Request Approval')]"
            "/ancestor::div[contains(@class,'modal') or contains(@class,'swal2-popup')][1]"
            "//span[normalize-space()='Cancel']"
        ),
        ".swal2-popup:has-text('Request Approval') .swal2-cancel",
        ".modal.show:has-text('Request Approval') button:has-text('Cancel')",
    ]

    send_request_popup_selectors = [
        "xpath=//*[contains(normalize-space(),'Request Approval')]",
        "xpath=//*[contains(normalize-space(),'Send Request')]",
        ".swal2-popup:has-text('Request Approval')",
        ".swal2-popup:has-text('Send Request')",
        ".modal.show:has-text('Request Approval')",
        ".modal.show:has-text('Send Request')",
    ]

    reject_confirm_message = "Do you want REJECT this 'Cost Of Route'?"

    reject_reason_input_selectors = [
        "#txtConfirmInput",
        "xpath=//*[@id='txtConfirmInput']",
        "textarea.swal2-textarea",
        ".swal2-textarea",
        "xpath=//textarea[contains(@class,'swal2')]",
        "xpath=//div[contains(@class,'swal2-popup')]//textarea",
    ]

    switch_to_updating_button_selectors = [
        "xpath=//*[@title='Switch To Updating']",
    ]

    list_filtered_row_checkbox_selectors = [
        (
            "xpath=//tr[@class='point-hover']"
            "//input[@type='checkbox']/following-sibling::span"
        ),
        (
            "xpath=//tr[contains(@class,'point-hover')]"
            "//input[@type='checkbox']/following-sibling::span"
        ),
    ]

    switch_to_updating_confirm_message = (
        "Do you want switch to edit mode this 'Cost Of Route'?"
    )

    _cost_of_route_code_th_xpath = (
        "//th[contains(@id,'PriceRouteCost') and span[normalize-space()='Code']]"
    )

    list_cor_code_filter_selectors = [
        (
            "xpath=//th[contains(@id,'PriceRouteCost') and span[normalize-space()='Code']]"
            "/ancestor::table[1]"
            "//tr[contains(@class,'filter-row')]"
            "/td[count("
            "ancestor::table[1]"
            "//th[contains(@id,'PriceRouteCost') and span[normalize-space()='Code']]"
            "/preceding-sibling::th)+1]//input"
        ),
    ]

    list_cor_code_header_selectors = [
        f"xpath={_cost_of_route_code_th_xpath}",
        f"xpath={_cost_of_route_code_th_xpath}//span[normalize-space()='Code']",
    ]

    _cost_of_route_list_table_xpath = (
        f"//table[.//th[contains(@id,'PriceRouteCost') "
        f"and span[normalize-space()='Code']]]"
    )

    _cost_of_route_route_code_th_xpath = (
        "//th[contains(@id,'PriceRouteCost') and contains(@id,'cRouteCode')]"
    )

    list_route_code_header_selectors = [
        f"xpath={_cost_of_route_route_code_th_xpath}",
        (
            f"xpath={_cost_of_route_route_code_th_xpath}"
            "//span[contains(normalize-space(),'Route') "
            "and contains(normalize-space(),'Code')]"
        ),
        "xpath=//th[normalize-space()='Route Code']",
        "xpath=//th[contains(normalize-space(),'Route') and contains(normalize-space(),'Code')]",
    ]

    _swal_ok_selectors = [
        "xpath=//span[normalize-space()='OK']",
        ".swal2-popup .swal2-confirm",
        "button.swal2-confirm",
    ]

    _swal_cancel_selectors = [
        "xpath=//span[normalize-space()='Cancel']",
        ".swal2-popup .swal2-cancel",
        "button.swal2-cancel",
        "button:has-text('Cancel')",
    ]

    @property
    def list_grid(self) -> ListGridComponent:
        if not hasattr(self, "_list_grid"):
            self._list_grid = ListGridComponent(self, "Cost Of Route list grid")
        return self._list_grid

    def _choose_route_modal_body(self) -> str:
        return (
            "//div[contains(@class,'modal')]"
            "[.//*[contains(normalize-space(),'Choose Route')]]"
            "//div[contains(@class,'modal-body')]"
        )

    def _field_container(self, label: str):
        selectors = [
            (
                f"xpath=//label[contains(normalize-space(),'{label}')]"
                "/ancestor::div[contains(@class,'form-group') or contains(@class,'col-')][1]"
            ),
            (
                f"xpath=//*[contains(normalize-space(),'{label}')]"
                "/ancestor::div[contains(@class,'form-group') or contains(@class,'col-')][1]"
            ),
        ]
        return self.wait_for_visible(selectors, f"{label} field container")

    @log_method("Search menu and open Cost Of Route page")
    def open_via_menu_search(self, menu_text: str = "Cost Of Route") -> "EtmsCostOfRoutePage":
        search = self.wait_for_visible(
            self.menu_search_input_selectors,
            "Menu search textbox",
        )
        search.click()
        search.fill(menu_text)
        self.wait_for_page_stable()

        icon = self.find_visible(self.menu_search_icon_selectors)
        if icon is not None:
            icon.click()
            self.wait_for_page_stable()

        result_selectors = [
            f"xpath=//*[contains(@class,'dropdown-menu')]//*[normalize-space()='{menu_text}']",
            f"xpath=//*[contains(@class,'search-result')]//*[normalize-space()='{menu_text}']",
            f"a:has-text('{menu_text}')",
            f"text={menu_text}",
        ]
        self.wait_for_visible(result_selectors, f"Menu search result: {menu_text}").click(
            force=True
        )
        self.page.wait_for_url(
            lambda url: self.list_page_hash in url.lower().replace("_", "-"),
            timeout=settings.page_load_timeout,
        )
        self.wait_for_page_stable()
        return self

    @log_method("Verify Cost Of Route list page is displayed")
    def is_list_page_displayed(self) -> bool:
        self.wait_for_visible(self.list_title_selectors, "Cost Of Route page title")
        self.list_grid.wait_until_ready(
            self.list_table_selectors,
            "Cost Of Route table",
        )
        return self.list_page_hash in self.current_url.lower().replace("_", "-")

    @log_method("Click Add New")
    def click_add_new(self) -> "EtmsCostOfRoutePage":
        self.click_when_ready(self.add_new_button_selectors, "Add New button")
        self.wait_for_page_stable()
        return self

    @log_method("Verify Choose Route popup is displayed")
    def is_choose_route_popup_displayed(self) -> bool:
        self.wait_for_visible(self.choose_route_popup_selectors, "Choose Route popup")
        return True

    @log_method("Filter route code in Choose Route popup")
    def search_route_in_choose_popup(self, route_code: str) -> "EtmsCostOfRoutePage":
        self._fill_route_code_filter(
            self.choose_route_code_filter_selectors,
            route_code,
            "Choose Route Code filter input",
        )
        return self

    choose_route_checkmark_selectors = [
        "xpath=//label[@class='form-label radio-container']//span[@class='checkmark']",
        "label.form-label.radio-container span.checkmark",
    ]

    def _route_row_checkmark_selectors(self, route_code: str) -> list[str]:
        modal_body = self._choose_route_modal_body()
        row_scopes = [
            f"{modal_body}//tr[contains(.,'{route_code}') and not(contains(@class,'filter-row'))]",
            f"{modal_body}//datatable-body-row[contains(.,'{route_code}')]",
            f"{modal_body}//datatable-row-wrapper[contains(.,'{route_code}')]",
        ]
        checkmark = "//label[@class='form-label radio-container']//span[@class='checkmark']"
        scoped = [f"xpath={scope}{checkmark}" for scope in row_scopes]
        return scoped + [
            f"xpath={modal_body}{checkmark}",
            *self.choose_route_checkmark_selectors,
        ]

    @log_method("Tick route row checkmark in Choose Route popup")
    def tick_route_row(self, route_code: str) -> "EtmsCostOfRoutePage":
        checkmark = self.wait_for_visible(
            self._route_row_checkmark_selectors(route_code),
            f"Route checkmark: {route_code}",
        )
        checkmark.click(force=True)
        self.wait_for_page_stable()
        return self

    @log_method("Click Choose on Choose Route popup")
    def click_choose_route(self) -> "EtmsCostOfRoutePage":
        self.click_when_ready(self.choose_button_selectors, "Choose button")
        self.wait_for_page_stable()
        return self

    @log_method("Choose route in popup")
    def choose_route(self, route_code: str) -> "EtmsCostOfRoutePage":
        self.is_choose_route_popup_displayed()
        self.search_route_in_choose_popup(route_code)
        self.tick_route_row(route_code)
        return self.click_choose_route()

    @log_method("Verify Add New Cost Of Route form is displayed")
    def is_add_form_displayed(self) -> bool:
        if self.modify_page_hash in self.current_url.lower().replace("_", "-"):
            self.wait_for_page_stable()
            return True
        self.wait_for_visible(self.add_form_title_selectors, "Add New Cost Of Route form")
        return True

    def _dropdown_search_field_selectors(self, label: str) -> list[str]:
        return [
            (
                f"xpath=//label[contains(normalize-space(),'{label}')]"
                "/ancestor::div[contains(@class,'form-group') or contains(@class,'col-')][1]"
                "//input[contains(@class,'search-field')]"
            ),
            (
                f"xpath=//label[contains(normalize-space(),'{label}')]"
                "/ancestor::div[contains(@class,'form-group') or contains(@class,'col-')][1]"
                "//*[contains(@class,'search-field')]//input"
            ),
            ".ng-dropdown-panel input.search-field",
            ".ng-dropdown-panel .search-field input",
            ".ng-dropdown-panel input[type='text']",
        ]

    def _dropdown_option_selectors(self, value: str) -> list[str]:
        return [
            f".ng-dropdown-panel .ng-option:has-text('{value}')",
            f"xpath=//ng-dropdown-panel//div[contains(@class,'ng-option') and contains(normalize-space(),'{value}')]",
            f"xpath=//ng-dropdown-panel//*[contains(@class,'ng-option') and contains(.,'{value}')]",
        ]

    @log_method("Select searchable dropdown field by label")
    def select_dropdown_field(self, label: str, value: str) -> "EtmsCostOfRoutePage":
        container = self._field_container(label)
        container.scroll_into_view_if_needed()

        ng_select = container.locator("ng-select").first
        if ng_select.count() > 0:
            ng_select.locator(".ng-select-container").click(force=True)
            self.page.locator(".ng-dropdown-panel").wait_for(
                state="visible",
                timeout=settings.browser_timeout,
            )

            search = self.wait_for_visible(
                self._dropdown_search_field_selectors(label),
                f"{label} search field",
            )
            search.click()
            search.fill(value)

            deadline = time.monotonic() + settings.browser_timeout / 1000
            option = None
            while time.monotonic() < deadline:
                option = self.find_visible(self._dropdown_option_selectors(value))
                if option is not None:
                    break
                search.press("Enter")
                self.page.wait_for_timeout(settings.polling_interval)

            if option is None:
                option = self.wait_for_visible(
                    self._dropdown_option_selectors(value),
                    f"{label} option: {value}",
                )
            option.click(force=True)
            self.page.locator(".ng-dropdown-panel").wait_for(
                state="hidden",
                timeout=settings.browser_timeout,
            )
            self.wait_for_page_stable()
            return self

        combogrid_toggle = container.locator("input.dropdown-toggle").first
        if combogrid_toggle.count() > 0:
            combogrid_toggle.click(force=True)
            search = self.wait_for_visible(
                self._dropdown_search_field_selectors(label),
                f"{label} combogrid search field",
            )
            search.click()
            search.fill(value)
            row_selectors = [
                f"xpath=//*[contains(@class,'dropdown-menu')]//tr[contains(.,'{value}')]",
                f"xpath=//*[contains(@class,'combogrid')]//tr[contains(.,'{value}')]",
            ]
            self.wait_for_visible(row_selectors, f"{label} option: {value}").click(force=True)
            self.page.keyboard.press("Escape")
            self.wait_for_page_stable()
            return self

        select_component = NgSelectComponent(
            self,
            [
                (
                    f"xpath=//label[contains(normalize-space(),'{label}')]"
                    "/following::ng-select[1]"
                ),
            ],
            f"{label} dropdown",
        )
        select_component.select_option_by_text(value)
        return self

    @log_method("Fill Add New Cost Of Route mapping fields")
    def fill_route_mapping_fields(self, data: dict[str, Any]) -> "EtmsCostOfRoutePage":
        self.select_dropdown_field("Vehicle Type", data["vehicle_type"])
        self.select_dropdown_field("Container Type", data["container_type"])
        self.select_dropdown_field("Weight Range", data["weight_range"])
        return self

    def _total_price_value_selectors(self) -> list[str]:
        scoped = self._surcharge_section_xpath
        return [
            (
                f"xpath={scoped}//datatable-body-row"
                "//datatable-body-cell"
                f"[count({scoped}//datatable-header-cell[contains(.,'Total (Price)')]"
                "/preceding-sibling::datatable-header-cell)+1]"
                "[normalize-space()!='' and normalize-space()!='0' and normalize-space()!='0.00']"
            ),
            (
                f"xpath={scoped}//tr[not(contains(@class,'filter-row'))]"
                "/td[count("
                f"{scoped}//th[contains(.,'Total (Price)')]/preceding-sibling::th"
                ")+1]"
                "[normalize-space()!='' and normalize-space()!='0' and normalize-space()!='0.00']"
            ),
            f"xpath={scoped}//datatable-body-row//datatable-body-cell[contains(.,'.')]",
            (
                f"xpath={scoped}//*[contains(normalize-space(),'Total (Price)')]"
                "/following::*[normalize-space()!='' and contains(.,'.')][1]"
            ),
        ]

    def _scroll_surcharge_section_into_view(self) -> None:
        section = self.find_visible(self.surcharge_section_selectors)
        if section is not None:
            section.scroll_into_view_if_needed()

    @log_method("Verify Total (Price) is displayed in Surcharge List")
    def is_total_price_displayed(self) -> bool:
        self._scroll_surcharge_section_into_view()
        self.wait_for_visible(self.total_price_label_selectors, "Total (Price) label")
        self.wait_for_visible(
            self._total_price_value_selectors(),
            "Total (Price) value",
        )
        return True

    @log_method("Click Generate on Surcharge List")
    def click_generate_surcharge(self) -> "EtmsCostOfRoutePage":
        self._scroll_surcharge_section_into_view()
        self.wait_for_visible(self.surcharge_section_selectors, "Surcharge List section")
        self.click_when_ready(self.generate_button_selectors, "Generate button")
        self.wait_for_page_stable()
        self._scroll_surcharge_section_into_view()
        return self

    @log_method("Click Save")
    def click_save(self) -> "EtmsCostOfRoutePage":
        self.click_when_ready(self.save_button_selectors, "Save button")
        self._wait_for_loading_overlay_hidden()
        self.wait_for_page_stable()
        return self

    def _success_message_selectors(self, message: str) -> list[str]:
        return [
            f"#toast-container .toast-message:has-text('{message}')",
            f"#toast-container *:has-text('{message}')",
            f".toast:has-text('{message}')",
            f"xpath=//*[contains(@class,'toast') and contains(.,'{message}')]",
            f".swal2-popup:has-text('{message}')",
            (
                f"xpath=//*[contains(@class,'swal2-success') "
                f"and contains(normalize-space(),'{message}')]"
            ),
            f"xpath=//*[contains(normalize-space(),'{message}')]",
            f"text={message}",
        ]

    @log_method("Verify success message is displayed")
    def is_success_message_displayed(self, message: str) -> bool:
        self.wait_for_visible(
            self._success_message_selectors(message),
            f"Success message: {message}",
            timeout=settings.page_load_timeout,
        )
        return True

    def _save_error_message_selectors(self) -> list[str]:
        return [
            "#toast-container .toast-error",
            ".toast-error",
            "xpath=//*[contains(@class,'toast-error')]",
            (
                "xpath=//*[contains(@class,'swal2-icon-error')]"
                "/ancestor::div[contains(@class,'swal2-popup')]"
            ),
            "xpath=//*[contains(@class,'invalid-feedback') and normalize-space()!='']",
        ]

    def _is_save_returned_to_list(self) -> bool:
        url = self.current_url.lower().replace("_", "-")
        if self.modify_page_hash in url:
            return False
        if self.list_page_hash not in url:
            return False
        if self._is_detail_form_displayed():
            return False
        return self._has_list_tabs()

    @log_method("Wait for save success message")
    def wait_for_save_success(self, message: str) -> "EtmsCostOfRoutePage":
        deadline = time.monotonic() + settings.page_load_timeout / 1000
        while time.monotonic() < deadline:
            if self.find_visible(self._success_message_selectors(message)) is not None:
                return self

            error = self.find_visible(self._save_error_message_selectors())
            if error is not None:
                error_text = error.inner_text().strip()
                raise AssertionError(
                    f"Save failed: {error_text or 'unknown validation/error message'}"
                )

            if self._is_save_returned_to_list() and "New data added" in message:
                logger.info(
                    "Save success — returned to Cost Of Route list (toast may have closed)"
                )
                return self

            self._wait_for_loading_overlay_hidden(timeout=settings.polling_interval * 2)
            self.page.wait_for_timeout(settings.polling_interval)

        self.wait_for_add_modal_closed()
        if self._is_save_returned_to_list() and "New data added" in message:
            return self

        raise AssertionError(f"Success message not displayed after save: {message}")

    @log_method("Wait for save completed")
    def wait_for_add_modal_closed(self) -> "EtmsCostOfRoutePage":
        deadline = time.monotonic() + settings.page_load_timeout / 1000
        while time.monotonic() < deadline:
            if self.modify_page_hash not in self.current_url.lower().replace("_", "-"):
                break
            modal = self.page.locator(
                "xpath=//div[contains(@class,'modal') and contains(@class,'show')]"
                "[.//*[contains(normalize-space(),'Add New Cost Of Route')]]"
            )
            if modal.count() == 0 or not modal.first.is_visible():
                break
            self.page.wait_for_timeout(settings.polling_interval)
        self._wait_for_loading_overlay_hidden()
        self.wait_for_page_stable()
        return self

    def _list_portlet_root(self) -> str:
        return (
            "//*[contains(@class,'page-title') and contains(normalize-space(),'Cost Of Route')]"
            "/ancestor::div[contains(@class,'m-portlet') or contains(@class,'portlet')][1]"
        )

    def _list_portlet_body(self) -> str:
        return (
            f"{self._list_portlet_root()}"
            "//div[contains(@class,'m-portlet__body') or contains(@class,'portlet__body')]"
        )

    def _filter_tab_link_xpath(self, tab_name: str) -> str:
        lit = self._xpath_literal(tab_name.strip())
        return (
            f"//ul[contains(@class,'filter-tab')]"
            f"//a[contains(normalize-space(),{lit})]"
        )

    def _list_tab_link_selectors(self, tab_name: str) -> list[str]:
        tab_xpath = self._filter_tab_link_xpath(tab_name)
        list_body = self._list_portlet_body()
        portlet = self._list_portlet_root()
        return [
            f"xpath={tab_xpath}",
            f"xpath={list_body}{tab_xpath}",
            f"xpath={portlet}{tab_xpath}",
        ]

    def _active_tab_grid_scopes(self, tab_name: str) -> list[str]:
        """Grid scope after filter-tab click — single shared ngx-datatable in portlet."""
        list_body = self._list_portlet_body()
        portlet = self._list_portlet_root()
        return [
            list_body,
            (
                f"{portlet}//div[contains(@class,'m-portlet__body') "
                "or contains(@class,'portlet__body')]"
            ),
            portlet,
        ]

    def _swal_paragraph_selectors(self, message: str) -> list[str]:
        lit = self._xpath_literal(message)
        return [f"xpath=//p[normalize-space()={lit}]"]

    def _filtered_cor_code_row_selectors(self, cor_code: str) -> list[str]:
        code = self._normalize_cor_code(cor_code)
        lit = self._xpath_literal(code)
        table = self._cost_of_route_list_table_xpath
        return [
            f"xpath={table}//tr[not(contains(@class,'filter-row'))][contains(.,{lit})]",
            f"xpath={table}//tbody//tr[td][contains(.,{lit})]",
        ]

    def _filtered_route_code_row_selectors(self, route_code: str) -> list[str]:
        lit = self._xpath_literal(route_code.strip())
        table = self._cost_of_route_list_table_xpath
        return [
            f"xpath={table}//tr[not(contains(@class,'filter-row'))][contains(.,{lit})]",
            f"xpath={table}//tbody//tr[td][contains(.,{lit})]",
        ]

    def _wait_for_loading_overlay_hidden(self, timeout: int | None = None) -> None:
        timeout = timeout or settings.browser_timeout
        deadline = time.monotonic() + timeout / 1000
        while time.monotonic() < deadline:
            if self.find_visible(self.list_grid.loading_overlay_selectors) is None:
                return
            self.page.wait_for_timeout(settings.polling_interval)

    def _wait_for_list_tab_active(
        self,
        tab_name: str,
        timeout: int | None = None,
    ) -> bool:
        timeout = timeout or settings.browser_timeout
        deadline = time.monotonic() + timeout / 1000
        while time.monotonic() < deadline:
            if self._is_list_tab_active(tab_name):
                return True
            self.page.wait_for_timeout(settings.polling_interval)
        return False

    def _wait_for_list_tab_content_loaded(self, tab_name: str) -> None:
        deadline = time.monotonic() + settings.browser_timeout / 1000
        while time.monotonic() < deadline:
            if not self._is_list_tab_active(tab_name):
                self.page.wait_for_timeout(settings.polling_interval)
                continue

            if self.find_visible(self.list_grid.loading_overlay_selectors) is not None:
                self.page.wait_for_timeout(settings.polling_interval)
                continue

            if self.find_visible(self.list_table_selectors) is not None:
                self.list_grid.wait_until_ready(
                    self.list_table_selectors,
                    "Cost Of Route table",
                )
                self.wait_for_page_stable()
                return

            self.page.wait_for_timeout(settings.polling_interval)

        raise AssertionError(
            f"Tab '{tab_name}' content did not finish loading after click."
        )

    def _is_list_tab_active(self, tab_name: str) -> bool:
        lit = self._xpath_literal(tab_name.strip())
        active_selectors = [
            (
                f"xpath=//ul[contains(@class,'filter-tab')]"
                f"//li[contains(@class,'active')]"
                f"//a[contains(normalize-space(),{lit})]"
            ),
            (
                f"xpath=//ul[contains(@class,'filter-tab')]"
                f"//a[contains(@class,'active') and contains(normalize-space(),{lit})]"
            ),
        ]
        return self.find_visible(active_selectors) is not None

    def _is_detail_form_displayed(self) -> bool:
        selectors = [
            (
                "xpath=//label[contains(normalize-space(),'Code')]"
                "/following::span[contains(normalize-space(),'/COR-')][1]"
            ),
            (
                "xpath=//label[contains(normalize-space(),'Code')]"
                "/ancestor::div[contains(@class,'form-group') or contains(@class,'col-')][1]"
                "//span[contains(normalize-space(),'/COR-')]"
            ),
        ]
        return self.find_visible(selectors) is not None

    def _has_list_tabs(self, *, timeout_ms: int | None = None) -> bool:
        timeout_ms = timeout_ms or min(settings.browser_timeout, 15000)
        deadline = time.monotonic() + timeout_ms / 1000
        list_body = self._list_portlet_body()
        portlet = self._list_portlet_root()
        tab_selectors = [
            "xpath=//ul[contains(@class,'filter-tab')]//a",
            f"xpath={list_body}//ul[contains(@class,'filter-tab')]//a",
            f"xpath={portlet}//ul[contains(@class,'filter-tab')]//a",
        ]
        while time.monotonic() < deadline:
            if self.find_visible(tab_selectors) is not None:
                return True
            self.page.wait_for_timeout(settings.polling_interval)
        return False

    def _is_on_list_page(self) -> bool:
        url = self.current_url.lower().replace("_", "-")
        if self.list_page_hash not in url:
            return False
        if self.modify_page_hash in url:
            return False
        if any(marker in url for marker in self.detail_page_hash_markers):
            return False
        if self._is_detail_form_displayed():
            return False
        return self._has_list_tabs()

    def _fill_route_code_filter(
        self,
        selectors: list[str],
        route_code: str,
        element_name: str,
    ) -> None:
        code_filter = self.wait_for_visible(selectors, element_name)
        code_filter.scroll_into_view_if_needed()
        code_filter.click()
        code_filter.fill("")
        code_filter.fill(route_code)
        # ngx-datatable filter row applies on input — no search button / Enter needed
        self.page.wait_for_timeout(settings.polling_interval)
        self.wait_for_page_stable()

    def _row_match_clause(
        self,
        route_code: str,
        vehicle_type: str | None = None,
    ) -> str:
        row_predicates = [f"contains(.,'{route_code}')"]
        if vehicle_type:
            row_predicates.append(f"contains(.,'{vehicle_type}')")
        return " and ".join(row_predicates)

    def _scoped_row_xpaths(
        self,
        row_match: str,
        *,
        list_body: str | None = None,
    ) -> list[str]:
        body = list_body or self._list_portlet_body()
        return [
            f"{body}//datatable-row-wrapper[{row_match}]",
            f"//datatable-row-wrapper[{row_match}]",
            f"{body}//datatable-body-row[{row_match}]",
            f"//datatable-body-row[{row_match}]",
            (
                f"{body}//tr[{row_match} and not(contains(@class,'filter-row'))]"
            ),
            f"//tr[{row_match} and not(contains(@class,'filter-row'))]",
        ]

    def _row_action_btn_selectors(
        self,
        route_code: str,
        vehicle_type: str | None = None,
    ) -> list[str]:
        row_match = self._row_match_clause(route_code, vehicle_type)
        action = "//*[contains(@class,'action-btn')]"
        selectors: list[str] = []
        for scope in self._scoped_row_xpaths(row_match):
            selectors.append(f"xpath={scope}//datatable-row-right{action}")
            selectors.append(f"xpath={scope}{action}")
        return selectors

    def _list_route_row_selectors(self, route_code: str) -> list[str]:
        list_body = self._list_portlet_body()
        row_match = self._row_match_clause(route_code)
        return [
            *self._filtered_route_code_row_selectors(route_code),
            *(
                f"xpath={scope}"
                for scope in self._scoped_row_xpaths(row_match, list_body=list_body)
            ),
        ]

    def _has_route_row(
        self,
        route_code: str,
        vehicle_type: str | None = None,
    ) -> bool:
        row_match = self._row_match_clause(route_code, vehicle_type)
        list_body = self._list_portlet_body()
        selectors = [
            *self._filtered_route_code_row_selectors(route_code),
            *(
                f"xpath={scope}"
                for scope in self._scoped_row_xpaths(row_match, list_body=list_body)
            ),
        ]
        return self.find_visible(selectors) is not None

    @log_method("Filter Route Code on Cost Of Route list")
    def filter_route_code_on_list(self, route_code: str) -> "EtmsCostOfRoutePage":
        self.is_list_page_displayed()
        self.list_grid.wait_until_ready(
            self.list_table_selectors,
            "Cost Of Route table",
        )
        self.wait_for_page_stable()

        header = self.find_visible(self.list_route_code_header_selectors)
        if header is not None:
            header.scroll_into_view_if_needed()
            header.click(force=True)
            self.wait_for_page_stable()

        self._fill_route_code_filter(
            self.list_route_code_filter_selectors,
            route_code,
            "Cost Of Route list Route Code filter input",
        )
        return self

    @log_method("Search Route Code on Cost Of Route list and wait for row")
    def search_route_on_list(self, route_code: str) -> "EtmsCostOfRoutePage":
        self.filter_route_code_on_list(route_code)
        self.wait_for_visible(
            self._list_route_row_selectors(route_code),
            f"Cost Of Route list row: {route_code}",
        )
        return self

    @log_method("Delete all filtered Cost Of Route rows by route code")
    def delete_all_filtered_rows_by_route_code(
        self,
        route_code: str,
        *,
        expected_delete_message: str = "Data delete success",
        vehicle_type: str | None = None,
        max_attempts: int = 20,
    ) -> "EtmsCostOfRoutePage":
        for _ in range(max_attempts):
            if not self._has_route_row(route_code, vehicle_type):
                return self
            self.click_row_action_btn(route_code, vehicle_type)
            self.click_row_delete_button(route_code, vehicle_type)
            self.is_delete_confirm_displayed()
            self.click_delete_confirm_ok()
            self.is_success_message_displayed(expected_delete_message)
            self.wait_for_page_stable()

        raise AssertionError(
            f"Could not delete all Cost Of Route rows for route {route_code} "
            f"after {max_attempts} attempts."
        )

    @log_method("Prepare Updating tab before create Cost Of Route")
    def prepare_updating_tab_before_create(
        self,
        route_code: str,
        *,
        tab_name: str = "Updating",
        expected_delete_message: str = "Data delete success",
    ) -> "EtmsCostOfRoutePage":
        """Filter by route code on Updating tab; delete rows only when any are visible."""
        self.click_list_tab(tab_name, force=True)
        self.filter_route_code_on_list(route_code)
        if not self._has_route_row(route_code):
            logger.info(
                "No Cost Of Route row for route {} on tab {} — skip pre-cleanup, continue create",
                route_code,
                tab_name,
            )
            return self

        self.delete_all_filtered_rows_by_route_code(
            route_code,
            expected_delete_message=expected_delete_message,
        )
        return self

    @log_method("Refresh Cost Of Route list")
    def refresh_list_page(self) -> "EtmsCostOfRoutePage":
        refresh_selectors = [
            "button[title='Refresh']",
            "xpath=//button[@title='Refresh']",
            "button:has(i.fa-sync)",
            "button:has(i.fa-refresh)",
            "xpath=//button[.//i[contains(@class,'fa-sync') or contains(@class,'fa-refresh')]]",
        ]
        refresh = self.find_visible(refresh_selectors)
        if refresh is not None:
            refresh.click(force=True)
            self.wait_for_page_stable()
        else:
            self.page.reload(wait_until="domcontentloaded")
            self.wait_for_page_stable()
        self.list_grid.wait_until_ready(
            self.list_table_selectors,
            "Cost Of Route table",
        )
        return self

    @log_method("Ensure Cost Of Route list page is displayed")
    def ensure_list_page_displayed(
        self,
        menu_text: str = "Cost Of Route",
    ) -> "EtmsCostOfRoutePage":
        self.wait_for_add_modal_closed()
        if self._is_detail_form_displayed() or not self._has_list_tabs():
            self.open_via_menu_search(menu_text)
        self.is_list_page_displayed()
        return self

    @log_method("Click list tab on Cost Of Route page")
    def click_list_tab(
        self,
        tab_name: str,
        *,
        force: bool = False,
    ) -> "EtmsCostOfRoutePage":
        tab_name = tab_name.strip()
        self.list_grid.wait_until_ready(
            self.list_table_selectors,
            "Cost Of Route table",
        )
        self._wait_for_loading_overlay_hidden()

        if not force and self._is_list_tab_active(tab_name):
            self._wait_for_list_tab_content_loaded(tab_name)
            return self

        tab = self.wait_for_visible(
            self._list_tab_link_selectors(tab_name),
            f"{tab_name} tab",
        )
        tab.scroll_into_view_if_needed()
        self._wait_for_loading_overlay_hidden()
        tab.click(force=True)

        if not self._wait_for_list_tab_active(tab_name, timeout=10_000):
            self._wait_for_loading_overlay_hidden()
            tab.click(force=True)
            if not self._wait_for_list_tab_active(tab_name):
                raise AssertionError(f"Tab '{tab_name}' is not active after click.")

        self._wait_for_list_tab_content_loaded(tab_name)
        return self

    @log_method("Click Accepted tab on Cost Of Route list")
    def click_accepted_tab(self) -> "EtmsCostOfRoutePage":
        return self.click_list_tab("Accepted")

    @log_method("Click row action button on list grid")
    def click_row_action_btn(
        self,
        route_code: str,
        vehicle_type: str | None = None,
    ) -> "EtmsCostOfRoutePage":
        row_match = self._row_match_clause(route_code, vehicle_type)
        list_body = self._list_portlet_body()
        row_wrapper = self.find_visible(
            [
                f"xpath={list_body}//datatable-row-wrapper[{row_match}]",
                f"xpath=//datatable-row-wrapper[{row_match}]",
                f"xpath={list_body}//tr[{row_match} and not(contains(@class,'filter-row'))]",
            ]
        )
        if row_wrapper is not None:
            row_wrapper.scroll_into_view_if_needed()
            row_wrapper.hover()
            self.wait_for_page_stable()

        action_btn = self.wait_for_visible(
            self._row_action_btn_selectors(route_code, vehicle_type),
            "Row action button",
        )
        action_btn.scroll_into_view_if_needed()
        action_btn.click(force=True)
        self.wait_for_page_stable()
        return self

    def _row_copy_btn_selectors(
        self,
        route_code: str,
        vehicle_type: str | None = None,
    ) -> list[str]:
        row_match = self._row_match_clause(route_code, vehicle_type)
        list_body = self._list_portlet_body()
        row_copy = (
            "//a[@title='Copy' and contains(@class,'btn-ftl-icon')]"
        )
        row_copy_by_id = "//a[contains(@id,'btnButtonRowCopy')]"
        return [
            f"xpath={list_body}//datatable-row-wrapper[{row_match}]{row_copy_by_id}",
            f"xpath={list_body}//datatable-row-wrapper[{row_match}]{row_copy}",
            f"xpath=//datatable-row-wrapper[{row_match}]{row_copy_by_id}",
            f"xpath=//datatable-row-wrapper[{row_match}]{row_copy}",
            f"xpath={list_body}//tr[{row_match} and not(contains(@class,'filter-row'))]{row_copy_by_id}",
            f"xpath={list_body}//tr[{row_match} and not(contains(@class,'filter-row'))]{row_copy}",
            f"xpath=//tr[{row_match} and not(contains(@class,'filter-row'))]{row_copy_by_id}",
            f"xpath=//tr[{row_match} and not(contains(@class,'filter-row'))]{row_copy}",
            f"xpath={list_body}//datatable-body-row[{row_match}]{row_copy_by_id}",
            f"xpath={list_body}//datatable-body-row[{row_match}]{row_copy}",
            *self.copy_action_selectors,
        ]

    @log_method("Click row Copy button on list grid")
    def click_row_copy_button(
        self,
        route_code: str,
        vehicle_type: str | None = None,
    ) -> "EtmsCostOfRoutePage":
        row_match = self._row_match_clause(route_code, vehicle_type)
        list_body = self._list_portlet_body()
        copy_btn = self.wait_for_visible(
            [
                *self._row_copy_btn_selectors(route_code, vehicle_type),
                (
                    f"xpath={list_body}//datatable-row-wrapper[{row_match}]"
                    "//a[contains(@class,'btn-ftl-icon') and (@title='Copy' or contains(@id,'Copy'))]"
                ),
                (
                    f"xpath={list_body}//datatable-row-wrapper[{row_match}]"
                    "//a[contains(@class,'btn-ftl-icon') and .//i[contains(@class,'copy')]]"
                ),
            ],
            "Row Copy button",
        )
        copy_btn.scroll_into_view_if_needed()
        copy_btn.click(force=True)
        self.wait_for_page_stable()
        return self

    @log_method("Verify copy confirmation popup is displayed")
    def is_copy_confirm_displayed(
        self,
        message: str | None = None,
    ) -> bool:
        expected = message or self.copy_confirm_message
        selectors = [
            f"xpath=//*[contains(normalize-space(),'{expected}')]",
            *self.copy_confirm_popup_selectors,
        ]
        self.wait_for_visible(
            selectors,
            f"Copy confirm: {expected}",
        )
        return True

    @log_method("Click Cancel on copy confirmation popup")
    def click_copy_confirm_cancel(self) -> "EtmsCostOfRoutePage":
        self.click_when_ready(self.copy_confirm_cancel_selectors, "Copy confirm Cancel")
        self.wait_for_page_stable()
        return self

    @log_method("Click OK on copy confirmation popup")
    def click_copy_confirm_ok(self) -> "EtmsCostOfRoutePage":
        self.click_when_ready(self.copy_confirm_ok_selectors, "Copy confirm OK")
        self.wait_for_page_stable()
        return self

    def _row_delete_btn_selectors(
        self,
        route_code: str,
        vehicle_type: str | None = None,
    ) -> list[str]:
        row_match = self._row_match_clause(route_code, vehicle_type)
        list_body = self._list_portlet_body()
        row_delete = (
            "//a[@title='Delete' and contains(@class,'btn-ftl-icon') "
            "and contains(@class,'text-danger')]"
        )
        row_delete_by_id = "//a[contains(@id,'btnButtonRowDelete')]"
        return [
            f"xpath={list_body}//datatable-row-wrapper[{row_match}]{row_delete_by_id}",
            f"xpath={list_body}//datatable-row-wrapper[{row_match}]{row_delete}",
            f"xpath=//datatable-row-wrapper[{row_match}]{row_delete_by_id}",
            f"xpath=//datatable-row-wrapper[{row_match}]{row_delete}",
            f"xpath={list_body}//tr[{row_match} and not(contains(@class,'filter-row'))]{row_delete_by_id}",
            f"xpath={list_body}//tr[{row_match} and not(contains(@class,'filter-row'))]{row_delete}",
            f"xpath=//tr[{row_match} and not(contains(@class,'filter-row'))]{row_delete_by_id}",
            f"xpath=//tr[{row_match} and not(contains(@class,'filter-row'))]{row_delete}",
            f"xpath={list_body}//tr[td and not(contains(@class,'filter-row'))]{row_delete_by_id}",
            *self.delete_action_selectors,
        ]

    def _row_send_request_btn_selectors(
        self,
        route_code: str,
        vehicle_type: str | None = None,
    ) -> list[str]:
        row_match = self._row_match_clause(route_code, vehicle_type)
        row_send = (
            "//a[contains(@title,'Send Request') and contains(@class,'btn-ftl-icon')]"
        )
        row_send_by_id = "//a[contains(@id,'btnButtonRowSendRequest')]"
        row_send_icon = (
            "//a[contains(@class,'btn-ftl-icon') and .//i[contains(@class,'send')]]"
        )
        selectors: list[str] = []
        for scope in self._scoped_row_xpaths(row_match):
            selectors.extend(
                [
                    f"xpath={scope}//datatable-row-right{row_send_by_id}",
                    f"xpath={scope}//datatable-row-right{row_send}",
                    f"xpath={scope}//datatable-row-right{row_send_icon}",
                    f"xpath={scope}{row_send_by_id}",
                    f"xpath={scope}{row_send}",
                    f"xpath={scope}{row_send_icon}",
                    (
                        f"xpath={scope}//*[contains(@class,'action-btn')]"
                        f"/following-sibling::a[contains(@title,'Send Request')]"
                    ),
                ]
            )
        return selectors

    @log_method("Click row Delete button on list grid")
    def click_row_delete_button(
        self,
        route_code: str,
        vehicle_type: str | None = None,
    ) -> "EtmsCostOfRoutePage":
        delete_btn = self.wait_for_visible(
            self._row_delete_btn_selectors(route_code, vehicle_type),
            "Row Delete button",
        )
        delete_btn.scroll_into_view_if_needed()
        delete_btn.click(force=True)
        self.wait_for_page_stable()
        return self

    @log_method("Verify delete confirmation popup is displayed")
    def is_delete_confirm_displayed(self) -> bool:
        self.wait_for_visible(
            self.delete_confirm_popup_selectors,
            f"Delete confirm: {self.delete_confirm_message}",
        )
        return True

    @log_method("Click OK on delete confirmation popup")
    def click_delete_confirm_ok(self) -> "EtmsCostOfRoutePage":
        self.click_when_ready(self.delete_confirm_ok_selectors, "Delete confirm OK")
        self.wait_for_page_stable()
        return self

    @log_method("Delete Cost Of Route record from list")
    def delete_cost_of_route(
        self,
        route_code: str,
        expected_delete_message: str,
        vehicle_type: str | None = None,
    ) -> "EtmsCostOfRoutePage":
        self.click_row_action_btn(route_code, vehicle_type)
        self.click_row_delete_button(route_code, vehicle_type)
        self.is_delete_confirm_displayed()
        self.click_delete_confirm_ok()
        self.is_success_message_displayed(expected_delete_message)
        return self

    @log_method("Delete Cost Of Route on first tab that has matching row")
    def delete_cost_of_route_on_tabs(
        self,
        route_code: str,
        expected_delete_message: str,
        vehicle_type: str | None = None,
        *,
        tabs: list[str],
    ) -> "EtmsCostOfRoutePage":
        for tab in tabs:
            if self.find_visible(self._list_tab_link_selectors(tab)) is None:
                logger.info("Tab '{}' not found — skip delete on this tab", tab)
                continue
            self.click_list_tab(tab, force=True)
            self.filter_route_code_on_list(route_code)
            if not self._has_route_row(route_code, vehicle_type):
                logger.info(
                    "No row for route {} on tab '{}' — try next tab",
                    route_code,
                    tab,
                )
                continue
            return self.delete_cost_of_route(
                route_code,
                expected_delete_message,
                vehicle_type,
            )

        raise AssertionError(
            f"Cannot delete Cost Of Route {route_code} on tabs {tabs}."
        )

    def _cor_code_pattern(self) -> re.Pattern[str]:
        return re.compile(r"\d+/COR-[A-Z0-9]+", re.IGNORECASE)

    def _code_column_cell_selectors(
        self,
        list_body: str,
        row_match: str,
    ) -> list[str]:
        code_header_idx = (
            f"count({list_body}//datatable-header-cell"
            "[.//span[normalize-space()='Code'] or normalize-space()='Code']"
            "/preceding-sibling::datatable-header-cell)+1"
        )
        row_scope = f"{list_body}//datatable-row-wrapper[{row_match}]"
        return [
            f"xpath={row_scope}//datatable-body-cell[{code_header_idx}]//span[normalize-space()!='']",
            f"xpath={row_scope}//datatable-body-cell[{code_header_idx}]",
            f"xpath={row_scope}//span[contains(normalize-space(),'/COR-')]",
            f"xpath=//datatable-row-wrapper[{row_match}]//span[contains(normalize-space(),'/COR-')]",
            (
                f"xpath={list_body}//tr[{row_match} and not(contains(@class,'filter-row'))]"
                "/td[count(//th[normalize-space()='Code']/preceding-sibling::th)+1]//span"
            ),
        ]

    def _normalize_cor_code(self, raw_text: str) -> str:
        text = " ".join(raw_text.split())
        match = self._cor_code_pattern().search(text)
        if match is not None:
            return match.group(0)
        return text.strip()

    def _xpath_literal(self, value: str) -> str:
        if "'" not in value:
            return f"'{value}'"
        if '"' not in value:
            return f'"{value}"'
        parts = value.split("'")
        return "concat(" + ", \"'\", ".join(f"'{part}'" for part in parts) + ")"

    def _cor_code_row_predicate(self, cor_code: str) -> str:
        code = self._normalize_cor_code(cor_code)
        lit = self._xpath_literal(code)
        return (
            f".//span[contains(normalize-space(),{lit})] or "
            f".//div[contains(@class,'datatable-body-cell-label')]"
            f"[contains(normalize-space(),{lit})]"
        )

    def _row_match_by_cor_code(self, cor_code: str) -> str:
        return self._cor_code_row_predicate(cor_code)

    def _cor_code_text_selectors(self, cor_code: str) -> list[str]:
        code = self._normalize_cor_code(cor_code)
        lit = self._xpath_literal(code)
        list_body = self._list_portlet_body()
        text_match = f"contains(normalize-space(),{lit})"
        return [
            f"xpath={list_body}//datatable-body//span[{text_match}]",
            (
                f"xpath={list_body}//datatable-body//div"
                f"[contains(@class,'datatable-body-cell-label')][{text_match}]"
            ),
            f"xpath={list_body}//datatable-body//*[{text_match}]",
            f"xpath={list_body}//table//tbody//span[{text_match}]",
            f"xpath={list_body}//table//tbody//td[{text_match}]",
        ]

    def _list_row_by_cor_code_selectors(self, cor_code: str) -> list[str]:
        row_pred = self._cor_code_row_predicate(cor_code)
        list_body = self._list_portlet_body()
        return [
            *self._filtered_cor_code_row_selectors(cor_code),
            f"xpath={list_body}//datatable-row-wrapper[{row_pred}]",
            f"xpath=//datatable-row-wrapper[{row_pred}]",
            f"xpath={list_body}//datatable-body-row[{row_pred}]",
            (
                f"xpath={list_body}//tr[not(contains(@class,'filter-row'))]"
                f"[{row_pred}]"
            ),
            *self._cor_code_text_selectors(cor_code),
        ]

    def _find_first_visible_locator(self, selectors: list[str]) -> Locator | None:
        from playwright.sync_api import Locator

        for selector in selectors:
            locator = self.page.locator(selector)
            try:
                count = locator.count()
            except Exception:
                continue
            for index in range(min(count, 25)):
                candidate: Locator = locator.nth(index)
                try:
                    if candidate.is_visible():
                        return candidate
                except Exception:
                    continue
        return None

    def _row_action_btn_by_cor_code_selectors(self, cor_code: str) -> list[str]:
        row_match = self._row_match_by_cor_code(cor_code)
        action = "//*[contains(@class,'action-btn')]"
        selectors: list[str] = []
        for scope in self._scoped_row_xpaths(row_match):
            selectors.append(f"xpath={scope}//datatable-row-right{action}")
            selectors.append(f"xpath={scope}{action}")
        return selectors

    def _row_icon_btn_by_cor_code_selectors(
        self,
        cor_code: str,
        *,
        title: str,
        id_fragment: str,
        extra_class: str = "",
        icon_class_fragment: str = "",
        fallback_selectors: list[str],
    ) -> list[str]:
        row_match = self._row_match_by_cor_code(cor_code)
        list_body = self._list_portlet_body()
        class_clause = f" and {extra_class}" if extra_class else ""
        row_link = (
            f"//a[@title='{title}' and contains(@class,'btn-ftl-icon'){class_clause}]"
        )
        row_link_by_id = f"//a[contains(@id,'{id_fragment}')]"
        containers = [
            f"{list_body}//datatable-row-wrapper[{row_match}]",
            f"//datatable-row-wrapper[{row_match}]",
            (
                f"{list_body}//tr[{row_match} and not(contains(@class,'filter-row'))]"
            ),
            f"//tr[{row_match} and not(contains(@class,'filter-row'))]",
            f"{list_body}//datatable-body-row[{row_match}]",
        ]
        selectors: list[str] = []
        for container in containers:
            selectors.append(f"xpath={container}{row_link_by_id}")
            selectors.append(f"xpath={container}{row_link}")
        if icon_class_fragment:
            selectors.append(
                f"xpath={list_body}//datatable-row-wrapper[{row_match}]"
                f"//a[contains(@class,'btn-ftl-icon') and "
                f".//i[contains(@class,'{icon_class_fragment}')]]"
            )
        selectors.extend(fallback_selectors)
        return selectors

    def _row_send_request_btn_by_cor_code_selectors(self, cor_code: str) -> list[str]:
        row_match = self._row_match_by_cor_code(cor_code)
        list_body = self._list_portlet_body()
        row_send = (
            "//a[contains(@title,'Send Request') and contains(@class,'btn-ftl-icon')]"
        )
        row_send_by_id = "//a[contains(@id,'btnButtonRowSendRequest')]"
        return [
            f"xpath={list_body}//datatable-row-wrapper[{row_match}]{row_send_by_id}",
            f"xpath={list_body}//datatable-row-wrapper[{row_match}]{row_send}",
            f"xpath=//datatable-row-wrapper[{row_match}]{row_send_by_id}",
            f"xpath=//datatable-row-wrapper[{row_match}]{row_send}",
            f"xpath={list_body}//tr[{row_match} and not(contains(@class,'filter-row'))]{row_send_by_id}",
            f"xpath={list_body}//tr[{row_match} and not(contains(@class,'filter-row'))]{row_send}",
            f"xpath=//tr[{row_match} and not(contains(@class,'filter-row'))]{row_send_by_id}",
            f"xpath=//tr[{row_match} and not(contains(@class,'filter-row'))]{row_send}",
            f"xpath={list_body}//datatable-body-row[{row_match}]{row_send_by_id}",
            f"xpath={list_body}//datatable-body-row[{row_match}]{row_send}",
            *self.send_request_action_selectors,
        ]

    def _row_reject_btn_selectors(
        self,
        route_code: str,
        vehicle_type: str | None = None,
    ) -> list[str]:
        row_match = self._row_match_clause(route_code, vehicle_type)
        row_reject = (
            "//a[contains(@title,'Reject') and contains(@class,'btn-ftl-icon')]"
        )
        row_reject_by_id = "//a[contains(@id,'btnButtonRowReject')]"
        selectors: list[str] = []
        for scope in self._scoped_row_xpaths(row_match):
            selectors.extend(
                [
                    f"xpath={scope}//datatable-row-right{row_reject_by_id}",
                    f"xpath={scope}//datatable-row-right{row_reject}",
                    f"xpath={scope}{row_reject_by_id}",
                    f"xpath={scope}{row_reject}",
                    (
                        f"xpath={scope}//*[contains(@class,'action-btn')]"
                        f"/following-sibling::a[contains(@title,'Reject')]"
                    ),
                ]
            )
        return selectors

    def _row_reject_btn_by_cor_code_selectors(self, cor_code: str) -> list[str]:
        return self._row_icon_btn_by_cor_code_selectors(
            cor_code,
            title="Reject",
            id_fragment="btnButtonRowReject",
            icon_class_fragment="reject",
            fallback_selectors=self.reject_action_selectors,
        )

    def _row_delete_btn_by_cor_code_selectors(self, cor_code: str) -> list[str]:
        return self._row_icon_btn_by_cor_code_selectors(
            cor_code,
            title="Delete",
            id_fragment="btnButtonRowDelete",
            extra_class="contains(@class,'text-danger')",
            icon_class_fragment="trash",
            fallback_selectors=self.delete_action_selectors,
        )

    def _popup_selectors_for_message(self, message: str) -> list[str]:
        return [
            f"xpath=//*[contains(normalize-space(),'{message}')]",
            f".swal2-popup:has-text('{message}')",
            f".modal.show:has-text('{message}')",
        ]

    @log_method("Verify popup message is displayed")
    def is_popup_message_displayed(self, message: str) -> bool:
        self.wait_for_visible(
            self._popup_selectors_for_message(message),
            f"Popup: {message}",
        )
        return True

    @log_method("Click OK on SweetAlert popup")
    def click_swal_ok(self) -> "EtmsCostOfRoutePage":
        self.click_when_ready(self._swal_ok_selectors, "SweetAlert OK")
        self.wait_for_page_stable()
        return self

    @log_method("Click Cancel on SweetAlert popup")
    def click_swal_cancel(self) -> "EtmsCostOfRoutePage":
        self.click_when_ready(self._swal_cancel_selectors, "SweetAlert Cancel")
        self.wait_for_page_stable()
        return self

    @log_method("Read COR code from list row")
    def read_cor_code_from_list_row(
        self,
        route_code: str,
        vehicle_type: str | None = None,
    ) -> str:
        list_body = self._list_portlet_body()
        row_match = self._row_match_clause(route_code, vehicle_type)
        self.wait_for_visible(
            [
                f"xpath={list_body}//datatable-row-wrapper[{row_match}]",
                f"xpath=//datatable-row-wrapper[{row_match}]",
                f"xpath={list_body}//tr[{row_match} and not(contains(@class,'filter-row'))]",
            ],
            f"Cost Of Route row: {route_code}",
        )
        return self._read_cor_code_span_for_route(route_code)

    def _read_cor_code_span_for_route(self, route_code: str) -> str:
        list_body = self._list_portlet_body()
        span = self.wait_for_visible(
            [
                (
                    f"xpath={list_body}//datatable-row-wrapper[contains(.,'{route_code}')]"
                    "//span[contains(normalize-space(),'/COR-')]"
                ),
                (
                    f"xpath=//datatable-row-wrapper[contains(.,'{route_code}')]"
                    "//span[contains(normalize-space(),'/COR-')]"
                ),
                (
                    f"xpath={list_body}//tr[contains(.,'{route_code}') "
                    "and not(contains(@class,'filter-row'))]"
                    "//span[contains(normalize-space(),'/COR-')]"
                ),
                (
                    f"xpath={list_body}//datatable-row-wrapper[contains(.,'{route_code}')]"
                    "//datatable-body-cell[1]//span"
                ),
            ],
            f"COR code span for route {route_code}",
        )
        code_text = self._normalize_cor_code(span.inner_text())
        if not self._cor_code_pattern().search(code_text):
            raise AssertionError(f"Invalid COR code format: {code_text!r}")
        return code_text

    def _extract_cor_code_from_row(
        self,
        row,
        list_body: str,
        row_match: str,
    ) -> str:
        cor_span = row.locator("xpath=.//span[contains(normalize-space(),'/COR-')]")
        for index in range(cor_span.count()):
            candidate = cor_span.nth(index)
            if not candidate.is_visible():
                continue
            code_text = self._normalize_cor_code(candidate.inner_text())
            if self._cor_code_pattern().search(code_text):
                return code_text

        text = self._normalize_cor_code(row.inner_text())
        match = self._cor_code_pattern().search(text)
        if match is not None:
            return match.group(0)
        raise AssertionError(
            f"Cannot read COR code from Code column. Row text: {row.inner_text()[:200]!r}"
        )

    @log_method("Read COR code from Add/Detail form")
    def read_cor_code_from_form(self) -> str:
        selectors = [
            (
                "xpath=//label[contains(normalize-space(),'Code')]"
                "/following::span[contains(normalize-space(),'/COR-')][1]"
            ),
            (
                "xpath=//label[contains(normalize-space(),'Code')]"
                "/ancestor::div[contains(@class,'form-group') or contains(@class,'col-')][1]"
                "//span[contains(normalize-space(),'/COR-')]"
            ),
            "xpath=//*[normalize-space()='Code']/following::span[contains(normalize-space(),'/COR-')][1]",
            (
                "xpath=//input[contains(@value,'/COR-') "
                "or contains(@ng-reflect-model,'/COR-')]"
            ),
        ]
        field = self.wait_for_visible(selectors, "COR Code field on form")
        code_text = self._normalize_cor_code(
            field.input_value() if field.evaluate("el => el.tagName.toLowerCase()") == "input"
            else field.inner_text()
        )
        if not self._cor_code_pattern().search(code_text):
            raise AssertionError(f"Invalid COR code on form: {code_text!r}")
        return code_text

    @log_method("Capture COR code after Save")
    def capture_cor_code_after_save(
        self,
        route_code: str,
        *,
        tabs: list[str] | None = None,
    ) -> str:
        deadline = time.monotonic() + settings.page_load_timeout / 1000
        while time.monotonic() < deadline:
            try:
                return self.read_cor_code_from_form()
            except AssertionError:
                self.page.wait_for_timeout(settings.polling_interval)

        self.wait_for_add_modal_closed()
        self.ensure_list_page_displayed()
        self.refresh_list_page()
        return self.read_cor_code_after_save(route_code, tabs=tabs)

    @log_method("Read COR code after save from list tabs")
    def read_cor_code_after_save(
        self,
        route_code: str,
        *,
        tabs: list[str] | None = None,
    ) -> str:
        tab_candidates: list[str | None] = [None]
        for tab in tabs or ["Updating", "Draft"]:
            if tab not in tab_candidates:
                tab_candidates.append(tab)

        errors: list[str] = []
        for tab in tab_candidates:
            label = tab or "default"
            try:
                if tab:
                    self.click_list_tab(tab)
                self.search_route_on_list(route_code)
                return self.read_cor_code_from_list_row(route_code)
            except AssertionError as exc:
                errors.append(f"{label}: {exc}")
                continue

        detail = "\n".join(errors)
        raise AssertionError(
            f"Cannot read COR code for route {route_code} on tabs {tab_candidates}.\n{detail}"
        )

    @log_method("Verify COR code row is displayed on tab")
    def is_cor_code_row_displayed(self, cor_code: str) -> bool:
        code = self._normalize_cor_code(cor_code)
        self.wait_for_visible(
            self._filtered_cor_code_row_selectors(code),
            f"Cost Of Route row with COR code: {code}",
        )
        return True

    @log_method("Filter COR code on Cost Of Route list")
    def filter_cor_code(self, cor_code: str) -> "EtmsCostOfRoutePage":
        code = self._normalize_cor_code(cor_code)
        self.list_grid.wait_until_ready(
            self.list_table_selectors,
            "Cost Of Route table",
        )
        self.wait_for_page_stable()

        header = self.wait_for_visible(
            self.list_cor_code_header_selectors,
            "Cost Of Route list table Code column header",
        )
        header.scroll_into_view_if_needed()
        header.click(force=True)
        self.wait_for_page_stable()

        code_filter = self.wait_for_visible(
            self.list_cor_code_filter_selectors,
            "Cost Of Route list table Code filter input",
        )
        code_filter.scroll_into_view_if_needed()
        code_filter.click(force=True)
        code_filter.fill("")
        code_filter.fill(code)
        self.page.wait_for_timeout(settings.polling_interval)
        self.wait_for_page_stable()

        self.is_cor_code_row_displayed(code)
        return self

    @log_method("Open tab and filter COR code on Cost Of Route list")
    def open_tab_and_filter_cor_code(
        self,
        tab_name: str,
        cor_code: str,
        *,
        force: bool = True,
    ) -> "EtmsCostOfRoutePage":
        self.click_list_tab(tab_name, force=force)
        return self.filter_cor_code(cor_code)

    @log_method("Create Cost Of Route record from test data")
    def create_cost_of_route_record(self, data: dict[str, Any]) -> "EtmsCostOfRoutePage":
        self.open_via_menu_search(data["menu_search"])
        self.prepare_updating_tab_before_create(
            data["route_code"],
            tab_name=data.get("tab_updating", "Updating"),
            expected_delete_message=data.get(
                "expected_delete_message",
                "Data delete success",
            ),
        )
        self.click_add_new()
        self.choose_route(data["route_code"])
        self.fill_route_mapping_fields(data)
        self.click_generate_surcharge()
        self.click_save()
        self.wait_for_add_modal_closed()
        return self

    @log_method("Click filtered row checkbox on Cost Of Route list")
    def click_filtered_row_checkbox(self) -> "EtmsCostOfRoutePage":
        checkbox = self.wait_for_visible(
            self.list_filtered_row_checkbox_selectors,
            "Filtered row checkbox",
        )
        checkbox.scroll_into_view_if_needed()
        checkbox.click(force=True)
        self.wait_for_page_stable()
        return self

    @log_method("Tick row checkbox by COR code")
    def tick_row_checkbox_by_cor_code(self, cor_code: str) -> "EtmsCostOfRoutePage":
        row_match = self._row_match_by_cor_code(cor_code)
        list_body = self._list_portlet_body()
        checkbox = self.wait_for_visible(
            [
                f"xpath={list_body}//datatable-row-wrapper[{row_match}]//input[@type='checkbox']",
                f"xpath=//datatable-row-wrapper[{row_match}]//input[@type='checkbox']",
                f"xpath={list_body}//tr[{row_match}]//input[@type='checkbox']",
            ],
            f"Row checkbox: {cor_code}",
        )
        checkbox.scroll_into_view_if_needed()
        if not checkbox.is_checked():
            checkbox.click(force=True)
        self.wait_for_page_stable()
        return self

    @log_method("Click row action button by COR code")
    def click_row_action_btn_by_cor_code(self, cor_code: str) -> "EtmsCostOfRoutePage":
        row_wrapper = self.find_visible(self._list_row_by_cor_code_selectors(cor_code))
        if row_wrapper is not None:
            row_wrapper.scroll_into_view_if_needed()
            row_wrapper.hover()
            self.wait_for_page_stable()

        action_btn = self.wait_for_visible(
            self._row_action_btn_by_cor_code_selectors(cor_code),
            "Row action button",
        )
        action_btn.scroll_into_view_if_needed()
        action_btn.click(force=True)
        self.wait_for_page_stable()
        return self

    @log_method("Click row Send Request button")
    def click_row_send_request_button(
        self,
        route_code: str,
        vehicle_type: str | None = None,
    ) -> "EtmsCostOfRoutePage":
        self.click_row_action_btn(route_code, vehicle_type)
        send_btn = self.wait_for_visible(
            self._row_send_request_btn_selectors(route_code, vehicle_type),
            "Row Send Request icon",
        )
        send_btn.scroll_into_view_if_needed()
        send_btn.click(force=True)
        self.wait_for_page_stable()
        return self

    @log_method("Send Request on Updating tab — cancel then confirm")
    def send_request_from_updating(
        self,
        route_code: str,
        vehicle_type: str | None,
        *,
        expected_send_request_message: str,
    ) -> "EtmsCostOfRoutePage":
        self.click_row_send_request_button(route_code, vehicle_type)
        self.is_send_request_popup_displayed()
        self.click_send_request_cancel()

        self.click_row_send_request_button(route_code, vehicle_type)
        self.is_send_request_popup_displayed()
        self.click_send_request_confirm()
        self.is_success_message_displayed(expected_send_request_message)
        return self

    @log_method("Click Cancel on Request Approval popup")
    def click_send_request_cancel(self) -> "EtmsCostOfRoutePage":
        self.click_when_ready(
            self.send_request_cancel_selectors,
            "Request Approval Cancel button",
        )
        self.wait_for_page_stable()
        return self

    @log_method("Verify Request Approval popup is displayed")
    def is_send_request_popup_displayed(self) -> bool:
        self.wait_for_visible(
            self.send_request_popup_selectors,
            "Request Approval popup",
        )
        return True

    @log_method("Click Send Request on approval popup")
    def click_send_request_confirm(self) -> "EtmsCostOfRoutePage":
        self.click_when_ready(
            self.send_request_confirm_selectors,
            "Send Request confirm button",
        )
        self.wait_for_page_stable()
        return self

    @log_method("Click row Reject button")
    def click_row_reject_button(
        self,
        route_code: str,
        vehicle_type: str | None = None,
    ) -> "EtmsCostOfRoutePage":
        self.click_row_action_btn(route_code, vehicle_type)
        reject_btn = self.wait_for_visible(
            self._row_reject_btn_selectors(route_code, vehicle_type),
            "Row Reject button",
        )
        reject_btn.scroll_into_view_if_needed()
        reject_btn.click(force=True)
        self.wait_for_page_stable()
        return self

    @log_method("Click row Reject button by COR code")
    def click_row_reject_button_by_cor_code(self, cor_code: str) -> "EtmsCostOfRoutePage":
        self.click_row_action_btn_by_cor_code(cor_code)
        reject_btn = self.wait_for_visible(
            self._row_reject_btn_by_cor_code_selectors(cor_code),
            "Row Reject button",
        )
        reject_btn.scroll_into_view_if_needed()
        reject_btn.click(force=True)
        self.wait_for_page_stable()
        return self

    @log_method("Verify reject confirmation popup is displayed")
    def is_reject_confirm_displayed(
        self,
        message: str | None = None,
    ) -> bool:
        expected = message or self.reject_confirm_message
        self.wait_for_visible(
            self._swal_paragraph_selectors(expected),
            f"Reject confirmation popup: {expected}",
        )
        return True

    @log_method("Fill reject reason and confirm")
    def fill_reject_reason_and_confirm(self, reason: str) -> "EtmsCostOfRoutePage":
        reason_input = self.wait_for_visible(
            self.reject_reason_input_selectors,
            "Reject reason input",
        )
        reason_input.click()
        reason_input.fill(reason)
        return self.click_swal_ok()

    @log_method("Reject Cost Of Route on Pending tab")
    def reject_cost_of_route_on_pending(
        self,
        data: dict[str, Any],
        cor_code: str,
        *,
        cancel_first: bool = True,
    ) -> "EtmsCostOfRoutePage":
        route_code = data["route_code"]
        vehicle_type = data.get("vehicle_type")
        confirm_message = data["expected_reject_confirm_message"]
        self.open_tab_and_filter_cor_code(data["tab_pending"], cor_code)
        if cancel_first:
            self.click_row_reject_button(route_code, vehicle_type)
            self.is_reject_confirm_displayed(confirm_message)
            self.click_swal_cancel()
        self.click_row_reject_button(route_code, vehicle_type)
        self.is_reject_confirm_displayed(confirm_message)
        self.fill_reject_reason_and_confirm(data["reject_reason"])
        self.is_success_message_displayed(data["expected_reject_success_message"])
        return self

    @log_method("Switch To Updating from Rejected tab")
    def switch_to_updating_from_rejected(
        self,
        data: dict[str, Any],
        cor_code: str,
        *,
        cancel_first: bool = True,
    ) -> "EtmsCostOfRoutePage":
        confirm_message = data["expected_switch_confirm_message"]
        self.open_tab_and_filter_cor_code(data["tab_rejected"], cor_code)
        self.click_filtered_row_checkbox()
        if cancel_first:
            self.click_switch_to_updating_button()
            self.is_switch_to_updating_confirm_displayed(confirm_message)
            self.click_swal_cancel()
        self.click_switch_to_updating_button()
        self.is_switch_to_updating_confirm_displayed(confirm_message)
        self.click_swal_ok()
        self.is_success_message_displayed(data["expected_switch_success_message"])
        return self

    @log_method("Click Switch To Updating toolbar button")
    def click_switch_to_updating_button(self) -> "EtmsCostOfRoutePage":
        self.click_when_ready(
            self.switch_to_updating_button_selectors,
            "Switch To Updating button",
        )
        self.wait_for_page_stable()
        return self

    @log_method("Verify Switch To Updating confirmation popup is displayed")
    def is_switch_to_updating_confirm_displayed(
        self,
        message: str | None = None,
    ) -> bool:
        expected = message or self.switch_to_updating_confirm_message
        self.wait_for_visible(
            self._swal_paragraph_selectors(expected),
            f"Switch To Updating confirmation popup: {expected}",
        )
        return True

    @log_method("Delete Cost Of Route by COR code")
    def delete_cost_of_route_by_cor_code(
        self,
        cor_code: str,
        expected_delete_message: str,
    ) -> "EtmsCostOfRoutePage":
        self.click_row_action_btn_by_cor_code(cor_code)
        self.click_row_delete_button_by_cor_code(cor_code)
        self.is_delete_confirm_displayed()
        self.click_delete_confirm_ok()
        self.is_success_message_displayed(expected_delete_message)
        return self

    @log_method("Click row Delete button by COR code")
    def click_row_delete_button_by_cor_code(self, cor_code: str) -> "EtmsCostOfRoutePage":
        delete_btn = self.wait_for_visible(
            self._row_delete_btn_by_cor_code_selectors(cor_code),
            "Row Delete button",
        )
        delete_btn.scroll_into_view_if_needed()
        delete_btn.click(force=True)
        self.wait_for_page_stable()
        return self

    _cleanup_tabs = ("Updating", "Draft", "Pending", "Rejected", "Accepted")

    def _try_delete_record_on_tab(
        self,
        tab: str,
        *,
        cor_code: str | None = None,
        route_code: str | None = None,
        vehicle_type: str | None = None,
        expected_delete_message: str,
    ) -> bool:
        try:
            self.click_list_tab(tab, force=True)
        except Exception as exc:
            logger.warning("Cleanup cannot open tab {}: {}", tab, exc)
            return False

        if cor_code:
            try:
                code = self._normalize_cor_code(cor_code)
                self.filter_cor_code(code)
                self.delete_cost_of_route_by_cor_code(code, expected_delete_message)
                return True
            except Exception as exc:
                logger.warning(
                    "Cleanup by cor_code on tab {} failed: {}",
                    tab,
                    exc,
                )

        if route_code and self._has_route_row(route_code, vehicle_type):
            try:
                self._fill_route_code_filter(
                    self.list_route_code_filter_selectors,
                    route_code,
                    f"Cleanup Route Code filter on tab '{tab}'",
                )
                self.wait_for_page_stable()
                self.delete_cost_of_route(
                    route_code,
                    expected_delete_message,
                    vehicle_type,
                )
                return True
            except Exception as exc:
                logger.warning(
                    "Cleanup by route on tab {} failed: {}",
                    tab,
                    exc,
                )

        return False

    @log_method("Cleanup orphan Cost Of Route records by route before test")
    def cleanup_orphan_records_by_route(
        self,
        route_code: str,
        vehicle_type: str | None = None,
        *,
        menu_search: str = "Cost Of Route",
        expected_delete_message: str = "Data delete success",
        tabs: list[str] | None = None,
    ) -> None:
        """Remove leftover records from prior failed runs (same route + vehicle)."""
        self.cleanup_created_record(
            menu_search=menu_search,
            expected_delete_message=expected_delete_message,
            route_code=route_code,
            vehicle_type=vehicle_type,
            tabs=tabs,
        )

    @log_method("Cleanup created Cost Of Route record if test failed")
    def cleanup_created_record(
        self,
        *,
        menu_search: str = "Cost Of Route",
        expected_delete_message: str = "Data delete success",
        cor_code: str | None = None,
        route_code: str | None = None,
        vehicle_type: str | None = None,
        tabs: list[str] | None = None,
    ) -> None:
        if not cor_code and not route_code:
            logger.warning("Cleanup skipped: no cor_code or route_code provided")
            return

        try:
            self.ensure_list_page_displayed(menu_search)
        except Exception as exc:
            logger.warning("Cleanup skipped — cannot open list page: {}", exc)
            return

        for tab in tabs or list(self._cleanup_tabs):
            if self._try_delete_record_on_tab(
                tab,
                cor_code=cor_code,
                route_code=route_code,
                vehicle_type=vehicle_type,
                expected_delete_message=expected_delete_message,
            ):
                logger.info(
                    "Cleanup deleted Cost Of Route on tab {} (cor_code={}, route_code={})",
                    tab,
                    cor_code,
                    route_code,
                )
                return

        logger.warning(
            "Cleanup could not delete record cor_code={} route_code={} vehicle_type={}",
            cor_code,
            route_code,
            vehicle_type,
        )
