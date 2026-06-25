import pytest

from tests.data_provider import DataProvider
from tests.etms.etms_performance_support import (
    run_etms_catalogue_master_performance_suite,
    run_etms_commodity_performance_suite,
    run_etms_driver_performance_suite,
    run_etms_partner_performance_suite,
    run_etms_transport_network_performance_suite,
    run_etms_vehicle_performance_suite,
)

pytestmark = [
    pytest.mark.etms,
    pytest.mark.performance,
]


@pytest.mark.performance
class TestEtmsPerformance:
    @pytest.mark.parametrize(
        "data",
        DataProvider.etms_cases("test_etms_performance_transport_network_pages_etms"),
    )
    @pytest.mark.tc_id("PERF_TN_001")
    def test_etms_performance_transport_network_pages(
        self,
        pages,
        data,
        login_etms,
    ):
        """Login once → measure Transport Network list pages → assert all thresholds."""
        run_etms_transport_network_performance_suite(
            pages=pages,
            data=data,
            login_etms=login_etms,
        )

    @pytest.mark.parametrize(
        "data",
        DataProvider.etms_cases("test_etms_performance_partner_pages_etms"),
    )
    @pytest.mark.tc_id("PERF_PT_001")
    def test_etms_performance_partner_pages(
        self,
        pages,
        data,
        login_etms,
    ):
        """Login once → measure Catalogue > Partner list pages → assert all thresholds."""
        run_etms_partner_performance_suite(
            pages=pages,
            data=data,
            login_etms=login_etms,
        )

    @pytest.mark.parametrize(
        "data",
        DataProvider.etms_cases("test_etms_performance_vehicle_pages_etms"),
    )
    @pytest.mark.tc_id("PERF_VH_001")
    def test_etms_performance_vehicle_pages(
        self,
        pages,
        data,
        login_etms,
    ):
        """Login once → measure Catalogue > Vehicle list pages → assert all thresholds."""
        run_etms_vehicle_performance_suite(
            pages=pages,
            data=data,
            login_etms=login_etms,
        )

    @pytest.mark.parametrize(
        "data",
        DataProvider.etms_cases("test_etms_performance_driver_pages_etms"),
    )
    @pytest.mark.tc_id("PERF_DL_001")
    def test_etms_performance_driver_pages(
        self,
        pages,
        data,
        login_etms,
    ):
        """Login once → measure Catalogue > Driver list pages → assert all thresholds."""
        run_etms_driver_performance_suite(
            pages=pages,
            data=data,
            login_etms=login_etms,
        )

    @pytest.mark.parametrize(
        "data",
        DataProvider.etms_cases("test_etms_performance_commodity_pages_etms"),
    )
    @pytest.mark.tc_id("PERF_CM_001")
    def test_etms_performance_commodity_pages(
        self,
        pages,
        data,
        login_etms,
    ):
        """Login once → measure Catalogue > Commodity list pages → assert all thresholds."""
        run_etms_commodity_performance_suite(
            pages=pages,
            data=data,
            login_etms=login_etms,
        )

    @pytest.mark.parametrize(
        "data",
        DataProvider.etms_cases("test_etms_performance_catalogue_master_pages_etms"),
    )
    @pytest.mark.tc_id("PERF_CAT_001")
    def test_etms_performance_catalogue_master_pages(
        self,
        pages,
        data,
        login_etms,
    ):
        """Login once → measure Catalogue master list pages → assert all thresholds."""
        run_etms_catalogue_master_performance_suite(
            pages=pages,
            data=data,
            login_etms=login_etms,
        )
