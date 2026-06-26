from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

import pytest

from tests.data_provider import DataProvider
from tests.etms.etms_performance_support import run_etms_performance_suite

pytestmark = [
    pytest.mark.etms,
    pytest.mark.vfc_etms,
    pytest.mark.performance,
]


@dataclass(frozen=True)
class _VfcPerformanceSuite:
    test_method: str
    json_key: str
    tc_id: str
    suite: str
    description: str
    provider: Literal["vfc", "etms"] = "vfc"
    use_setdefault: bool = False


_VFC_PERFORMANCE_SUITES: tuple[_VfcPerformanceSuite, ...] = (
    _VfcPerformanceSuite(
        "test_vfc_etms_performance_transport_network_pages",
        "test_vfc_etms_performance_transport_network_pages_etms",
        "PERF_TN_001",
        "transport_network",
        "VFC login once → measure Transport Network list pages → assert all thresholds.",
        use_setdefault=True,
    ),
    _VfcPerformanceSuite(
        "test_vfc_etms_performance_partner_pages",
        "test_etms_performance_partner_pages_etms",
        "PERF_PT_001",
        "partner",
        "VFC login once → measure Catalogue > Partner list pages → assert all thresholds.",
        provider="etms",
    ),
    _VfcPerformanceSuite(
        "test_vfc_etms_performance_vehicle_pages",
        "test_etms_performance_vehicle_pages_etms",
        "PERF_VH_001",
        "vehicle",
        "VFC login once → measure Catalogue > Vehicle list pages → assert all thresholds.",
        provider="etms",
    ),
    _VfcPerformanceSuite(
        "test_vfc_etms_performance_driver_pages",
        "test_etms_performance_driver_pages_etms",
        "PERF_DL_001",
        "driver",
        "VFC login once → measure Catalogue > Driver list pages → assert all thresholds.",
        provider="etms",
    ),
    _VfcPerformanceSuite(
        "test_vfc_etms_performance_commodity_pages",
        "test_etms_performance_commodity_pages_etms",
        "PERF_CM_001",
        "commodity",
        "VFC login once → measure Catalogue > Commodity list pages → assert all thresholds.",
        provider="etms",
    ),
    _VfcPerformanceSuite(
        "test_vfc_etms_performance_catalogue_master_pages",
        "test_etms_performance_catalogue_master_pages_etms",
        "PERF_CAT_001",
        "catalogue_master",
        "VFC login once → measure Catalogue master list pages → assert all thresholds.",
        provider="etms",
    ),
    _VfcPerformanceSuite(
        "test_vfc_etms_performance_pricing_common_pages",
        "test_vfc_etms_performance_pricing_common_pages_etms",
        "PERF_PR_001",
        "pricing_common",
        "VFC login once → measure Pricing > Common workflow tabs → assert all thresholds.",
    ),
    _VfcPerformanceSuite(
        "test_vfc_etms_performance_pricing_fcl_pages",
        "test_vfc_etms_performance_pricing_fcl_pages_etms",
        "PERF_FCL_001",
        "pricing_fcl",
        "VFC login once → measure Pricing > FCL Pricing workflow tabs → assert all thresholds.",
    ),
    _VfcPerformanceSuite(
        "test_vfc_etms_performance_pricing_lcl_pages",
        "test_vfc_etms_performance_pricing_lcl_pages_etms",
        "PERF_LCL_001",
        "pricing_lcl",
        "VFC login once → measure Pricing > LCL Pricing workflow tabs → assert all thresholds.",
    ),
    _VfcPerformanceSuite(
        "test_vfc_etms_performance_pricing_distribution_pages",
        "test_vfc_etms_performance_pricing_distribution_pages_etms",
        "PERF_DIST_001",
        "pricing_distribution",
        "VFC login once → measure Pricing > Distribution Pricing workflow tabs → assert all thresholds.",
    ),
    _VfcPerformanceSuite(
        "test_vfc_etms_performance_pricing_report_pages",
        "test_vfc_etms_performance_pricing_report_pages_etms",
        "PERF_PRPT_001",
        "pricing_report",
        "VFC login once → measure Pricing Report load & Commission Rate Card workflow tabs.",
    ),
    _VfcPerformanceSuite(
        "test_vfc_etms_performance_quotation_pages",
        "test_vfc_etms_performance_quotation_pages_etms",
        "PERF_QUOT_001",
        "quotation",
        "VFC login once → measure Quotation create forms & FCL Quotation List workflow tabs.",
    ),
    _VfcPerformanceSuite(
        "test_vfc_etms_performance_customer_service_pages",
        "test_vfc_etms_performance_customer_service_pages_etms",
        "PERF_CS_001",
        "customer_service_common",
        "VFC login once → measure Customer Service > Common > Verifying Booking list load.",
    ),
    _VfcPerformanceSuite(
        "test_vfc_etms_performance_customer_service_fcl_pages",
        "test_vfc_etms_performance_customer_service_fcl_pages_etms",
        "PERF_CS_FCL_001",
        "customer_service_fcl",
        "VFC login once → measure Customer Service > FCL pages & workflow tabs.",
    ),
    _VfcPerformanceSuite(
        "test_vfc_etms_performance_customer_service_lcl_ftl_pages",
        "test_vfc_etms_performance_customer_service_lcl_ftl_pages_etms",
        "PERF_CS_LCL_001",
        "customer_service_lcl_ftl",
        "VFC login once → measure Customer Service > LCL/FTL pages & workflow tabs.",
    ),
    _VfcPerformanceSuite(
        "test_vfc_etms_performance_customer_service_soa_outsource_pages",
        "test_vfc_etms_performance_customer_service_soa_outsource_pages_etms",
        "PERF_CS_SOA_001",
        "customer_service_soa_outsource",
        "VFC login once → measure Customer Service > SOA For Outsource workflow tabs.",
    ),
)


def _data_provider(provider: Literal["vfc", "etms"]) -> Callable[[str], list]:
    return (
        DataProvider.vfc_etms_cases
        if provider == "vfc"
        else DataProvider.etms_cases
    )


def _make_vfc_performance_test(spec: _VfcPerformanceSuite) -> Callable:
    provider = _data_provider(spec.provider)

    @pytest.mark.parametrize("data", provider(spec.json_key))
    @pytest.mark.tc_id(spec.tc_id)
    def test_method(self, pages, data, login_vfc_etms) -> None:
        run_etms_performance_suite(
            suite=spec.suite,
            pages=pages,
            data=data,
            login_etms=login_vfc_etms,
            use_setdefault=spec.use_setdefault,
        )

    test_method.__name__ = spec.test_method
    test_method.__doc__ = spec.description
    return test_method


@pytest.mark.performance
class TestVfcEtmsPerformance:
    pass


for _spec in _VFC_PERFORMANCE_SUITES:
    setattr(
        TestVfcEtmsPerformance,
        _spec.test_method,
        _make_vfc_performance_test(_spec),
    )
