import pytest

from tests.data_provider import DataProvider


@pytest.mark.efms
@pytest.mark.regression
class TestEfmsBookingReceipt:
    """FMS_BR_001 – FMS_BR_005: Booking Receipt CRUD flow (run in order)."""

    booking_no: str | None = None

    @pytest.mark.parametrize(
        "data",
        DataProvider.efms_cases("test_fms_br_001_open_add_booking_receipt_efms"),
    )
    @pytest.mark.tc_id("FMS_BR_001")
    def test_fms_br_001_open_add_booking_receipt_efms(
        self,
        pages,
        data,
        login_efms,
    ):
        login_efms(data["company"])

        # Step 1: Open Booking Receipt page
        pages.efms_booking_receipt_page.open_list_page()

        # Step 2: Click Add new
        pages.efms_booking_receipt_page.click_add_new()

        # Step 3: Click Air Export
        pages.efms_booking_receipt_page.click_add_new_option(data["add_option"])

        # Expected: Add New Booking Receipt form displayed
        assert pages.efms_booking_receipt_page.is_add_form_displayed()

    @pytest.mark.parametrize(
        "data",
        DataProvider.efms_cases("test_fms_br_002_create_booking_receipt_efms"),
    )
    @pytest.mark.tc_id("FMS_BR_002")
    def test_fms_br_002_create_booking_receipt_efms(
        self,
        pages,
        data,
        login_efms,
    ):
        login_efms(data["company"])
        br_page = pages.efms_booking_receipt_page

        br_page.open_list_page()
        br_page.click_add_new()
        br_page.click_add_new_option(data["add_option"])
        assert br_page.is_add_form_displayed()

        # Steps 1–9: Fill create form (BR_ADD_001)
        br_page.fill_create_form(data)

        # Step 10: Save
        br_page.click_save()

        # Step 11: Confirm Yes
        br_page.click_confirm_yes()

        # Expected 1: Success message
        assert br_page.is_message_displayed(data["expected_success_message"])

        # Expected 2: Capture booking_no from grid row matching created data
        br_page.open_list_page()
        assert br_page.is_booking_receipt_displayed()
        TestEfmsBookingReceipt.booking_no = br_page.get_booking_no_from_grid_row_containing(
            data["shipper"]
        )
        if not TestEfmsBookingReceipt.booking_no:
            TestEfmsBookingReceipt.booking_no = br_page.get_first_booking_no_from_grid()
        assert TestEfmsBookingReceipt.booking_no, "Cannot capture booking_no after create"

    @pytest.mark.parametrize(
        "data",
        DataProvider.efms_cases("test_fms_br_003_open_detail_booking_receipt_efms"),
    )
    @pytest.mark.tc_id("FMS_BR_003")
    def test_fms_br_003_open_detail_booking_receipt_efms(
        self,
        pages,
        data,
        login_efms,
    ):
        booking_no = TestEfmsBookingReceipt.booking_no
        if not booking_no:
            pytest.skip("Requires booking_no from FMS_BR_002")

        login_efms(data["company"])
        br_page = pages.efms_booking_receipt_page

        # Step 1: Open Booking Receipt page
        br_page.open_list_page()

        # Step 2: Search created Booking Receipt
        br_page.search_booking(booking_no)

        # Step 3: Click Booking No
        br_page.click_booking_no(booking_no)

        # Expected: Detail page displayed
        assert br_page.is_detail_displayed()

    @pytest.mark.parametrize(
        "data",
        DataProvider.efms_cases("test_fms_br_004_update_booking_receipt_efms"),
    )
    @pytest.mark.tc_id("FMS_BR_004")
    def test_fms_br_004_update_booking_receipt_efms(
        self,
        pages,
        data,
        login_efms,
    ):
        booking_no = TestEfmsBookingReceipt.booking_no
        if not booking_no:
            pytest.skip("Requires booking_no from FMS_BR_002")

        login_efms(data["company"])
        br_page = pages.efms_booking_receipt_page

        br_page.open_list_page()
        br_page.search_booking(booking_no)
        br_page.click_booking_no(booking_no)
        assert br_page.is_detail_displayed()

        # Steps 1–4: Update fields (BR_UPDATE_001)
        br_page.fill_update_form(data)

        # Step 5: Save
        br_page.click_save()

        # Expected 1: Success message
        assert br_page.is_message_displayed(data["expected_success_message"])

        # Expected 2: Still on detail page
        assert br_page.is_detail_displayed()

        # Expected 3: Status remains Draft for delete step
        br_page.open_list_page()
        status = br_page.get_booking_status_in_grid(booking_no)
        assert status == "Draft", f"Expected Draft after update, got: {status}"

    @pytest.mark.parametrize(
        "data",
        DataProvider.efms_cases("test_fms_br_005_delete_booking_receipt_efms"),
    )
    @pytest.mark.tc_id("FMS_BR_005")
    def test_fms_br_005_delete_booking_receipt_efms(
        self,
        pages,
        data,
        login_efms,
    ):
        booking_no = TestEfmsBookingReceipt.booking_no
        if not booking_no:
            pytest.skip("Requires booking_no from FMS_BR_002")

        login_efms(data["company"])
        br_page = pages.efms_booking_receipt_page

        # Step 1: Open list, refresh grid, then delete with full wait chain (popup/API/toast/grid)
        br_page.open_list_page()
        br_page.refresh_list_page()

        br_page.delete_booking_receipt_from_grid(
            booking_no,
            data["expected_success_message"],
        )

        # Re-open list page and verify again to avoid false-positive from transient DOM updates.
        br_page.open_list_page()
        assert br_page.wait_until_booking_absent(booking_no), (
            f"Booking {booking_no} still exists after reload. "
            f"row='{br_page.get_booking_row_text(booking_no)}'"
        )
