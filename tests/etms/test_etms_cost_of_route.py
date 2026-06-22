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

        # Step 1: Search menu → open Cost Of Route page
        cor_page.open_via_menu_search(data["menu_search"])
        assert cor_page.is_list_page_displayed()

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
        cor_page.wait_for_add_modal_closed()
        assert cor_page.is_success_message_displayed(data["expected_success_message"])

        # Step 7: action-btn → Delete → confirm
        cor_page.ensure_list_page_displayed(data["menu_search"])
        cor_page.click_row_action_btn(data["route_code"], data["vehicle_type"])
        cor_page.click_row_delete_button(data["route_code"], data["vehicle_type"])
        assert cor_page.is_delete_confirm_displayed()
        cor_page.click_delete_confirm_ok()
        assert cor_page.is_success_message_displayed(data["expected_delete_message"])
