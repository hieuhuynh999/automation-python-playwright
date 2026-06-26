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
    CATALOGUE_LIST_PAGE_CONFIGS,
    EtmsAdministrativeUnitsPage,
    EtmsBookingInformationPage,
    EtmsCatalogueListPage,
    EtmsCatalogueMenuPage,
    EtmsCommissionRateCardPage,
    EtmsCostOfRoutePage,
    EtmsCostOfRouteWorkflowPage,
    EtmsDistributionBuyingPage,
    EtmsDistributionRateCardPage,
    EtmsFclBuyingPricePage,
    EtmsFclRateCardListPage,
    EtmsFclRentingContainerPage,
    EtmsFclRentingVehiclePage,
    EtmsHomePage,
    EtmsLclBuyingPage,
    EtmsLclRateCardPage,
    EtmsLoginPage,
    EtmsPriceTollBuyingPage,
    EtmsVfcLoginPage,
    EtmsVehiclePartTypePage,
    EtmsVehicleTypePage,
    EtmsZoneCodePage,
)
from automation.pages.etms.etms_customer_service_pages import (
    EtmsContainerDepositManagementPage,
    EtmsFclBookingPage,
    EtmsLclFtlBookingPage,
    EtmsLclShipmentManagementPage,
    EtmsSoaForOutsourcePage,
)
from automation.pages.etms.etms_pricing_report_page import EtmsPricingReportPage
from automation.pages.etms.etms_pricing_workflow_list_page import EtmsFclQuotationListPage
from automation.pages.etms.etms_quotation_form_page import (
    EtmsCreateDistributionQuotationPage,
    EtmsCreateFclQuotationPage,
    EtmsCreateLclQuotationPage,
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
        self._etms_cost_of_route_workflow_page: EtmsCostOfRouteWorkflowPage | None = None
        self._etms_price_toll_buying_page: EtmsPriceTollBuyingPage | None = None
        self._etms_fcl_rate_card_list_page: EtmsFclRateCardListPage | None = None
        self._etms_fcl_buying_price_page: EtmsFclBuyingPricePage | None = None
        self._etms_fcl_renting_container_page: EtmsFclRentingContainerPage | None = None
        self._etms_fcl_renting_vehicle_page: EtmsFclRentingVehiclePage | None = None
        self._etms_lcl_rate_card_page: EtmsLclRateCardPage | None = None
        self._etms_lcl_buying_page: EtmsLclBuyingPage | None = None
        self._etms_distribution_rate_card_page: EtmsDistributionRateCardPage | None = None
        self._etms_distribution_buying_page: EtmsDistributionBuyingPage | None = None
        self._etms_pricing_report_page: EtmsPricingReportPage | None = None
        self._etms_commission_rate_card_page: EtmsCommissionRateCardPage | None = None
        self._etms_create_fcl_quotation_page: EtmsCreateFclQuotationPage | None = None
        self._etms_fcl_quotation_list_page: EtmsFclQuotationListPage | None = None
        self._etms_create_lcl_quotation_page: EtmsCreateLclQuotationPage | None = None
        self._etms_create_distribution_quotation_page: EtmsCreateDistributionQuotationPage | None = None
        self._etms_fcl_booking_page: EtmsFclBookingPage | None = None
        self._etms_container_deposit_management_page: EtmsContainerDepositManagementPage | None = None
        self._etms_lcl_ftl_booking_page: EtmsLclFtlBookingPage | None = None
        self._etms_lcl_shipment_management_page: EtmsLclShipmentManagementPage | None = None
        self._etms_soa_for_outsource_page: EtmsSoaForOutsourcePage | None = None
        self._etms_catalogue_menu_page: EtmsCatalogueMenuPage | None = None
        self._etms_catalogue_list_pages: dict[str, EtmsCatalogueListPage] = {}
        self._etms_administrative_units_page: EtmsAdministrativeUnitsPage | None = None
        self._etms_booking_information_page: EtmsBookingInformationPage | None = None
        self._etms_zone_code_page: EtmsZoneCodePage | None = None
        self._etms_vehicle_part_type_page: EtmsVehiclePartTypePage | None = None
        self._etms_vehicle_type_page: EtmsVehicleTypePage | None = None
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
    def etms_cost_of_route_workflow_page(self) -> EtmsCostOfRouteWorkflowPage:
        if self._etms_cost_of_route_workflow_page is None:
            self._etms_cost_of_route_workflow_page = EtmsCostOfRouteWorkflowPage(self.page)
        return self._etms_cost_of_route_workflow_page

    @property
    def etms_price_toll_buying_page(self) -> EtmsPriceTollBuyingPage:
        if self._etms_price_toll_buying_page is None:
            self._etms_price_toll_buying_page = EtmsPriceTollBuyingPage(self.page)
        return self._etms_price_toll_buying_page

    @property
    def etms_fcl_rate_card_list_page(self) -> EtmsFclRateCardListPage:
        if self._etms_fcl_rate_card_list_page is None:
            self._etms_fcl_rate_card_list_page = EtmsFclRateCardListPage(self.page)
        return self._etms_fcl_rate_card_list_page

    @property
    def etms_fcl_buying_price_page(self) -> EtmsFclBuyingPricePage:
        if self._etms_fcl_buying_price_page is None:
            self._etms_fcl_buying_price_page = EtmsFclBuyingPricePage(self.page)
        return self._etms_fcl_buying_price_page

    @property
    def etms_fcl_renting_container_page(self) -> EtmsFclRentingContainerPage:
        if self._etms_fcl_renting_container_page is None:
            self._etms_fcl_renting_container_page = EtmsFclRentingContainerPage(self.page)
        return self._etms_fcl_renting_container_page

    @property
    def etms_fcl_renting_vehicle_page(self) -> EtmsFclRentingVehiclePage:
        if self._etms_fcl_renting_vehicle_page is None:
            self._etms_fcl_renting_vehicle_page = EtmsFclRentingVehiclePage(self.page)
        return self._etms_fcl_renting_vehicle_page

    @property
    def etms_lcl_rate_card_page(self) -> EtmsLclRateCardPage:
        if self._etms_lcl_rate_card_page is None:
            self._etms_lcl_rate_card_page = EtmsLclRateCardPage(self.page)
        return self._etms_lcl_rate_card_page

    @property
    def etms_lcl_buying_page(self) -> EtmsLclBuyingPage:
        if self._etms_lcl_buying_page is None:
            self._etms_lcl_buying_page = EtmsLclBuyingPage(self.page)
        return self._etms_lcl_buying_page

    @property
    def etms_distribution_rate_card_page(self) -> EtmsDistributionRateCardPage:
        if self._etms_distribution_rate_card_page is None:
            self._etms_distribution_rate_card_page = EtmsDistributionRateCardPage(self.page)
        return self._etms_distribution_rate_card_page

    @property
    def etms_distribution_buying_page(self) -> EtmsDistributionBuyingPage:
        if self._etms_distribution_buying_page is None:
            self._etms_distribution_buying_page = EtmsDistributionBuyingPage(self.page)
        return self._etms_distribution_buying_page

    @property
    def etms_pricing_report_page(self) -> EtmsPricingReportPage:
        if self._etms_pricing_report_page is None:
            self._etms_pricing_report_page = EtmsPricingReportPage(self.page)
        return self._etms_pricing_report_page

    @property
    def etms_commission_rate_card_page(self) -> EtmsCommissionRateCardPage:
        if self._etms_commission_rate_card_page is None:
            self._etms_commission_rate_card_page = EtmsCommissionRateCardPage(self.page)
        return self._etms_commission_rate_card_page

    @property
    def etms_create_fcl_quotation_page(self) -> EtmsCreateFclQuotationPage:
        if self._etms_create_fcl_quotation_page is None:
            self._etms_create_fcl_quotation_page = EtmsCreateFclQuotationPage(self.page)
        return self._etms_create_fcl_quotation_page

    @property
    def etms_fcl_quotation_list_page(self) -> EtmsFclQuotationListPage:
        if self._etms_fcl_quotation_list_page is None:
            self._etms_fcl_quotation_list_page = EtmsFclQuotationListPage(self.page)
        return self._etms_fcl_quotation_list_page

    @property
    def etms_create_lcl_quotation_page(self) -> EtmsCreateLclQuotationPage:
        if self._etms_create_lcl_quotation_page is None:
            self._etms_create_lcl_quotation_page = EtmsCreateLclQuotationPage(self.page)
        return self._etms_create_lcl_quotation_page

    @property
    def etms_create_distribution_quotation_page(self) -> EtmsCreateDistributionQuotationPage:
        if self._etms_create_distribution_quotation_page is None:
            self._etms_create_distribution_quotation_page = EtmsCreateDistributionQuotationPage(
                self.page
            )
        return self._etms_create_distribution_quotation_page

    @property
    def etms_fcl_booking_page(self) -> EtmsFclBookingPage:
        if self._etms_fcl_booking_page is None:
            self._etms_fcl_booking_page = EtmsFclBookingPage(self.page)
        return self._etms_fcl_booking_page

    @property
    def etms_container_deposit_management_page(self) -> EtmsContainerDepositManagementPage:
        if self._etms_container_deposit_management_page is None:
            self._etms_container_deposit_management_page = EtmsContainerDepositManagementPage(
                self.page
            )
        return self._etms_container_deposit_management_page

    @property
    def etms_lcl_ftl_booking_page(self) -> EtmsLclFtlBookingPage:
        if self._etms_lcl_ftl_booking_page is None:
            self._etms_lcl_ftl_booking_page = EtmsLclFtlBookingPage(self.page)
        return self._etms_lcl_ftl_booking_page

    @property
    def etms_lcl_shipment_management_page(self) -> EtmsLclShipmentManagementPage:
        if self._etms_lcl_shipment_management_page is None:
            self._etms_lcl_shipment_management_page = EtmsLclShipmentManagementPage(self.page)
        return self._etms_lcl_shipment_management_page

    @property
    def etms_soa_for_outsource_page(self) -> EtmsSoaForOutsourcePage:
        if self._etms_soa_for_outsource_page is None:
            self._etms_soa_for_outsource_page = EtmsSoaForOutsourcePage(self.page)
        return self._etms_soa_for_outsource_page

    @property
    def etms_catalogue_menu_page(self) -> EtmsCatalogueMenuPage:
        if self._etms_catalogue_menu_page is None:
            self._etms_catalogue_menu_page = EtmsCatalogueMenuPage(self.page)
        return self._etms_catalogue_menu_page

    def etms_catalogue_list_page(self, page_key: str) -> EtmsCatalogueListPage:
        if page_key not in self._etms_catalogue_list_pages:
            self._etms_catalogue_list_pages[page_key] = EtmsCatalogueListPage(
                self.page,
                page_key,
            )
        return self._etms_catalogue_list_pages[page_key]

    def etms_transport_network_list_page(self, page_key: str) -> EtmsCatalogueListPage:
        """Backward-compatible alias for Transport Network catalogue list pages."""
        if page_key not in CATALOGUE_LIST_PAGE_CONFIGS:
            known = ", ".join(sorted(CATALOGUE_LIST_PAGE_CONFIGS))
            raise KeyError(f"Unknown catalogue list page_key '{page_key}'. Known: {known}")
        return self.etms_catalogue_list_page(page_key)

    def etms_partner_list_page(self, page_key: str) -> EtmsCatalogueListPage:
        """Backward-compatible alias for Partner catalogue list pages."""
        return self.etms_transport_network_list_page(page_key)

    @property
    def etms_places_page(self) -> EtmsCatalogueListPage:
        """Backward-compatible alias — Places is a catalogue list page."""
        return self.etms_catalogue_list_page("places")

    @property
    def etms_distance_between_places_page(self) -> EtmsCatalogueListPage:
        """Backward-compatible alias — Distance Between Places is a catalogue list page."""
        return self.etms_catalogue_list_page("distance_between_places")

    @property
    def etms_administrative_units_page(self) -> EtmsAdministrativeUnitsPage:
        if self._etms_administrative_units_page is None:
            self._etms_administrative_units_page = EtmsAdministrativeUnitsPage(self.page)
        return self._etms_administrative_units_page

    @property
    def etms_booking_information_page(self) -> EtmsBookingInformationPage:
        if self._etms_booking_information_page is None:
            self._etms_booking_information_page = EtmsBookingInformationPage(self.page)
        return self._etms_booking_information_page

    @property
    def etms_zone_code_page(self) -> EtmsZoneCodePage:
        if self._etms_zone_code_page is None:
            self._etms_zone_code_page = EtmsZoneCodePage(self.page)
        return self._etms_zone_code_page

    @property
    def etms_vehicle_part_type_page(self) -> EtmsVehiclePartTypePage:
        if self._etms_vehicle_part_type_page is None:
            self._etms_vehicle_part_type_page = EtmsVehiclePartTypePage(self.page)
        return self._etms_vehicle_part_type_page

    @property
    def etms_vehicle_type_page(self) -> EtmsVehicleTypePage:
        if self._etms_vehicle_type_page is None:
            self._etms_vehicle_type_page = EtmsVehicleTypePage(self.page)
        return self._etms_vehicle_type_page

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
