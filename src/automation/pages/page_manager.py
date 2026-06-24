from playwright.sync_api import Page

from automation.pages.efms import (
    EfmsAgentPage,
    EfmsBookingReceiptPage,
    EfmsCustomClearancePage,
    EfmsCustomerPage,
    EfmsHomePage,
    EfmsJobManagementPage,
    EfmsLoginPage,
    EfmsServicesDocumentationPage,
    EfmsTruckingInlandPage,
    EfmsWorkOrderPage,
)
from automation.pages.etms import (
    EtmsCostOfRoutePage,
    EtmsDistanceBetweenPlacesPage,
    EtmsHomePage,
    EtmsLoginPage,
    EtmsPartnerListPage,
    EtmsPlacesPage,
    EtmsTransportNetworkListPage,
    EtmsVfcLoginPage,
)


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
        self._etms_cost_of_route_page: EtmsCostOfRoutePage | None = None
        self._etms_places_page: EtmsPlacesPage | None = None
        self._etms_distance_between_places_page: EtmsDistanceBetweenPlacesPage | None = None
        self._etms_transport_network_list_pages: dict[str, EtmsTransportNetworkListPage] = {}
        self._etms_partner_list_pages: dict[str, EtmsPartnerListPage] = {}
        self._etms_home_page: EtmsHomePage | None = None
        self._etms_login_page: EtmsLoginPage | None = None
        self._etms_vfc_login_page: EtmsVfcLoginPage | None = None

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
            self._efms_services_documentation_page = EfmsServicesDocumentationPage(self.page)
        return self._efms_services_documentation_page

    @property
    def etms_cost_of_route_page(self) -> EtmsCostOfRoutePage:
        if self._etms_cost_of_route_page is None:
            self._etms_cost_of_route_page = EtmsCostOfRoutePage(self.page)
        return self._etms_cost_of_route_page

    @property
    def etms_places_page(self) -> EtmsPlacesPage:
        if self._etms_places_page is None:
            self._etms_places_page = EtmsPlacesPage(self.page)
        return self._etms_places_page

    @property
    def etms_distance_between_places_page(self) -> EtmsDistanceBetweenPlacesPage:
        if self._etms_distance_between_places_page is None:
            self._etms_distance_between_places_page = EtmsDistanceBetweenPlacesPage(self.page)
        return self._etms_distance_between_places_page

    def etms_transport_network_list_page(self, page_key: str) -> EtmsTransportNetworkListPage:
        if page_key not in self._etms_transport_network_list_pages:
            self._etms_transport_network_list_pages[page_key] = EtmsTransportNetworkListPage(
                self.page,
                page_key,
            )
        return self._etms_transport_network_list_pages[page_key]

    def etms_partner_list_page(self, page_key: str) -> EtmsPartnerListPage:
        if page_key not in self._etms_partner_list_pages:
            self._etms_partner_list_pages[page_key] = EtmsPartnerListPage(
                self.page,
                page_key,
            )
        return self._etms_partner_list_pages[page_key]

    @property
    def etms_login_page(self) -> EtmsLoginPage:
        if self._etms_login_page is None:
            self._etms_login_page = EtmsLoginPage(self.page)
        return self._etms_login_page

    @property
    def etms_vfc_login_page(self) -> EtmsVfcLoginPage:
        if self._etms_vfc_login_page is None:
            self._etms_vfc_login_page = EtmsVfcLoginPage(self.page)
        return self._etms_vfc_login_page

    @property
    def etms_home_page(self) -> EtmsHomePage:
        if self._etms_home_page is None:
            self._etms_home_page = EtmsHomePage(self.page)
        return self._etms_home_page
