import pytest

from tests.data_provider import DataProvider
from tests.etms.etms_performance_support import run_etms_performance_suite

pytestmark = [
    pytest.mark.etms,
    pytest.mark.vfc_etms,
    pytest.mark.performance,
]


@pytest.mark.performance
class TestVfcEtmsPerformance:
    @pytest.mark.parametrize(
        "data",
        DataProvider.vfc_etms_cases("test_vfc_etms_performance_transport_network_pages_etms"),
    )
    @pytest.mark.tc_id("PERF_VFC_001")
    def test_vfc_etms_performance_transport_network_pages(
        self, pages, data, login_vfc_etms
    ):
        """VFC login once → measure Transport Network list pages → assert all thresholds."""
        run_etms_performance_suite(
            suite="transport_network",
            pages=pages,
            data=data,
            login_etms=login_vfc_etms,
            use_setdefault=True,
        )

    @pytest.mark.parametrize(
        "data",
        DataProvider.vfc_etms_cases("test_vfc_etms_performance_partner_pages_etms"),
    )
    @pytest.mark.tc_id("PERF_VFC_002")
    def test_vfc_etms_performance_partner_pages(self, pages, data, login_vfc_etms):
        """VFC login once → measure Catalogue > Partner list pages → assert all thresholds."""
        run_etms_performance_suite(
            suite="partner",
            pages=pages,
            data=data,
            login_etms=login_vfc_etms,
        )

    @pytest.mark.parametrize(
        "data",
        DataProvider.vfc_etms_cases("test_vfc_etms_performance_vehicle_pages_etms"),
    )
    @pytest.mark.tc_id("PERF_VFC_003")
    def test_vfc_etms_performance_vehicle_pages(self, pages, data, login_vfc_etms):
        """VFC login once → measure Catalogue > Vehicle list pages → assert all thresholds."""
        run_etms_performance_suite(
            suite="vehicle",
            pages=pages,
            data=data,
            login_etms=login_vfc_etms,
        )

    @pytest.mark.parametrize(
        "data",
        DataProvider.vfc_etms_cases("test_vfc_etms_performance_driver_pages_etms"),
    )
    @pytest.mark.tc_id("PERF_VFC_004")
    def test_vfc_etms_performance_driver_pages(self, pages, data, login_vfc_etms):
        """VFC login once → measure Catalogue > Driver list pages → assert all thresholds."""
        run_etms_performance_suite(
            suite="driver",
            pages=pages,
            data=data,
            login_etms=login_vfc_etms,
        )

    @pytest.mark.parametrize(
        "data",
        DataProvider.vfc_etms_cases("test_vfc_etms_performance_commodity_pages_etms"),
    )
    @pytest.mark.tc_id("PERF_VFC_005")
    def test_vfc_etms_performance_commodity_pages(self, pages, data, login_vfc_etms):
        """VFC login once → measure Catalogue > Commodity list pages → assert all thresholds."""
        run_etms_performance_suite(
            suite="commodity",
            pages=pages,
            data=data,
            login_etms=login_vfc_etms,
        )

    @pytest.mark.parametrize(
        "data",
        DataProvider.vfc_etms_cases("test_vfc_etms_performance_catalogue_master_pages_etms"),
    )
    @pytest.mark.tc_id("PERF_VFC_006")
    def test_vfc_etms_performance_catalogue_master_pages(
        self, pages, data, login_vfc_etms
    ):
        """VFC login once → measure Catalogue master list pages → assert all thresholds."""
        run_etms_performance_suite(
            suite="catalogue_master",
            pages=pages,
            data=data,
            login_etms=login_vfc_etms,
        )

    @pytest.mark.parametrize(
        "data",
        DataProvider.vfc_etms_cases("test_vfc_etms_performance_pricing_common_pages_etms"),
    )
    @pytest.mark.tc_id("PERF_VFC_007")
    def test_vfc_etms_performance_pricing_common_pages(
        self, pages, data, login_vfc_etms
    ):
        """VFC login once → measure Pricing > Common workflow tabs → assert all thresholds."""
        run_etms_performance_suite(
            suite="pricing_common",
            pages=pages,
            data=data,
            login_etms=login_vfc_etms,
        )

    @pytest.mark.parametrize(
        "data",
        DataProvider.vfc_etms_cases("test_vfc_etms_performance_pricing_fcl_pages_etms"),
    )
    @pytest.mark.tc_id("PERF_VFC_008")
    def test_vfc_etms_performance_pricing_fcl_pages(self, pages, data, login_vfc_etms):
        """VFC login once → measure Pricing > FCL Pricing workflow tabs → assert all thresholds."""
        run_etms_performance_suite(
            suite="pricing_fcl",
            pages=pages,
            data=data,
            login_etms=login_vfc_etms,
        )

    @pytest.mark.parametrize(
        "data",
        DataProvider.vfc_etms_cases("test_vfc_etms_performance_pricing_lcl_pages_etms"),
    )
    @pytest.mark.tc_id("PERF_VFC_009")
    def test_vfc_etms_performance_pricing_lcl_pages(self, pages, data, login_vfc_etms):
        """VFC login once → measure Pricing > LCL Pricing workflow tabs → assert all thresholds."""
        run_etms_performance_suite(
            suite="pricing_lcl",
            pages=pages,
            data=data,
            login_etms=login_vfc_etms,
        )

    @pytest.mark.parametrize(
        "data",
        DataProvider.vfc_etms_cases(
            "test_vfc_etms_performance_pricing_distribution_pages_etms"
        ),
    )
    @pytest.mark.tc_id("PERF_VFC_010")
    def test_vfc_etms_performance_pricing_distribution_pages(
        self, pages, data, login_vfc_etms
    ):
        """VFC login once → measure Pricing > Distribution Pricing workflow tabs."""
        run_etms_performance_suite(
            suite="pricing_distribution",
            pages=pages,
            data=data,
            login_etms=login_vfc_etms,
        )

    @pytest.mark.parametrize(
        "data",
        DataProvider.vfc_etms_cases("test_vfc_etms_performance_pricing_report_pages_etms"),
    )
    @pytest.mark.tc_id("PERF_VFC_011")
    def test_vfc_etms_performance_pricing_report_pages(
        self, pages, data, login_vfc_etms
    ):
        """VFC login once → measure Pricing Report & Commission Rate Card tabs."""
        run_etms_performance_suite(
            suite="pricing_report",
            pages=pages,
            data=data,
            login_etms=login_vfc_etms,
        )

    @pytest.mark.parametrize(
        "data",
        DataProvider.vfc_etms_cases("test_vfc_etms_performance_quotation_pages_etms"),
    )
    @pytest.mark.tc_id("PERF_VFC_012")
    def test_vfc_etms_performance_quotation_pages(self, pages, data, login_vfc_etms):
        """VFC login once → measure Quotation create forms & FCL Quotation List tabs."""
        run_etms_performance_suite(
            suite="quotation",
            pages=pages,
            data=data,
            login_etms=login_vfc_etms,
        )

    @pytest.mark.parametrize(
        "data",
        DataProvider.vfc_etms_cases("test_vfc_etms_performance_customer_service_pages_etms"),
    )
    @pytest.mark.tc_id("PERF_VFC_013")
    def test_vfc_etms_performance_customer_service_pages(
        self, pages, data, login_vfc_etms
    ):
        """VFC login once → measure Customer Service > Common > Verifying Booking."""
        run_etms_performance_suite(
            suite="customer_service_common",
            pages=pages,
            data=data,
            login_etms=login_vfc_etms,
        )

    @pytest.mark.parametrize(
        "data",
        DataProvider.vfc_etms_cases(
            "test_vfc_etms_performance_customer_service_fcl_pages_etms"
        ),
    )
    @pytest.mark.tc_id("PERF_VFC_014")
    def test_vfc_etms_performance_customer_service_fcl_pages(
        self, pages, data, login_vfc_etms
    ):
        """VFC login once → measure Customer Service > FCL pages & workflow tabs."""
        run_etms_performance_suite(
            suite="customer_service_fcl",
            pages=pages,
            data=data,
            login_etms=login_vfc_etms,
        )

    @pytest.mark.parametrize(
        "data",
        DataProvider.vfc_etms_cases(
            "test_vfc_etms_performance_customer_service_lcl_ftl_pages_etms"
        ),
    )
    @pytest.mark.tc_id("PERF_VFC_015")
    def test_vfc_etms_performance_customer_service_lcl_ftl_pages(
        self, pages, data, login_vfc_etms
    ):
        """VFC login once → measure Customer Service > LCL/FTL pages & workflow tabs."""
        run_etms_performance_suite(
            suite="customer_service_lcl_ftl",
            pages=pages,
            data=data,
            login_etms=login_vfc_etms,
        )

    @pytest.mark.parametrize(
        "data",
        DataProvider.vfc_etms_cases(
            "test_vfc_etms_performance_customer_service_soa_outsource_pages_etms"
        ),
    )
    @pytest.mark.tc_id("PERF_VFC_016")
    def test_vfc_etms_performance_customer_service_soa_outsource_pages(
        self, pages, data, login_vfc_etms
    ):
        """VFC login once → measure Customer Service > SOA For Outsource workflow tabs."""
        run_etms_performance_suite(
            suite="customer_service_soa_outsource",
            pages=pages,
            data=data,
            login_etms=login_vfc_etms,
        )

    @pytest.mark.parametrize(
        "data",
        DataProvider.vfc_etms_cases("test_vfc_etms_performance_operation_common_pages_etms"),
    )
    @pytest.mark.tc_id("PERF_VFC_017")
    def test_vfc_etms_performance_operation_common_pages(
        self, pages, data, login_vfc_etms
    ):
        """VFC login once → measure Operation > Common pages & workflow tabs."""
        run_etms_performance_suite(
            suite="operation_common",
            pages=pages,
            data=data,
            login_etms=login_vfc_etms,
        )

    @pytest.mark.parametrize(
        "data",
        DataProvider.vfc_etms_cases("test_vfc_etms_performance_operation_fcl_pages_etms"),
    )
    @pytest.mark.tc_id("PERF_VFC_018")
    def test_vfc_etms_performance_operation_fcl_pages(
        self, pages, data, login_vfc_etms
    ):
        """VFC login once → measure Operation > FCL > FCL Transport Request List."""
        run_etms_performance_suite(
            suite="operation_fcl",
            pages=pages,
            data=data,
            login_etms=login_vfc_etms,
        )

    @pytest.mark.parametrize(
        "data",
        DataProvider.vfc_etms_cases(
            "test_vfc_etms_performance_operation_lcl_ftl_pages_etms"
        ),
    )
    @pytest.mark.tc_id("PERF_VFC_019")
    def test_vfc_etms_performance_operation_lcl_ftl_pages(
        self, pages, data, login_vfc_etms
    ):
        """VFC login once → measure Operation > LCL/FTL pages (grid + action controls)."""
        run_etms_performance_suite(
            suite="operation_lcl_ftl",
            pages=pages,
            data=data,
            login_etms=login_vfc_etms,
        )
