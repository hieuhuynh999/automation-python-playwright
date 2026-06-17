import pytest

from automation.config import settings
from automation.logging.step_logger import record_step_log
from tests.data_provider import DataProvider

COMMERCIAL_MENU_ACTIONS = {
    "agent": (
        "efms_agent_page",
        "click_agent_menu",
        "is_agent_list_displayed",
    ),
    "customer": (
        "efms_customer_page",
        "click_customer_menu",
        "is_customer_list_displayed",
    ),
    "work_order": (
        "efms_work_order_page",
        "click_work_order_menu",
        "is_work_order_list_displayed",
    ),
    "booking_receipt": (
        "efms_booking_receipt_page",
        "click_booking_receipt_menu",
        "is_booking_receipt_displayed",
    ),
}

LOGISTICS_MENU_ACTIONS = {
    "job_management": (
        "efms_job_management_page",
        "click_job_management_menu",
        "is_job_management_displayed",
    ),
    "custom_clearance": (
        "efms_custom_clearance_page",
        "click_custom_clearance_menu",
        "is_custom_clearance_displayed",
    ),
    "trucking_inland": (
        "efms_trucking_inland_page",
        "click_trucking_inland_menu",
        "is_trucking_inland_displayed",
    ),
}

SERVICES_MENU_ACTIONS = {
    "air_export": (
        "efms_services_documentation_page",
        "click_air_export_menu",
        "is_air_export_displayed",
    ),
    "air_import": (
        "efms_services_documentation_page",
        "click_air_import_menu",
        "is_air_import_displayed",
    ),
    "sea_consol_export": (
        "efms_services_documentation_page",
        "click_sea_consol_export_menu",
        "is_sea_consol_export_displayed",
    ),
    "sea_consol_import": (
        "efms_services_documentation_page",
        "click_sea_consol_import_menu",
        "is_sea_consol_import_displayed",
    ),
    "sea_fcl_export": (
        "efms_services_documentation_page",
        "click_sea_fcl_export_menu",
        "is_sea_fcl_export_displayed",
    ),
    "sea_fcl_import": (
        "efms_services_documentation_page",
        "click_sea_fcl_import_menu",
        "is_sea_fcl_import_displayed",
    ),
    "sea_lcl_export": (
        "efms_services_documentation_page",
        "click_sea_lcl_export_menu",
        "is_sea_lcl_export_displayed",
    ),
    "sea_lcl_import": (
        "efms_services_documentation_page",
        "click_sea_lcl_import_menu",
        "is_sea_lcl_import_displayed",
    ),
}


@pytest.mark.navigation
@pytest.mark.efms
class TestEfmsNavigate:
    @pytest.mark.parametrize(
        "data",
        DataProvider.efms_cases("test_smk_nav_verify_commercial_menu_efms"),
    )
    def test_smk_nav_verify_commercial_menu_efms(self, pages, data, efms_account_password):
        # Precondition: Login success
        pages.efms_login_page.open().login(
            settings.efms_username,
            efms_account_password,
            data["company"],
        )
        assert pages.efms_home_page.is_dashboard_displayed()
        pages.efms_home_page.wait_for_dashboard_ready()

        # Step 1: Open Commercial Menu
        pages.efms_agent_page.open_commercial_menu()

        for index, scenario in enumerate(data["scenarios"]):
            step = scenario["step"]
            record_step_log(f"[STEP {step}] {scenario['description']}")

            # Reset to dashboard before each scenario except the first
            if index > 0:
                base_url = pages.efms_agent_page.page.url.split("#")[0]
                pages.efms_agent_page.page.goto(
                    f"{base_url}#/home",
                    wait_until="domcontentloaded",
                )
                pages.efms_home_page.wait_for_dashboard_ready()
                pages.efms_agent_page.wait_for_sidebar_ready()
                pages.efms_agent_page.open_commercial_menu()

            page_name, click_method_name, verify_method_name = COMMERCIAL_MENU_ACTIONS[
                scenario["menu_action"]
            ]
            action_page = getattr(pages, page_name)

            getattr(action_page, click_method_name)()

            assert getattr(action_page, verify_method_name)(), (
                f"Step {step}: {scenario['description']} — verification failed"
            )
            record_step_log(f"[STEP PASS] {step}")

    @pytest.mark.parametrize(
        "data",
        DataProvider.efms_cases("test_smk_nav_verify_logistics_menu_efms"),
    )
    @pytest.mark.tc_id("SMK_NAV_005")
    def test_smk_nav_verify_logistics_menu_efms(self, pages, data, efms_account_password):
        # Precondition: Login success
        pages.efms_login_page.open().login(
            settings.efms_username,
            efms_account_password,
            data["company"],
        )
        assert pages.efms_home_page.is_dashboard_displayed()
        pages.efms_home_page.wait_for_dashboard_ready()

        # Step 1: Open Logistics Menu
        pages.efms_job_management_page.open_logistics_menu()

        for scenario in data["scenarios"]:
            step = scenario["step"]
            record_step_log(
                f"[STEP {step}] {scenario['description']}",
            )

            page_name, click_method_name, verify_method_name = LOGISTICS_MENU_ACTIONS[
                scenario["menu_action"]
            ]
            action_page = getattr(pages, page_name)

            getattr(action_page, click_method_name)()

            assert getattr(action_page, verify_method_name)(), (
                f"Step {step}: {scenario['description']} — verification failed"
            )
            record_step_log(f"[STEP PASS] {step}")

    @pytest.mark.parametrize(
        "data",
        DataProvider.efms_cases("test_smk_nav_verify_services_menu_efms"),
    )
    @pytest.mark.tc_id("SMK_NAV_006")
    def test_smk_nav_verify_services_menu_efms(self, pages, data, efms_account_password):
        # Precondition: Login success
        pages.efms_login_page.open().login(
            settings.efms_username,
            efms_account_password,
            data["company"],
        )
        assert pages.efms_home_page.is_dashboard_displayed()
        pages.efms_home_page.wait_for_dashboard_ready()

        # Step 1: Open Services Menu
        pages.efms_services_documentation_page.open_services_menu()

        for scenario in data["scenarios"]:
            step = scenario["step"]
            record_step_log(f"[STEP {step}] {scenario['description']}")

            page_name, click_method_name, verify_method_name = SERVICES_MENU_ACTIONS[
                scenario["menu_action"]
            ]
            action_page = getattr(pages, page_name)

            getattr(action_page, click_method_name)()

            assert getattr(action_page, verify_method_name)(), (
                f"Step {step}: {scenario['description']} — verification failed"
            )
            record_step_log(f"[STEP PASS] {step}")
