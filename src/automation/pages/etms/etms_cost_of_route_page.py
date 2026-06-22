from __future__ import annotations

import time
from typing import Any

from automation.config import settings
from automation.logging import log_method
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
        "xpath=//th[contains(normalize-space(),'Route')]",
        "xpath=//div[contains(@class,'datatable-header-cell') and contains(.,'Route')]",
        "xpath=//table//th",
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

    @log_method("Search route code in Choose Route popup filter")
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
        self.wait_for_page_stable()
        return self

    def _success_message_selectors(self, message: str) -> list[str]:
        return [
            f"#toast-container .toast-message:has-text('{message}')",
            f"#toast-container *:has-text('{message}')",
            f".toast:has-text('{message}')",
            f"xpath=//*[contains(@class,'toast') and contains(.,'{message}')]",
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

    @log_method("Wait for save completed")
    def wait_for_add_modal_closed(self) -> "EtmsCostOfRoutePage":
        deadline = time.monotonic() + settings.page_load_timeout / 1000
        while time.monotonic() < deadline:
            if self.modify_page_hash not in self.current_url.lower().replace("_", "-"):
                self.wait_for_page_stable()
                return self
            modal = self.page.locator(
                "xpath=//div[contains(@class,'modal') and contains(@class,'show')]"
                "[.//*[contains(normalize-space(),'Add New Cost Of Route')]]"
            )
            if modal.count() == 0 or not modal.first.is_visible():
                self.wait_for_page_stable()
                return self
            self.page.wait_for_timeout(settings.polling_interval)
        self.wait_for_page_stable()
        return self

    def _list_portlet_body(self) -> str:
        return (
            "//*[contains(@class,'page-title') and contains(normalize-space(),'Cost Of Route')]"
            "/ancestor::div[contains(@class,'m-portlet') or contains(@class,'portlet')][1]"
            "//div[contains(@class,'m-portlet__body') or contains(@class,'portlet__body')]"
        )

    def _is_on_list_page(self) -> bool:
        url = self.current_url.lower().replace("_", "-")
        return (
            self.list_page_hash in url
            and self.modify_page_hash not in url
        )

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
        code_filter.press("Enter")
        self.wait_for_page_stable()

    def _list_route_row_selectors(self, route_code: str) -> list[str]:
        list_body = self._list_portlet_body()
        return [
            f"xpath={list_body}//tr[contains(.,'{route_code}') and not(contains(@class,'filter-row'))]",
            f"xpath={list_body}//datatable-body-row[contains(.,'{route_code}')]",
            f"xpath=//tr[contains(.,'{route_code}') and not(contains(@class,'filter-row'))]",
        ]

    def _row_action_btn_selectors(
        self,
        route_code: str,
        vehicle_type: str | None = None,
    ) -> list[str]:
        row_predicates = [f"contains(.,'{route_code}')"]
        if vehicle_type:
            row_predicates.append(f"contains(.,'{vehicle_type}')")
        row_match = " and ".join(row_predicates)
        list_body = self._list_portlet_body()
        return [
            f"xpath={list_body}//tr[{row_match} and not(contains(@class,'filter-row'))]//*[contains(@class,'action-btn')]",
            f"xpath={list_body}//datatable-body-row[{row_match}]//*[contains(@class,'action-btn')]",
            f"xpath=//table//tbody//tr[{row_match} and not(contains(@class,'filter-row'))]//*[contains(@class,'action-btn')]",
            f"xpath=//datatable-body-row[{row_match}]//*[contains(@class,'action-btn')]",
            (
                f"xpath=//tr[{row_match} and not(contains(@class,'filter-row'))]"
                "//*[contains(@class,'action-btn')]"
            ),
            f"xpath={list_body}//tr[td and not(contains(@class,'filter-row'))]//*[contains(@class,'action-btn')]",
            "[class*='action-btn']",
        ]

    @log_method("Search Route Code on Cost Of Route list filter")
    def search_route_on_list(self, route_code: str) -> "EtmsCostOfRoutePage":
        self.is_list_page_displayed()
        self._fill_route_code_filter(
            self.list_route_code_filter_selectors,
            route_code,
            "Cost Of Route list Route Code filter input",
        )
        self.wait_for_visible(
            self._list_route_row_selectors(route_code),
            f"Cost Of Route list row: {route_code}",
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
        if not self._is_on_list_page():
            self.open_via_menu_search(menu_text)
        self.is_list_page_displayed()
        return self

    @log_method("Click row action button on list grid")
    def click_row_action_btn(
        self,
        route_code: str,
        vehicle_type: str | None = None,
    ) -> "EtmsCostOfRoutePage":
        action_btn = self.wait_for_visible(
            self._row_action_btn_selectors(route_code, vehicle_type),
            "Row action button",
        )
        action_btn.scroll_into_view_if_needed()
        action_btn.click(force=True)
        self.wait_for_page_stable()
        return self

    def _row_delete_btn_selectors(
        self,
        route_code: str,
        vehicle_type: str | None = None,
    ) -> list[str]:
        row_predicates = [f"contains(.,'{route_code}')"]
        if vehicle_type:
            row_predicates.append(f"contains(.,'{vehicle_type}')")
        row_match = " and ".join(row_predicates)
        list_body = self._list_portlet_body()
        row_delete = (
            "//a[@title='Delete' and contains(@class,'btn-ftl-icon') "
            "and contains(@class,'text-danger')]"
        )
        row_delete_by_id = "//a[contains(@id,'btnButtonRowDelete')]"
        return [
            f"xpath={list_body}//tr[{row_match} and not(contains(@class,'filter-row'))]{row_delete_by_id}",
            f"xpath={list_body}//tr[{row_match} and not(contains(@class,'filter-row'))]{row_delete}",
            f"xpath=//tr[{row_match} and not(contains(@class,'filter-row'))]{row_delete_by_id}",
            f"xpath=//tr[{row_match} and not(contains(@class,'filter-row'))]{row_delete}",
            f"xpath={list_body}//tr[td and not(contains(@class,'filter-row'))]{row_delete_by_id}",
            *self.delete_action_selectors,
        ]

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
