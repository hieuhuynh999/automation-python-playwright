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

    @log_method("Click Booking Receipt Menu")
    def click_booking_receipt_menu(self) -> "EfmsBookingReceiptPage":
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
