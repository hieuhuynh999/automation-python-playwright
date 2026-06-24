import pytest

from tests.data_provider import DataProvider


@pytest.mark.etms
@pytest.mark.regression
class TestEtmsCostOfRoute:
    @pytest.mark.parametrize(
        "data",
        DataProvider.etms_cases("test_cor_lp_001_create_cost_of_route_etms"),
    )
    @pytest.mark.tc_id("COR_LP_001")
    def test_cor_lp_001_create_cost_of_route_etms(
        self,
        pages,
        data,
        login_etms,
    ):
        login_etms(data["branch"])
        cor_page = pages.etms_cost_of_route_page
        record_saved = False
        cleanup_done = False

        try:
            # Step 1: Search menu → open Cost Of Route page
            cor_page.open_via_menu_search(data["menu_search"])
            assert cor_page.is_list_page_displayed()
            cor_page.prepare_updating_tab_before_create(
                data["route_code"],
                tab_name=data.get("tab_updating", "Updating"),
                expected_delete_message=data["expected_delete_message"],
            )

            # Step 2: Click Add New → Choose Route popup
            cor_page.click_add_new()
            assert cor_page.is_choose_route_popup_displayed()

            # Step 3: Choose route → Add New form
            cor_page.choose_route(data["route_code"])
            assert cor_page.is_add_form_displayed()

            # Step 4: Select Vehicle Type, Container Type, Weight Range
            cor_page.fill_route_mapping_fields(data)

            # Step 5: Generate surcharge list, then verify Total (Price)
            cor_page.click_generate_surcharge()
            assert cor_page.is_total_price_displayed()

            # Step 6: Save → popup closes + success message
            cor_page.click_save()
            cor_page.wait_for_save_success(data["expected_success_message"])
            record_saved = True

            # Step 7: action-btn → Delete → confirm
            cor_page.ensure_list_page_displayed(data["menu_search"])
            cor_page.click_row_action_btn(data["route_code"], data["vehicle_type"])
            cor_page.click_row_delete_button(data["route_code"], data["vehicle_type"])
            assert cor_page.is_delete_confirm_displayed()
            cor_page.click_delete_confirm_ok()
            assert cor_page.is_success_message_displayed(data["expected_delete_message"])
            cleanup_done = True
        finally:
            if record_saved and not cleanup_done:
                cor_page.cleanup_created_record(
                    menu_search=data["menu_search"],
                    expected_delete_message=data["expected_delete_message"],
                    route_code=data["route_code"],
                    vehicle_type=data["vehicle_type"],
                )

    @pytest.mark.parametrize(
        "data",
        DataProvider.etms_cases("test_cor_cp_001_copy_cost_of_route_etms"),
    )
    @pytest.mark.tc_id("COR_CP_001")
    def test_cor_cp_001_copy_cost_of_route_etms(
        self,
        pages,
        data,
        login_etms,
    ):
        login_etms(data["branch"])
        cor_page = pages.etms_cost_of_route_page
        source_vehicle_type = data.get("source_vehicle_type")
        record_saved = False
        cleanup_done = False

        try:
            # Step 1: Open Cost Of Route page
            cor_page.open_via_menu_search(data["menu_search"])
            assert cor_page.is_list_page_displayed()
            cor_page.prepare_updating_tab_before_create(
                data["route_code"],
                tab_name=data.get("tab_updating", "Updating"),
                expected_delete_message=data["expected_delete_message"],
            )

            # Step 2: Click Accepted tab
            cor_page.click_list_tab(data["tab"], force=True)

            # Step 8: Search Route Code
            cor_page.search_route_on_list(data["route_code"])

            # Steps 9–11: action-btn → Copy → Cancel (popup then dismiss)
            cor_page.click_row_action_btn(data["route_code"], source_vehicle_type)
            cor_page.click_row_copy_button(data["route_code"], source_vehicle_type)
            assert cor_page.is_copy_confirm_displayed(data["expected_copy_confirm_message"])
            cor_page.click_copy_confirm_cancel()

            # Steps 12–14: action-btn → Copy → OK → Add New form
            cor_page.click_row_action_btn(data["route_code"], source_vehicle_type)
            cor_page.click_row_copy_button(data["route_code"], source_vehicle_type)
            assert cor_page.is_copy_confirm_displayed(data["expected_copy_confirm_message"])
            cor_page.click_copy_confirm_ok()
            assert cor_page.is_add_form_displayed()

            # Step 15: Vehicle Type, Container Type, Weight Range
            cor_page.fill_route_mapping_fields(data)

            # Step 16: Generate surcharge list
            cor_page.click_generate_surcharge()
            assert cor_page.is_total_price_displayed()

            # Step 17: Save → popup closes + success message
            cor_page.click_save()
            cor_page.wait_for_save_success(data["expected_save_success_message"])
            record_saved = True

            # Step 18: Delete copied record — try Draft / Updating
            cor_page.ensure_list_page_displayed(data["menu_search"])
            cor_page.delete_cost_of_route_on_tabs(
                data["route_code"],
                data["expected_delete_message"],
                data["vehicle_type"],
                tabs=[data["delete_tab"], "Updating", "Draft"],
            )
            cleanup_done = True
        finally:
            if record_saved and not cleanup_done:
                cor_page.cleanup_created_record(
                    menu_search=data["menu_search"],
                    expected_delete_message=data["expected_delete_message"],
                    route_code=data["route_code"],
                    vehicle_type=data["vehicle_type"],
                )

    @pytest.mark.parametrize(
        "data",
        DataProvider.etms_cases("test_tms_cor_001_reject_switch_updating_cost_of_route_etms"),
    )
    @pytest.mark.tc_id("TMS_COR_001")
    @pytest.mark.critical
    @pytest.mark.debug
    def test_tms_cor_001_reject_switch_updating_cost_of_route_etms(
        self,
        pages,
        data,
        login_etms,
    ):
        """TMS_COR_001 — create → send request → reject → switch to updating → delete."""
        login_etms(data["branch"])
        cor_page = pages.etms_cost_of_route_page

        cor_page.create_cost_of_route_record(data)
        cor_page.wait_for_save_success(data["expected_success_message"])

        cor_code = cor_page.capture_cor_code_after_save(
            data["route_code"],
            tabs=[data["tab_updating"], "Draft"],
        )
        cor_page.ensure_list_page_displayed(data["menu_search"])
        cor_page.open_tab_and_filter_cor_code(data["tab_updating"], cor_code)
        cor_page.send_request_from_updating(
            data["route_code"],
            data["vehicle_type"],
            expected_send_request_message=data["expected_send_request_message"],
        )

        cor_page.reject_cost_of_route_on_pending(data, cor_code)
        cor_page.switch_to_updating_from_rejected(data, cor_code)

        cor_page.open_tab_and_filter_cor_code(data["tab_updating"], cor_code)
        cor_page.delete_cost_of_route_by_cor_code(
            cor_code,
            data["expected_delete_message"],
        )
