from automation.logging import log_method
from automation.pages.efms.services.services_menu_page import EfmsServicesMenuPage


class EfmsServicesDocumentationPage(EfmsServicesMenuPage):
    shipment_item_selectors = [
        "xpath=//div[contains(@class,'m-portlet__body')]//div[@class='shipment-item-wrapper']",
        "xpath=//div[contains(@class,'m-portlet__body')]//div[contains(@class,'shipment-item-wrapper')]",
        "xpath=//div[@class='shipment-item-wrapper']",
        ".m-portlet__body .shipment-item-wrapper",
    ]

    def _menu_selectors(self, href_fragment: str, label: str) -> list[str]:
        return [
            f"xpath=//div[contains(@class,'m-menu__submenu')]//a[contains(@href,'{href_fragment}')]",
            f"xpath=//li[contains(@class,'m-menu__item--open')]//div[contains(@class,'m-menu__submenu')]//a[.//span[normalize-space()='{label}']]",
            f"xpath=//div[contains(@class,'m-menu__submenu')]//span[normalize-space()='{label}']",
            f"xpath=//span[normalize-space()='{label}']",
        ]

    def _title_selectors(self, label: str) -> list[str]:
        return [
            f"xpath=//h3[normalize-space()='{label}']",
            f"h3:has-text('{label}')",
        ]

    def _click_service(self, label: str, href_fragment: str, hash_fragment: str) -> None:
        self._click_services_submenu(
            self._menu_selectors(href_fragment, label),
            hash_fragment,
        )

    def _verify_service(self, label: str, hash_fragment: str) -> bool:
        return self._is_services_page_displayed(
            hash_fragment,
            self._title_selectors(label),
            f"{label} title",
            self.shipment_item_selectors,
            f"{label} shipment list",
        )

    @log_method("Click Air Export Menu")
    def click_air_export_menu(self) -> "EfmsServicesDocumentationPage":
        self._click_service(
            "Air Export",
            "documentation/air-export",
            "/home/documentation/air-export",
        )
        return self

    @log_method("Verify Air Export is displayed")
    def is_air_export_displayed(self) -> bool:
        return self._verify_service("Air Export", "#/home/documentation/air-export")

    @log_method("Click Air Import Menu")
    def click_air_import_menu(self) -> "EfmsServicesDocumentationPage":
        self._click_service(
            "Air Import",
            "documentation/air-import",
            "/home/documentation/air-import",
        )
        return self

    @log_method("Verify Air Import is displayed")
    def is_air_import_displayed(self) -> bool:
        return self._verify_service("Air Import", "#/home/documentation/air-import")

    @log_method("Click Sea Consol Export Menu")
    def click_sea_consol_export_menu(self) -> "EfmsServicesDocumentationPage":
        self._click_service(
            "Sea Consol Export",
            "documentation/sea-consol-export",
            "/home/documentation/sea-consol-export",
        )
        return self

    @log_method("Verify Sea Consol Export is displayed")
    def is_sea_consol_export_displayed(self) -> bool:
        return self._verify_service(
            "Sea Consol Export",
            "#/home/documentation/sea-consol-export",
        )

    @log_method("Click Sea Consol Import Menu")
    def click_sea_consol_import_menu(self) -> "EfmsServicesDocumentationPage":
        self._click_service(
            "Sea Consol Import",
            "documentation/sea-consol-import",
            "/home/documentation/sea-consol-import",
        )
        return self

    @log_method("Verify Sea Consol Import is displayed")
    def is_sea_consol_import_displayed(self) -> bool:
        return self._verify_service(
            "Sea Consol Import",
            "#/home/documentation/sea-consol-import",
        )

    @log_method("Click Sea FCL Export Menu")
    def click_sea_fcl_export_menu(self) -> "EfmsServicesDocumentationPage":
        self._click_service(
            "Sea FCL Export",
            "documentation/sea-fcl-export",
            "/home/documentation/sea-fcl-export",
        )
        return self

    @log_method("Verify Sea FCL Export is displayed")
    def is_sea_fcl_export_displayed(self) -> bool:
        return self._verify_service(
            "Sea FCL Export",
            "#/home/documentation/sea-fcl-export",
        )

    @log_method("Click Sea FCL Import Menu")
    def click_sea_fcl_import_menu(self) -> "EfmsServicesDocumentationPage":
        self._click_service(
            "Sea FCL Import",
            "documentation/sea-fcl-import",
            "/home/documentation/sea-fcl-import",
        )
        return self

    @log_method("Verify Sea FCL Import is displayed")
    def is_sea_fcl_import_displayed(self) -> bool:
        return self._verify_service(
            "Sea FCL Import",
            "#/home/documentation/sea-fcl-import",
        )

    @log_method("Click Sea LCL Export Menu")
    def click_sea_lcl_export_menu(self) -> "EfmsServicesDocumentationPage":
        self._click_service(
            "Sea LCL Export",
            "documentation/sea-lcl-export",
            "/home/documentation/sea-lcl-export",
        )
        return self

    @log_method("Verify Sea LCL Export is displayed")
    def is_sea_lcl_export_displayed(self) -> bool:
        return self._verify_service(
            "Sea LCL Export",
            "#/home/documentation/sea-lcl-export",
        )

    @log_method("Click Sea LCL Import Menu")
    def click_sea_lcl_import_menu(self) -> "EfmsServicesDocumentationPage":
        self._click_service(
            "Sea LCL Import",
            "documentation/sea-lcl-import",
            "/home/documentation/sea-lcl-import",
        )
        return self

    @log_method("Verify Sea LCL Import is displayed")
    def is_sea_lcl_import_displayed(self) -> bool:
        return self._verify_service(
            "Sea LCL Import",
            "#/home/documentation/sea-lcl-import",
        )
