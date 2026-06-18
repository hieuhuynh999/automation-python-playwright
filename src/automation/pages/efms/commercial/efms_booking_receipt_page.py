from __future__ import annotations

import re
import time
from datetime import date
from typing import Any

from automation.config import settings
from automation.logging import log_method
from automation.pages.efms.commercial.commercial_menu_page import EfmsCommercialMenuPage


class EfmsBookingReceiptPage(EfmsCommercialMenuPage):
    menu_selectors = [
        "xpath=//div[contains(@class,'m-menu__submenu')]//a[contains(@href,'commercial/booking-receipt')]",
        "xpath=//li[contains(@class,'m-menu__item--open')]//div[contains(@class,'m-menu__submenu')]//a[.//span[normalize-space()='Booking Receipt']]",
        "xpath=//div[contains(@class,'m-menu__submenu')]//span[normalize-space()='Booking Receipt']",
        "xpath=//span[normalize-space()='Booking Receipt']",
    ]

    list_title_selectors = [
        "xpath=//h3[normalize-space()='Booking Receipt']",
        "h3:has-text('Booking Receipt')",
    ]

    list_table_selectors = [
        "xpath=//th[normalize-space()='Booking No']",
        "th:has-text('Booking No')",
    ]

    add_new_button_selectors = [
        "button:has-text('Add new')",
        "button:has-text('add new')",
        "xpath=//button[contains(.,'Add new')]",
        "xpath=//button[contains(.,'add new')]",
    ]

    add_form_title_selectors = [
        "xpath=//h3[contains(normalize-space(),'Add New Booking Receipt')]",
        "h3:has-text('Add New Booking Receipt')",
        "xpath=//*[contains(normalize-space(),'Add New Booking Receipt')]",
    ]

    detail_title_selectors = [
        "xpath=//h3[contains(normalize-space(),'Detail Booking Receipt')]",
        "h3:has-text('Detail Booking Receipt')",
        "xpath=//*[contains(normalize-space(),'Detail Booking Receipt')]",
    ]

    save_button_selectors = [
        "button:has-text('Save')",
        "xpath=//button[normalize-space()='Save']",
    ]

    delete_button_selectors = [
        (
            "xpath=//*[contains(@class,'m-portlet__head')]"
            "//button[contains(@class,'btn-outline-danger') and .//i[contains(@class,'la-trash')]]"
        ),
        "button.btn-outline-danger:has(i.la-trash)",
    ]

    delete_confirm_popup_selectors = [
        "xpath=//h5[text()='Delete Booking Receipt ']//ancestor::div",
        "xpath=//div[contains(@class,'swal2-popup') and .//h2[contains(.,'Delete Booking Receipt')]]",
        ".swal2-popup:has(.swal2-title:has-text('Delete Booking Receipt'))",
    ]

    delete_confirm_yes_selectors = [
        "xpath=//h5[text()='Delete Booking Receipt ']//ancestor::div//span[text()=' Yes ']",
        (
            "xpath=//div[contains(@class,'swal2-popup') and .//h2[contains(.,'Delete Booking Receipt')]]"
            "//button[contains(@class,'swal2-confirm')]"
        ),
        ".swal2-popup:has(.swal2-title:has-text('Delete Booking Receipt')) .swal2-confirm",
    ]

    yes_button_selectors = [
        ".swal2-confirm",
        "button:has-text('Yes')",
        "[aria-label='Yes']",
        "xpath=//button[normalize-space()='Yes']",
    ]

    loading_overlay_selectors = [
        ".m-blockui",
        ".block-ui-wrapper.block-ui-active",
        "xpath=//div[contains(@class,'block-ui') and contains(@class,'active')]",
        "xpath=//div[contains(@class,'loading-mask')]",
    ]

    def _is_booking_receipt_delete_response(self, response) -> bool:
        url = response.url.lower()
        normalized = url.replace("-", "")
        if "bookingreceipt" not in normalized and "booking/receipt" not in url:
            return False
        if response.request.method == "DELETE":
            return response.status in (200, 204)
        if response.request.method in ("POST", "PUT"):
            return response.status in (200, 204) and "delete" in url
        return False

    def _wait_delete_confirm_popup_closed(self, timeout: int | None = None) -> None:
        timeout = timeout or settings.page_load_timeout
        try:
            self.page.wait_for_function(
                "() => !document.querySelector('.swal2-popup')",
                timeout=timeout,
            )
            return
        except Exception:
            pass

        deadline = time.monotonic() + timeout / 1000
        while time.monotonic() < deadline:
            if self.find_visible(self.delete_confirm_popup_selectors) is None:
                return
            self.page.wait_for_timeout(settings.polling_interval)

    def _wait_for_grid_ready(self, timeout: int | None = None) -> None:
        timeout = timeout or settings.browser_timeout
        deadline = time.monotonic() + timeout / 1000
        while time.monotonic() < deadline:
            overlay = self.find_visible(self.loading_overlay_selectors)
            table = self.find_visible(self.list_table_selectors)
            if overlay is None and table is not None:
                return
            self.page.wait_for_timeout(settings.polling_interval)
        self.wait_for_page_stable()

    def _click_delete_confirm_yes_and_wait(
        self,
        expected_message: str | None = None,
    ) -> EfmsBookingReceiptPage:
        popup_timeout = settings.page_load_timeout
        self.wait_for_visible(
            self.delete_confirm_popup_selectors,
            "Delete Booking Receipt confirm popup",
            timeout=popup_timeout,
        )
        yes_btn = self._wait_actionable(
            self.delete_confirm_yes_selectors,
            "Yes on Delete Booking Receipt popup",
            timeout=popup_timeout,
        )
        try:
            with self.page.expect_response(
                self._is_booking_receipt_delete_response,
                timeout=popup_timeout,
            ):
                yes_btn.click(force=True)
        except Exception:
            yes_btn.click(force=True)

        self._wait_delete_confirm_popup_closed(timeout=popup_timeout)
        self._wait_for_grid_ready(timeout=popup_timeout)
        if expected_message:
            self.is_message_displayed(expected_message)
        else:
            self.wait_for_page_stable()
        return self

    @log_method("Search Booking Receipt")
    def search_booking(self, booking_no: str) -> EfmsBookingReceiptPage:
        row_selectors = [
            f"xpath=//span[normalize-space()='{booking_no}']",
            f"xpath=//td[contains(.,'{booking_no}')]",
        ]
        self.wait_for_visible(row_selectors, f"Booking Receipt row: {booking_no}")
        return self

    @log_method("Refresh Booking Receipt list page")
    def refresh_list_page(self) -> EfmsBookingReceiptPage:
        self.page.reload(wait_until="domcontentloaded")
        self.wait_for_page_stable()
        try:
            self.page.wait_for_load_state(
                "networkidle",
                timeout=min(15000, settings.page_load_timeout),
            )
        except Exception:
            pass
        self._wait_for_grid_ready(timeout=settings.page_load_timeout)
        assert self.is_booking_receipt_displayed()
        return self

    @log_method("Open Booking Receipt list page")
    def open_list_page(self) -> EfmsBookingReceiptPage:
        base = settings.efms_base_url.rstrip("/")
        self.open_url(f"{base}/en/#/home/commercial/booking-receipt")
        assert self.is_booking_receipt_displayed()
        return self

    @log_method("Click Booking Receipt Menu")
    def click_booking_receipt_menu(self) -> EfmsBookingReceiptPage:
        self._click_commercial_submenu(
            self.menu_selectors,
            "/home/commercial/booking-receipt",
        )
        return self

    @log_method("Verify Booking Receipt is displayed")
    def is_booking_receipt_displayed(self) -> bool:
        return self._is_page_displayed(
            "#/home/commercial/booking-receipt",
            self.list_title_selectors,
            self.list_table_selectors,
            "Booking Receipt title",
            "Booking Receipt table",
        )

    @log_method("Click Add new button")
    def click_add_new(self) -> EfmsBookingReceiptPage:
        self.wait_for_visible(self.add_new_button_selectors, "Add new button").click(force=True)
        return self

    @log_method("Click Add new option")
    def click_add_new_option(self, option: str) -> EfmsBookingReceiptPage:
        option_selectors = [
            f"a.dropdown-item:has-text('{option}')",
            f"xpath=//div[contains(@class,'dropdown-menu-wrapper')]//a[contains(normalize-space(),'{option}')]",
            f"xpath=//a[@title='Create Booking Receipt' and contains(.,'{option}')]",
            f"xpath=//div[contains(@class,'cdk-overlay-pane')]//a[contains(.,'{option}')]",
        ]
        if not self.find_visible(option_selectors):
            self.wait_for_visible(self.add_new_button_selectors, "Add new button").click(force=True)
        self.wait_for_visible(option_selectors, f"Add new option: {option}").click(force=True)
        self.wait_for_page_stable()
        return self

    @log_method("Verify Add New Booking Receipt form is displayed")
    def is_add_form_displayed(self) -> bool:
        self.wait_for_visible(
            self.add_form_title_selectors,
            "Add New Booking Receipt form",
            timeout=settings.page_load_timeout,
        )
        return True

    @log_method("Verify Detail Booking Receipt is displayed")
    def is_detail_displayed(self) -> bool:
        self.wait_for_visible(
            self.detail_title_selectors,
            "Detail Booking Receipt page",
            timeout=settings.page_load_timeout,
        )
        return True

    def _resolve_date_value(self, value: str) -> str:
        if str(value).strip().upper() == "TODAY":
            return date.today().strftime("%d/%m/%Y")
        return str(value)

    @log_method("Fill date field")
    def fill_date_field(self, label: str, value: str) -> EfmsBookingReceiptPage:
        resolved = self._resolve_date_value(value)
        container = self._field_container(label)
        field = container.locator(
            "input[formcontrolname='bookingDate'], input[name='daterange'], input"
        ).first
        field.click(force=True)
        field.evaluate(
            """(el, val) => {
                el.removeAttribute('readonly');
                el.value = val;
                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
                el.dispatchEvent(new Event('blur', { bubbles: true }));
            }""",
            resolved,
        )
        self.page.keyboard.press("Escape")
        return self

    def _field_container(self, label: str):
        return self.page.locator(
            "xpath="
            f"//label[contains(normalize-space(),'{label}')]"
            "/ancestor::div[contains(@class,'col-lg')][1]"
        ).first

    @log_method("Select combogrid field")
    def select_combogrid_field(self, label: str, value: str) -> EfmsBookingReceiptPage:
        self.page.keyboard.press("Escape")

        container = self._field_container(label)
        search_selectors = [
            (
                "xpath=//label[contains(normalize-space(),'"
                f"{label}"
                "')]/ancestor::div[contains(@class,'col-lg')][1]"
                "//input[contains(@class,'cbgr-input-search')]"
            ),
            ".e--combogrid.show input.cbgr-input-search",
        ]

        search = None
        for attempt in range(2):
            container.locator("input.dropdown-toggle").first.click(force=True)
            try:
                search = self.wait_for_visible(
                    search_selectors,
                    f"{label} combogrid search",
                    timeout=15000,
                )
                break
            except AssertionError:
                if attempt == 1:
                    raise
                self.page.keyboard.press("Escape")

        assert search is not None
        search.click()
        search.fill(value)

        dropdown = container.locator(".dropdown-menu.e--combogrid-content")
        if dropdown.locator("table tbody tr").count() == 0:
            dropdown = self.page.locator(
                ".e--combogrid.show .dropdown-menu.e--combogrid-content"
            ).last

        row = dropdown.locator("table tbody tr").filter(has_text=value).first
        deadline = time.monotonic() + settings.browser_timeout / 1000
        while time.monotonic() < deadline:
            if row.count() > 0:
                row.click(force=True)
                self.page.keyboard.press("Escape")
                self.wait_for_page_stable()
                return self
            self.page.wait_for_timeout(settings.polling_interval)

        raise AssertionError(
            f"Element '{label} option: {value}' not found in combogrid "
            f"after {settings.browser_timeout}ms."
        )

    @log_method("Select dropdown field")
    def select_dropdown_field(self, label: str, value: str) -> EfmsBookingReceiptPage:
        container = self._field_container(label)

        if container.locator("app-combo-grid-virtual-scroll").count() > 0:
            return self.select_combogrid_field(label, value)

        ng_select = container.locator("ng-select").first
        if ng_select.count() > 0:
            ng_select.click()
            input_el = ng_select.locator("input").first
            if input_el.count() > 0:
                input_el.fill(value)
            option_selectors = [
                f"ng-dropdown-panel .ng-option:has-text('{value}')",
                f"xpath=//ng-dropdown-panel//*[contains(normalize-space(),'{value}')]",
            ]
            self.wait_for_visible(option_selectors, f"{label} option: {value}").click(force=True)
            self.wait_for_page_stable()
            return self

        select_el = container.locator("select").first
        if select_el.count() > 0:
            select_el.select_option(label=value)
            return self

        input_selectors = [
            (
                "xpath=//label[contains(normalize-space(),'"
                f"{label}"
                "')]/ancestor::div[contains(@class,'col-lg')][1]"
                "//input[not(contains(@class,'dropdown-toggle'))]"
            ),
            f"xpath=//label[contains(.,'{label}')]/following::input[1]",
            f"xpath=//*[contains(normalize-space(),'{label}')]/following::input[1]",
        ]
        field = self.wait_for_visible(input_selectors, f"{label} input")
        field.click()
        field.fill(value)
        option_selectors = [
            f"xpath=//*[contains(@class,'dropdown-menu')]//*[contains(.,'{value}')]",
            f"xpath=//*[contains(@class,'autocomplete')]//*[contains(.,'{value}')]",
            f"text={value}",
        ]
        if self.find_visible(option_selectors):
            self.wait_for_visible(option_selectors, f"{label} suggestion: {value}").click(
                force=True
            )
        self.wait_for_page_stable()
        return self

    @log_method("Fill input field")
    def fill_input_field(self, label: str, value: str) -> EfmsBookingReceiptPage:
        input_selectors = [
            (
                "xpath=//label[contains(normalize-space(),'"
                f"{label}"
                "')]/ancestor::div[contains(@class,'col-lg')][1]"
                "//input[not(contains(@class,'dropdown-toggle'))]"
            ),
            f"xpath=//label[contains(.,'{label}')]/following::input[1]",
            f"xpath=//*[contains(normalize-space(),'{label}')]/following::input[1]",
            f"xpath=//input[@formcontrolname and contains(@placeholder,'{label}')]",
        ]
        field = self.wait_for_visible(input_selectors, f"{label} input")
        field.click()
        field.fill(str(value))
        return self

    @log_method("Fill Booking Receipt create form")
    def fill_create_form(self, data: dict[str, Any]) -> EfmsBookingReceiptPage:
        self.select_dropdown_field("Customer/Payer", data["customer_payer"])
        self.select_dropdown_field("Salesman", data["salesman"])
        self.fill_date_field("Booking Date", str(data["booking_date"]))
        self.select_dropdown_field("Shipment Type", data["shipment_type"])
        self.select_dropdown_field("Departure Location", data["departure_location"])
        self.select_dropdown_field("Arrival Location", data["arrival_location"])
        self.select_dropdown_field("Shipper", data["shipper"])
        self.fill_input_field("Weight", data["weight"])
        self.fill_input_field("Package Qty", data["package_qty"])
        return self

    @log_method("Fill Booking Receipt update form")
    def fill_update_form(self, data: dict[str, Any]) -> EfmsBookingReceiptPage:
        self.select_dropdown_field("Incoterm", data["incoterm"])
        self.select_dropdown_field("Shipper", data["shipper"])
        self.select_dropdown_field("Commodities", data["commodities"])
        self.fill_input_field("CBM", data["cbm"])
        return self

    @log_method("Click Save button")
    def click_save(self) -> EfmsBookingReceiptPage:
        self.wait_for_visible(self.save_button_selectors, "Save button").click(force=True)
        self.wait_for_page_stable()
        return self

    @log_method("Click Yes on confirm popup")
    def click_confirm_yes(self) -> EfmsBookingReceiptPage:
        self.wait_for_visible(self.yes_button_selectors, "Yes confirm button").click(force=True)
        return self

    def _toolbar_delete_selectors(self) -> list[str]:
        return list(self.delete_button_selectors)

    def _row_delete_selectors(self, booking_no: str) -> list[str]:
        return [
            (
                "xpath=//tr[.//span[normalize-space()='"
                f"{booking_no}"
                "']]//app-permission-button[@type='delete']"
            ),
            (
                "xpath=//span[normalize-space()='"
                f"{booking_no}"
                "']//preceding::td//app-permission-button[@type='delete']"
            ),
        ]

    def _delete_button_selectors(self, booking_no: str) -> list[str]:
        return self._toolbar_delete_selectors() + self._row_delete_selectors(booking_no)

    def _wait_toolbar_delete_ready(self, timeout: int | None = None):
        return self._wait_actionable(
            self._toolbar_delete_selectors(),
            "Toolbar Delete button",
            timeout=timeout or settings.page_load_timeout,
            stable_checks=3,
        )

    def _click_delete_for_booking(self, booking_no: str) -> None:
        popup_timeout = settings.page_load_timeout
        toolbar = self._wait_toolbar_delete_ready(timeout=popup_timeout)
        toolbar.click(force=True)
        self.wait_for_visible(
            self.delete_confirm_popup_selectors,
            "Delete Booking Receipt confirm popup",
            timeout=popup_timeout,
        )

    def _wait_actionable(
        self,
        selectors: list[str],
        element_name: str,
        timeout: int | None = None,
        stable_checks: int = 3,
    ):
        timeout = timeout or settings.browser_timeout
        deadline = time.monotonic() + timeout / 1000
        consecutive = 0
        while time.monotonic() < deadline:
            locator = self.find_visible(selectors)
            if locator is not None:
                try:
                    if locator.is_enabled():
                        consecutive += 1
                        if consecutive >= stable_checks:
                            return locator
                    else:
                        consecutive = 0
                except Exception:
                    consecutive = 0
            else:
                consecutive = 0
            self.page.wait_for_timeout(settings.polling_interval)
        raise AssertionError(
            self._build_wait_error(element_name, selectors, timeout)
            + " (element not actionable/stable)"
        )

    @log_method("Delete Booking Receipt from grid (stable)")
    def delete_booking_receipt_from_grid(
        self, booking_no: str, expected_message: str
    ) -> EfmsBookingReceiptPage:
        row_selectors = [
            f"xpath=//tr[.//span[normalize-space()='{booking_no}']]",
            f"xpath=//tr[.//a[normalize-space()='{booking_no}']]",
        ]

        self.wait_for_page_stable()
        self.search_booking(booking_no)
        self._wait_actionable(row_selectors, f"Booking row: {booking_no}")

        self.select_booking_row(booking_no)
        self._wait_for_grid_ready(timeout=settings.page_load_timeout)
        self._wait_toolbar_delete_ready(timeout=settings.page_load_timeout)

        self._click_delete_for_booking(booking_no)
        self._click_delete_confirm_yes_and_wait(expected_message)

        if not self.wait_until_booking_absent(booking_no, timeout=settings.page_load_timeout):
            raise AssertionError(
                f"Booking {booking_no} still visible after delete. "
                f"row='{self.get_booking_row_text(booking_no)}'"
            )
        return self

    @log_method("Click Yes on Delete Booking Receipt popup")
    def click_delete_confirm_yes(
        self, expected_message: str | None = None
    ) -> EfmsBookingReceiptPage:
        popup_timeout = settings.page_load_timeout
        try:
            self._click_delete_confirm_yes_and_wait(expected_message)
        except AssertionError:
            # Some environments show a generic confirm dialog without the expected title.
            self.click_confirm_yes()
            self._wait_delete_confirm_popup_closed(timeout=popup_timeout)
            self._wait_for_grid_ready(timeout=popup_timeout)
            if expected_message:
                self.is_message_displayed(expected_message)
            else:
                self.wait_for_page_stable()
        return self

    @log_method("Verify system message is displayed")
    def is_message_displayed(self, message: str) -> bool:
        message_selectors = [
            f"#toast-container .toast-message:has-text('{message}')",
            f"#toast-container *:has-text('{message}')",
            f"xpath=//*[contains(@class,'toast') and contains(.,'{message}')]",
            f"xpath=//*[contains(@class,'alert') and contains(.,'{message}')]",
            f".swal2-html-container:has-text('{message}')",
            f"xpath=//*[contains(normalize-space(),'{message}')]",
        ]
        self.wait_for_visible(
            message_selectors,
            f"System message: {message}",
            timeout=15000,
        )
        return True

    @log_method("Get latest system message")
    def get_latest_system_message(self) -> str:
        message_selectors = [
            "#toast-container .toast-message",
            ".swal2-html-container",
            "xpath=//*[contains(@class,'toast-message')]",
            "xpath=//*[contains(@class,'swal2-html-container')]",
        ]
        locator = self.find_visible(message_selectors)
        if locator is None:
            return ""
        return " ".join(locator.inner_text().split()).strip()

    @log_method("Click Booking No link")
    def click_booking_no(self, booking_no: str) -> EfmsBookingReceiptPage:
        booking_link_selectors = [
            f"xpath=//span[normalize-space()='{booking_no}']",
            f"xpath=//a[normalize-space()='{booking_no}']",
            f"xpath=//td[contains(.,'{booking_no}')]//span",
            f"xpath=//td[contains(.,'{booking_no}')]//a",
        ]
        self.wait_for_visible(booking_link_selectors, f"Booking No: {booking_no}").click(force=True)
        self.wait_for_page_stable()
        return self

    @log_method("Get Booking No from current page")
    def get_booking_no_from_current_view(self) -> str | None:
        value_selectors = [
            "input[formcontrolname='bookingNo']",
            "input[name='bookingNo']",
            "xpath=//label[contains(normalize-space(),'Booking No')]/following::input[1]",
            "xpath=//*[contains(normalize-space(),'Booking No')]/following::span[1]",
        ]
        for selector in value_selectors:
            locator = self.page.locator(selector).first
            try:
                if locator.count() == 0:
                    continue
                value = (locator.input_value() or "").strip()
                if not value:
                    value = (locator.inner_text() or "").strip()
                match = re.search(r"BK[A-Z]{2}\d+", value)
                if match:
                    return match.group(0)
            except Exception:
                continue

        url_match = re.search(
            r"booking-receipt/(?:detail/)?([A-Z]{2,}\d+)",
            self.current_url,
        )
        if url_match:
            return url_match.group(1)
        return None

    @log_method("Get Booking No from grid row containing text")
    def get_booking_no_from_grid_row_containing(self, text: str) -> str | None:
        row_selectors = [
            f"xpath=//table//tbody//tr[contains(.,'{text}')]",
            f"xpath=//tr[contains(.,'{text}')]",
        ]
        row = self.find_visible(row_selectors)
        if row is None:
            return None
        match = re.search(r"BK[A-Z]{2}\d+", row.inner_text())
        return match.group(0) if match else None

    @log_method("Get first Booking No from grid")
    def get_first_booking_no_from_grid(self) -> str:
        booking_cell_selectors = [
            "xpath=//table//tbody//td//span[starts-with(normalize-space(),'BK')]",
            "xpath=//td//span[starts-with(normalize-space(),'BK')]",
            "xpath=//span[starts-with(normalize-space(),'BKAE')]",
            "xpath=//table//tbody/tr[1]//td[1]//a",
            "xpath=//table//tbody/tr[1]//td[1]",
        ]
        cell = self.wait_for_visible(
            booking_cell_selectors,
            "First Booking No in grid",
            timeout=settings.page_load_timeout,
        )
        match = re.search(r"BK[A-Z]{2}\d+", cell.inner_text())
        return match.group(0) if match else cell.inner_text().strip()

    @log_method("Select Booking Receipt row in grid")
    def select_booking_row(self, booking_no: str) -> EfmsBookingReceiptPage:
        row_checkbox_selectors = [
            f"xpath=//tr[.//span[normalize-space()='{booking_no}']]//input[@type='checkbox']",
            f"xpath=//tr[.//a[normalize-space()='{booking_no}']]//input[@type='checkbox']",
            f"xpath=//*[contains(.,'{booking_no}')]/ancestor::tr[1]//input[@type='checkbox']",
            f"xpath=//*[contains(.,'{booking_no}')]/ancestor::datatable-row-wrapper[1]//input[@type='checkbox']",
        ]
        row_selectors = [
            f"xpath=//tr[.//span[normalize-space()='{booking_no}']]",
            f"xpath=//tr[.//a[normalize-space()='{booking_no}']]",
        ]

        self._wait_for_grid_ready(timeout=settings.page_load_timeout)
        checkbox = self.wait_for_visible(
            row_checkbox_selectors,
            f"Row checkbox for {booking_no}",
        )

        deadline = time.monotonic() + settings.page_load_timeout / 1000
        while time.monotonic() < deadline:
            toolbar = self.find_visible(self._toolbar_delete_selectors())
            if toolbar is not None:
                try:
                    if toolbar.is_enabled():
                        return self
                except Exception:
                    pass

            if not checkbox.is_checked():
                checkbox.click(force=True)
            else:
                try:
                    self._wait_toolbar_delete_ready(timeout=5000)
                    return self
                except AssertionError:
                    checkbox.click(force=True)

            self.page.wait_for_timeout(settings.polling_interval)
            refreshed = self.find_visible(row_checkbox_selectors)
            if refreshed is not None:
                checkbox = refreshed

        row = self.find_visible(row_selectors)
        if row is not None:
            row.click(force=True)
            self.page.wait_for_timeout(settings.polling_interval)

        self._wait_toolbar_delete_ready(timeout=settings.page_load_timeout)
        return self

    @log_method("Click Delete button")
    def click_delete(self, booking_no: str | None = None) -> EfmsBookingReceiptPage:
        if not booking_no:
            toolbar_delete = self.find_visible(self._toolbar_delete_selectors())
            if toolbar_delete is not None:
                toolbar_delete.click(force=True)
                return self
            raise AssertionError("Toolbar Delete not found; booking_no is required for row delete.")

        self._click_delete_for_booking(booking_no)
        return self

    @log_method("Wait until Booking Receipt is absent from grid")
    def wait_until_booking_absent(self, booking_no: str, timeout: int | None = None) -> bool:
        timeout = timeout or settings.page_load_timeout
        try:
            self.page.wait_for_load_state(
                "networkidle",
                timeout=min(15000, timeout),
            )
        except Exception:
            pass
        self._wait_for_grid_ready(timeout=timeout)

        deadline = time.monotonic() + timeout / 1000
        while time.monotonic() < deadline:
            if self.is_booking_absent_from_grid(booking_no):
                return True
            self.page.wait_for_timeout(settings.polling_interval)
        return False

    @log_method("Get Booking Receipt status in grid")
    def get_booking_status_in_grid(self, booking_no: str) -> str:
        row_selectors = [
            f"xpath=//table//tbody//tr[.//*[contains(normalize-space(),'{booking_no}')]]",
            f"xpath=//tr[.//*[contains(normalize-space(),'{booking_no}')]]",
        ]
        row = self.wait_for_visible(
            row_selectors,
            f"Row for booking: {booking_no}",
            timeout=settings.page_load_timeout,
        )
        row_text = " ".join(row.inner_text().split())
        if "Draft" in row_text:
            return "Draft"
        if "Confirmed" in row_text:
            return "Confirmed"
        if "Rejected" in row_text:
            return "Rejected"
        return row_text

    @log_method("Verify Booking Receipt is not in grid")
    def is_booking_absent_from_grid(self, booking_no: str) -> bool:
        row = self.page.locator(
            "xpath=//table//tbody//tr[.//span[normalize-space()='"
            f"{booking_no}"
            "'] or .//a[normalize-space()='"
            f"{booking_no}"
            "']]"
        )
        try:
            return row.count() == 0
        except Exception:
            # Grid is often re-rendered right after delete; treat transient detach as retry case.
            return False

    @log_method("Get Booking row text in grid")
    def get_booking_row_text(self, booking_no: str) -> str:
        row = self.page.locator(
            "xpath=//table//tbody//tr[.//span[normalize-space()='"
            f"{booking_no}"
            "'] or .//a[normalize-space()='"
            f"{booking_no}"
            "']]"
        ).first
        if row.count() == 0:
            return ""
        return " ".join(row.inner_text().split()).strip()
