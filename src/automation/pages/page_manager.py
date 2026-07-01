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
    EtmsVehicleListPage,
    EtmsZoneCodePage,
)
from automation.pages.etms.etms_customer_service_pages import (
    EtmsContainerDepositManagementPage,
    EtmsFclBookingPage,
    EtmsLclFtlBookingPage,
    EtmsLclShipmentManagementPage,
    EtmsSoaForOutsourcePage,
)
from automation.pages.etms.etms_management_pages import EtmsAuthorizationPage
from automation.pages.etms.etms_system_pages import (
    EtmsApprovalWorkflowConfigurationPage,
    EtmsGuideStylePage,
    EtmsSystemRolePage,
    EtmsUserLogPage,
)
from automation.pages.etms.etms_material_pages import (
    EtmsExportMaterialPage,
    EtmsImportMaterialPage,
)
from automation.pages.etms.etms_accounting_pages import (
    EtmsAccountingPaymentRequestPage,
    EtmsAccrualOfCostsPage,
    EtmsRevenueAccrualPage,
)
from automation.pages.etms.etms_reporting_page import EtmsReportingPage
from automation.pages.etms.etms_maintenance_pages import (
    EtmsMaintenanceSettlementPage,
    EtmsMrPaymentRequestPage,
    EtmsMrRequestPage,
    EtmsMrTypePage,
    EtmsVehicleMrPlanPage,
    EtmsVehicleNeedMaintainingPage,
)
from automation.pages.etms.etms_operation_lcl_ftl_action_page import (
    EtmsLclFtlCheckInPage,
    EtmsLclFtlCheckOutPage,
    EtmsLclFtlUnbagPage,
)
from automation.pages.etms.etms_operation_pages import (
    EtmsConfirmEpodPage,
    EtmsUnlockTransportRequestPage,
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
        self._etms_unlock_transport_request_page: EtmsUnlockTransportRequestPage | None = None
        self._etms_confirm_epod_page: EtmsConfirmEpodPage | None = None
        self._etms_lcl_ftl_check_out_page: EtmsLclFtlCheckOutPage | None = None
        self._etms_lcl_ftl_check_in_page: EtmsLclFtlCheckInPage | None = None
        self._etms_lcl_ftl_unbag_page: EtmsLclFtlUnbagPage | None = None
        self._etms_vehicle_need_maintaining_page: EtmsVehicleNeedMaintainingPage | None = None
        self._etms_mr_request_page: EtmsMrRequestPage | None = None
        self._etms_maintenance_settlement_page: EtmsMaintenanceSettlementPage | None = None
        self._etms_mr_payment_request_page: EtmsMrPaymentRequestPage | None = None
        self._etms_vehicle_mr_plan_page: EtmsVehicleMrPlanPage | None = None
        self._etms_mr_type_page: EtmsMrTypePage | None = None
        self._etms_import_material_page: EtmsImportMaterialPage | None = None
        self._etms_export_material_page: EtmsExportMaterialPage | None = None
        self._etms_accrual_of_costs_page: EtmsAccrualOfCostsPage | None = None
        self._etms_accounting_payment_request_page: EtmsAccountingPaymentRequestPage | None = None
        self._etms_revenue_accrual_page: EtmsRevenueAccrualPage | None = None
        self._etms_accounting_reporting_page: EtmsReportingPage | None = None
        self._etms_authorization_page: EtmsAuthorizationPage | None = None
        self._etms_role_page: EtmsSystemRolePage | None = None
        self._etms_user_log_page: EtmsUserLogPage | None = None
        self._etms_guide_style_page: EtmsGuideStylePage | None = None
        self._etms_approval_workflow_configuration_page: (
            EtmsApprovalWorkflowConfigurationPage | None
        ) = None
        self._etms_catalogue_menu_page: EtmsCatalogueMenuPage | None = None
        self._etms_catalogue_list_pages: dict[str, EtmsCatalogueListPage] = {}
        self._etms_administrative_units_page: EtmsAdministrativeUnitsPage | None = None
        self._etms_booking_information_page: EtmsBookingInformationPage | None = None
        self._etms_zone_code_page: EtmsZoneCodePage | None = None
        self._etms_vehicle_part_type_page: EtmsVehiclePartTypePage | None = None
        self._etms_vehicle_type_page: EtmsVehicleTypePage | None = None
        self._etms_vehicle_list_page: EtmsVehicleListPage | None = None
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
    def etms_unlock_transport_request_page(self) -> EtmsUnlockTransportRequestPage:
        if self._etms_unlock_transport_request_page is None:
            self._etms_unlock_transport_request_page = EtmsUnlockTransportRequestPage(
                self.page
            )
        return self._etms_unlock_transport_request_page

    @property
    def etms_confirm_epod_page(self) -> EtmsConfirmEpodPage:
        if self._etms_confirm_epod_page is None:
            self._etms_confirm_epod_page = EtmsConfirmEpodPage(self.page)
        return self._etms_confirm_epod_page

    @property
    def etms_lcl_ftl_check_out_page(self) -> EtmsLclFtlCheckOutPage:
        if self._etms_lcl_ftl_check_out_page is None:
            self._etms_lcl_ftl_check_out_page = EtmsLclFtlCheckOutPage(self.page)
        return self._etms_lcl_ftl_check_out_page

    @property
    def etms_lcl_ftl_check_in_page(self) -> EtmsLclFtlCheckInPage:
        if self._etms_lcl_ftl_check_in_page is None:
            self._etms_lcl_ftl_check_in_page = EtmsLclFtlCheckInPage(self.page)
        return self._etms_lcl_ftl_check_in_page

    @property
    def etms_lcl_ftl_unbag_page(self) -> EtmsLclFtlUnbagPage:
        if self._etms_lcl_ftl_unbag_page is None:
            self._etms_lcl_ftl_unbag_page = EtmsLclFtlUnbagPage(self.page)
        return self._etms_lcl_ftl_unbag_page

    @property
    def etms_vehicle_need_maintaining_page(self) -> EtmsVehicleNeedMaintainingPage:
        if self._etms_vehicle_need_maintaining_page is None:
            self._etms_vehicle_need_maintaining_page = EtmsVehicleNeedMaintainingPage(
                self.page
            )
        return self._etms_vehicle_need_maintaining_page

    @property
    def etms_mr_request_page(self) -> EtmsMrRequestPage:
        if self._etms_mr_request_page is None:
            self._etms_mr_request_page = EtmsMrRequestPage(self.page)
        return self._etms_mr_request_page

    @property
    def etms_maintenance_settlement_page(self) -> EtmsMaintenanceSettlementPage:
        if self._etms_maintenance_settlement_page is None:
            self._etms_maintenance_settlement_page = EtmsMaintenanceSettlementPage(
                self.page
            )
        return self._etms_maintenance_settlement_page

    @property
    def etms_mr_payment_request_page(self) -> EtmsMrPaymentRequestPage:
        if self._etms_mr_payment_request_page is None:
            self._etms_mr_payment_request_page = EtmsMrPaymentRequestPage(self.page)
        return self._etms_mr_payment_request_page

    @property
    def etms_vehicle_mr_plan_page(self) -> EtmsVehicleMrPlanPage:
        if self._etms_vehicle_mr_plan_page is None:
            self._etms_vehicle_mr_plan_page = EtmsVehicleMrPlanPage(self.page)
        return self._etms_vehicle_mr_plan_page

    @property
    def etms_mr_type_page(self) -> EtmsMrTypePage:
        if self._etms_mr_type_page is None:
            self._etms_mr_type_page = EtmsMrTypePage(self.page)
        return self._etms_mr_type_page

    @property
    def etms_import_material_page(self) -> EtmsImportMaterialPage:
        if self._etms_import_material_page is None:
            self._etms_import_material_page = EtmsImportMaterialPage(self.page)
        return self._etms_import_material_page

    @property
    def etms_export_material_page(self) -> EtmsExportMaterialPage:
        if self._etms_export_material_page is None:
            self._etms_export_material_page = EtmsExportMaterialPage(self.page)
        return self._etms_export_material_page

    @property
    def etms_accrual_of_costs_page(self) -> EtmsAccrualOfCostsPage:
        if self._etms_accrual_of_costs_page is None:
            self._etms_accrual_of_costs_page = EtmsAccrualOfCostsPage(self.page)
        return self._etms_accrual_of_costs_page

    @property
    def etms_accounting_payment_request_page(self) -> EtmsAccountingPaymentRequestPage:
        if self._etms_accounting_payment_request_page is None:
            self._etms_accounting_payment_request_page = EtmsAccountingPaymentRequestPage(
                self.page
            )
        return self._etms_accounting_payment_request_page

    @property
    def etms_revenue_accrual_page(self) -> EtmsRevenueAccrualPage:
        if self._etms_revenue_accrual_page is None:
            self._etms_revenue_accrual_page = EtmsRevenueAccrualPage(self.page)
        return self._etms_revenue_accrual_page

    @property
    def etms_reporting_page(self) -> EtmsReportingPage:
        if self._etms_accounting_reporting_page is None:
            self._etms_accounting_reporting_page = EtmsReportingPage(self.page)
        return self._etms_accounting_reporting_page

    @property
    def etms_accounting_reporting_page(self) -> EtmsReportingPage:
        """Backward-compatible alias for etms_reporting_page."""
        return self.etms_reporting_page

    @property
    def etms_authorization_page(self) -> EtmsAuthorizationPage:
        if self._etms_authorization_page is None:
            self._etms_authorization_page = EtmsAuthorizationPage(self.page)
        return self._etms_authorization_page

    @property
    def etms_role_page(self) -> EtmsSystemRolePage:
        if self._etms_role_page is None:
            self._etms_role_page = EtmsSystemRolePage(self.page)
        return self._etms_role_page

    @property
    def etms_user_log_page(self) -> EtmsUserLogPage:
        if self._etms_user_log_page is None:
            self._etms_user_log_page = EtmsUserLogPage(self.page)
        return self._etms_user_log_page

    @property
    def etms_guide_style_page(self) -> EtmsGuideStylePage:
        if self._etms_guide_style_page is None:
            self._etms_guide_style_page = EtmsGuideStylePage(self.page)
        return self._etms_guide_style_page

    @property
    def etms_approval_workflow_configuration_page(
        self,
    ) -> EtmsApprovalWorkflowConfigurationPage:
        if self._etms_approval_workflow_configuration_page is None:
            self._etms_approval_workflow_configuration_page = (
                EtmsApprovalWorkflowConfigurationPage(self.page)
            )
        return self._etms_approval_workflow_configuration_page

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
    def etms_vehicle_list_page(self) -> EtmsVehicleListPage:
        if self._etms_vehicle_list_page is None:
            self._etms_vehicle_list_page = EtmsVehicleListPage(self.page)
        return self._etms_vehicle_list_page

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
