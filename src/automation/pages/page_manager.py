from playwright.sync_api import Page

from automation.pages.efms import (
    EfmsAgentPage,
    EfmsBookingReceiptPage,
    EfmsCustomerPage,
    EfmsCustomClearancePage,
    EfmsHomePage,
    EfmsJobManagementPage,
    EfmsLoginPage,
    EfmsServicesDocumentationPage,
    EfmsTruckingInlandPage,
    EfmsWorkOrderPage,
)
from automation.pages.etms import EtmsHomePage


class PageManager:
    def __init__(self, page: Page):
        self.page = page
        self._efms_login_page: EfmsLoginPage | None = None
        self._efms_home_page: EfmsHomePage | None = None
        self._efms_agent_page: EfmsAgentPage | None = None
        self._efms_customer_page: EfmsCustomerPage | None = None
        self._efms_work_order_page: EfmsWorkOrderPage | None = None
        self._efms_booking_receipt_page: EfmsBookingReceiptPage | None = None
        self._efms_job_management_page: EfmsJobManagementPage | None = None
        self._efms_custom_clearance_page: EfmsCustomClearancePage | None = None
        self._efms_trucking_inland_page: EfmsTruckingInlandPage | None = None
        self._efms_services_documentation_page: EfmsServicesDocumentationPage | None = None
        self._etms_home_page: EtmsHomePage | None = None

    @property
    def efms_login_page(self) -> EfmsLoginPage:
        if self._efms_login_page is None:
            self._efms_login_page = EfmsLoginPage(self.page)
        return self._efms_login_page

    @property
    def efms_home_page(self) -> EfmsHomePage:
        if self._efms_home_page is None:
            self._efms_home_page = EfmsHomePage(self.page)
        return self._efms_home_page

    @property
    def efms_agent_page(self) -> EfmsAgentPage:
        if self._efms_agent_page is None:
            self._efms_agent_page = EfmsAgentPage(self.page)
        return self._efms_agent_page

    @property
    def efms_customer_page(self) -> EfmsCustomerPage:
        if self._efms_customer_page is None:
            self._efms_customer_page = EfmsCustomerPage(self.page)
        return self._efms_customer_page

    @property
    def efms_work_order_page(self) -> EfmsWorkOrderPage:
        if self._efms_work_order_page is None:
            self._efms_work_order_page = EfmsWorkOrderPage(self.page)
        return self._efms_work_order_page

    @property
    def efms_booking_receipt_page(self) -> EfmsBookingReceiptPage:
        if self._efms_booking_receipt_page is None:
            self._efms_booking_receipt_page = EfmsBookingReceiptPage(self.page)
        return self._efms_booking_receipt_page

    @property
    def efms_job_management_page(self) -> EfmsJobManagementPage:
        if self._efms_job_management_page is None:
            self._efms_job_management_page = EfmsJobManagementPage(self.page)
        return self._efms_job_management_page

    @property
    def efms_custom_clearance_page(self) -> EfmsCustomClearancePage:
        if self._efms_custom_clearance_page is None:
            self._efms_custom_clearance_page = EfmsCustomClearancePage(self.page)
        return self._efms_custom_clearance_page

    @property
    def efms_trucking_inland_page(self) -> EfmsTruckingInlandPage:
        if self._efms_trucking_inland_page is None:
            self._efms_trucking_inland_page = EfmsTruckingInlandPage(self.page)
        return self._efms_trucking_inland_page

    @property
    def efms_services_documentation_page(self) -> EfmsServicesDocumentationPage:
        if self._efms_services_documentation_page is None:
            self._efms_services_documentation_page = EfmsServicesDocumentationPage(
                self.page
            )
        return self._efms_services_documentation_page

    @property
    def etms_home_page(self) -> EtmsHomePage:
        if self._etms_home_page is None:
            self._etms_home_page = EtmsHomePage(self.page)
        return self._etms_home_page
