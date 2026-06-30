import time

from playwright.sync_api import Locator

from automation.config import settings
from automation.logging import log_method, logger
from automation.pages.base_page import BasePage


def _sidebar_link_by_label(label: str) -> str:
    return (
        "xpath=//a[contains(@class,'nav-link')]"
        f"[.//span[normalize-space()='{label}']]"
    )


def _catalogue_submenu_link_by_label(label: str) -> str:
    return (
        "xpath=//ul[contains(@class,'submenu')]"
        f"//span[normalize-space()='{label}']"
        "/ancestor::a[contains(@class,'nav-link')][1]"
    )


def _sidebar_link_by_href(fragment: str, *, exclude_fragment: str | None = None) -> str:
    if exclude_fragment:
        return (
            f"xpath=//a[contains(@href,'{fragment}') "
            f"and not(contains(@href,'{exclude_fragment}'))]"
        )
    return f"a[href*='{fragment}']"


def _sidebar_child_link(parent_label: str, child_label: str) -> str:
    """Leaf/toggle link under a top-level sidebar section (e.g. Pricing > Common)."""
    return (
        "xpath=//a[contains(@class,'nav-link')]"
        f"[.//span[normalize-space()='{parent_label}']]"
        "/ancestor::li[1]"
        "//ul[contains(@class,'submenu') or contains(@class,'menu-content')]"
        f"//span[normalize-space()='{child_label}']"
        "/ancestor::a[contains(@class,'nav-link')][1]"
    )


def etms_page_title_selectors(title: str) -> list[str]:
    """Page title locators — ITL (h3.page-title) and VFC (h5.semibold / breadcrumb)."""
    return [
        f"xpath=//h3[normalize-space()='{title}']",
        f"h3:has-text('{title}')",
        f"xpath=//h5[normalize-space()='{title}']",
        f"h5:has-text('{title}')",
        f".page-title:has-text('{title}')",
        f"xpath=//*[contains(@class,'page-title') and normalize-space()='{title}']",
        (
            "xpath=//li[contains(@class,'breadcrumb-item') and contains(@class,'active')]"
            f"//span[normalize-space()='{title}']"
        ),
        (
            "xpath=//*[contains(@class,'page-title') "
            f"and contains(normalize-space(),'{title}')]"
        ),
    ]


def etms_pricing_filter_tab_selectors(tab_label: str) -> list[str]:
    """Pricing workflow tabs — VFC uses button/span inside ul.filter-tab; ITL may use anchor."""
    lit = tab_label.strip()
    return [
        (
            "xpath=//ul[contains(@class,'filter-tab')]"
            f"//button[normalize-space()='{lit}']"
        ),
        (
            "xpath=//ul[contains(@class,'filter-tab')]"
            f"//button[.//span[normalize-space()='{lit}']]"
        ),
        (
            "xpath=//ul[contains(@class,'filter-tab')]"
            f"//span[normalize-space()='{lit}']"
        ),
        (
            "xpath=//ul[contains(@class,'filter-tab')]"
            f"//a[normalize-space()='{lit}']"
        ),
        (
            "xpath=//ul[contains(@class,'filter-tab')]"
            f"//a[.//span[normalize-space()='{lit}']]"
        ),
        (
            f"xpath=//*[self::button or self::span or self::a]"
            f"[normalize-space()='{lit}' and ancestor::ul[contains(@class,'filter-tab')]]"
        ),
    ]


def etms_in_page_tab_selectors(tab_label: str) -> list[str]:
    """In-page tab locators — ITL (nav-tabs) and VFC (main-content a.nav-link)."""
    return [
        (
            "xpath=//div[contains(@class,'nav-tabs')]"
            f"//a[normalize-space()='{tab_label}']"
        ),
        (
            "xpath=//ul[contains(@class,'nav-tabs')]"
            f"//a[normalize-space()='{tab_label}']"
        ),
        (
            f"xpath=//a[contains(@class,'nav-link') and normalize-space()='{tab_label}' "
            "and not(ancestor::lth-sidebar) and not(ancestor::*[contains(@class,'sidebar-menu')])]"
        ),
        f"xpath=//*[@role='tab' and normalize-space()='{tab_label}']",
        (
            "xpath=//div[contains(@class,'ant-tabs-tab')]"
            f"[normalize-space()='{tab_label}']"
        ),
        (
            "xpath=//*[self::h3 or contains(@class,'page-title')]"
            "/ancestor::div[contains(@class,'m-portlet') or contains(@class,'portlet')][1]"
            f"//a[contains(@class,'nav-link') and normalize-space()='{tab_label}']"
        ),
        f"text='{tab_label}'",
    ]


def etms_sidebar_menu_selectors(
    parent_label: str,
    labels: tuple[str, ...],
    page_hash: str,
) -> list[str]:
    """Sidebar menu locators for a page under an optional parent section."""
    selectors: list[str] = []
    for label in labels:
        if parent_label:
            selectors.append(_sidebar_child_link(parent_label, label))
        selectors.extend(
            [
                _catalogue_submenu_link_by_label(label),
                (
                    "xpath=//a[contains(@class,'nav-link')]"
                    f"[.//span[normalize-space()='{label}']]"
                ),
            ]
        )
    selectors.append(_sidebar_link_by_href(page_hash))
    return list(dict.fromkeys(selectors))


def etms_in_page_tab_active_selectors(tab_label: str) -> list[str]:
    """Locators for an active in-page tab matching ``tab_label``."""
    lit = tab_label.strip()
    return [
        (
            "xpath=//div[contains(@class,'nav-tabs')]"
            f"//a[contains(@class,'active') and normalize-space()='{lit}']"
        ),
        (
            "xpath=//div[contains(@class,'main-content')]"
            f"//a[contains(@class,'nav-link') and contains(@class,'active') "
            f"and normalize-space()='{lit}']"
        ),
        (
            f"xpath=//a[contains(@class,'nav-link') and contains(@class,'active') "
            f"and normalize-space()='{lit}']"
        ),
        *etms_in_page_tab_selectors(lit),
    ]


def is_etms_in_page_tab_active(page: BasePage, tab_label: str) -> bool:
    """Return True when an in-page tab with ``tab_label`` has the active class."""
    for selector in etms_in_page_tab_active_selectors(tab_label):
        locator = page.page.locator(selector).first
        try:
            if locator.count() == 0:
                continue
            classes = locator.get_attribute("class") or ""
            if "active" in classes:
                return True
        except Exception:
            continue
    return False


class EtmsCatalogueMenuPage(BasePage):
    """Sidebar navigation — Catalogue menu group (eTMS nav-link sidebar)."""

    loading_overlay_selectors = [
        ".m-blockui",
        ".block-ui-wrapper.block-ui-active",
        "xpath=//div[contains(@class,'block-ui') and contains(@class,'active')]",
        "xpath=//div[contains(@class,'loading-mask')]",
        ".ng-progress-bar[active='true']",
    ]

    sidebar_ready_selectors = [
        "#cat > a.nav-link",
        "xpath=//li[@id='cat']//span[normalize-space()='Catalogue']",
        _sidebar_link_by_label("Catalogue"),
        "lth-sidebar .sidebar-menu",
        ".ftl-main-header",
    ]

    catalogue_menu_selectors = [
        "#cat > a.nav-link",
        (
            "xpath=//li[@id='cat']//span[normalize-space()='Catalogue']"
            "/ancestor::a[contains(@class,'nav-link')][1]"
        ),
        _sidebar_link_by_label("Catalogue"),
    ]

    catalogue_expanded_selectors = [
        "#catTransportNetwork > a.nav-link",
        "#catPartners > a.nav-link",
        "#catVehicles > a.nav-link",
        "#catDrivers > a.nav-link",
        "#catCommoditys > a.nav-link",
        _catalogue_submenu_link_by_label("Transport Network"),
        _catalogue_submenu_link_by_label("Partner"),
        _catalogue_submenu_link_by_label("Vehicle"),
        _catalogue_submenu_link_by_label("Driver list"),
        _catalogue_submenu_link_by_label("Commodity"),
        _sidebar_link_by_href("catalogue/charge"),
        (
            "xpath=//li[@id='cat']//ul[contains(@class,'menu-content')]"
            "//a[contains(@class,'nav-link')]"
        ),
    ]

    transport_network_toggle_selectors = [
        "#catTransportNetwork > a.nav-link",
        (
            "xpath=//li[@id='catTransportNetwork']"
            "//span[normalize-space()='Transport Network']"
            "/ancestor::a[contains(@class,'nav-link')][1]"
        ),
        _catalogue_submenu_link_by_label("Transport Network"),
    ]

    transport_network_submenu_selectors = [
        "#catOtherPlace > a.nav-link",
        (
            "xpath=//li[@id='catTransportNetwork']"
            "//li[@id='catOtherPlace']//a[contains(@class,'nav-link')]"
        ),
        _sidebar_link_by_href("catalogue/other-place"),
        _sidebar_link_by_label("Places"),
    ]

    partner_toggle_selectors = [
        "#catPartners > a.nav-link",
        (
            "xpath=//li[@id='catPartners']"
            "//span[normalize-space()='Partner']"
            "/ancestor::a[contains(@class,'nav-link')][1]"
        ),
        _catalogue_submenu_link_by_label("Partner"),
    ]

    partner_submenu_selectors = [
        "#catPartnerGroup > a.nav-link",
        (
            "xpath=//li[@id='catPartners']"
            "//li[@id='catPartnerGroup']//a[contains(@class,'nav-link')]"
        ),
        _sidebar_link_by_href("catalogue/partner-group"),
        _sidebar_link_by_label("Partner Group"),
    ]

    vehicle_toggle_selectors = [
        "#catVehicles > a.nav-link",
        (
            "xpath=//li[@id='catVehicles']"
            "//span[normalize-space()='Vehicle']"
            "/ancestor::a[contains(@class,'nav-link')][1]"
        ),
        _catalogue_submenu_link_by_label("Vehicle"),
    ]

    vehicle_submenu_selectors = [
        "#catVehicle > a.nav-link",
        (
            "xpath=//li[@id='catVehicles']"
            "//li[@id='catVehicle']//a[contains(@class,'nav-link')]"
        ),
        _sidebar_link_by_label("Vehicle List"),
        (
            "xpath=//a[contains(@href,'catalogue/vehicle') "
            "and not(contains(@href,'vehicle-'))]"
        ),
    ]

    driver_toggle_selectors = [
        "#catDrivers > a.nav-link",
        (
            "xpath=//li[@id='catDrivers']"
            "//span[normalize-space()='Driver list']"
            "/ancestor::a[contains(@class,'nav-link')][1]"
        ),
        _catalogue_submenu_link_by_label("Driver list"),
    ]

    driver_submenu_selectors = [
        "#catDriver > a.nav-link",
        (
            "xpath=//li[@id='catDrivers']"
            "//li[@id='catDriver']//a[contains(@class,'nav-link')]"
        ),
        _sidebar_link_by_href("catalogue/driver"),
        _sidebar_link_by_label("Driver"),
    ]

    commodity_toggle_selectors = [
        "#catCommoditys > a.nav-link",
        (
            "xpath=//li[@id='catCommoditys']"
            "//span[normalize-space()='Commodity']"
            "/ancestor::a[contains(@class,'nav-link')][1]"
        ),
        _catalogue_submenu_link_by_label("Commodity"),
    ]

    commodity_submenu_selectors = [
        "#catCommodity > a.nav-link",
        (
            "xpath=//li[@id='catCommoditys']"
            "//li[@id='catCommodity']//a[contains(@class,'nav-link')]"
        ),
        _sidebar_link_by_label("Commodity List"),
        (
            "xpath=//a[contains(@href,'catalogue/commodity') "
            "and not(contains(@href,'commodity-'))]"
        ),
    ]

    pricing_menu_selectors = [
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='Pricing']]",
        _sidebar_link_by_label("Pricing"),
    ]

    pricing_expanded_selectors = [
        _sidebar_child_link("Pricing", "Common"),
        _sidebar_child_link("Pricing", "FCL Pricing"),
        _sidebar_child_link("Pricing", "LCL Pricing"),
        _sidebar_child_link("Pricing", "Distribution Pricing"),
        _sidebar_child_link("Pricing", "Pricing Report"),
        _sidebar_child_link("Pricing", "Commission Rate Card"),
        _sidebar_link_by_href("pricing/common"),
        _sidebar_link_by_href("pricing/fcl"),
        _sidebar_link_by_href("pricing/rate-card-list"),
    ]

    pricing_common_toggle_selectors = [
        _sidebar_child_link("Pricing", "Common"),
        _sidebar_link_by_href("pricing/common"),
    ]

    pricing_common_expanded_selectors = [
        _sidebar_link_by_href("pricing/cost-of-route"),
        _sidebar_link_by_href("pricing/toll-buying"),
        _sidebar_child_link("Pricing", "Cost Of Route"),
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='Cost Of Route']]",
    ]

    pricing_fcl_toggle_selectors = [
        _sidebar_child_link("Pricing", "FCL Pricing"),
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='FCL Pricing']]",
    ]

    pricing_fcl_expanded_selectors = [
        _sidebar_link_by_href("pricing/fcl/fcl-rate-card-list"),
        _sidebar_link_by_href("pricing/fcl/fcl-buying"),
        _sidebar_link_by_href("pricing/fcl/fcl-renting-container"),
        _sidebar_link_by_href("pricing/fcl/fcl-renting-vehicle"),
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='FCL Rate Card List']]",
    ]

    pricing_lcl_toggle_selectors = [
        _sidebar_child_link("Pricing", "LCL Pricing"),
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='LCL Pricing']]",
    ]

    pricing_lcl_expanded_selectors = [
        _sidebar_link_by_href("pricing/rate-card-list"),
        _sidebar_link_by_href("pricing/buying"),
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='3. LCL Rate Card']]",
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='LCL Buying']]",
    ]

    pricing_distribution_toggle_selectors = [
        _sidebar_child_link("Pricing", "Distribution Pricing"),
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='Distribution Pricing']]",
    ]

    pricing_distribution_expanded_selectors = [
        _sidebar_link_by_href("pricing/dtb/dtb-rate-card-list"),
        _sidebar_link_by_href("pricing/buying-per-trip-v2"),
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='2. Distribution Rate Card']]",
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='Distribution Buying']]",
    ]

    pricing_report_expanded_selectors = [
        _sidebar_link_by_href("accounting/report"),
        _sidebar_link_by_href("pricing/commission-rate-card"),
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='Pricing Report']]",
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='Commission Rate Card']]",
    ]

    quotation_menu_selectors = [
        _sidebar_link_by_label("Quotation"),
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='Quotation']]",
    ]

    quotation_expanded_selectors = [
        _sidebar_child_link("Quotation", "Create FCL Quotation"),
        _sidebar_child_link("Quotation", "FCL Quotation List"),
        _sidebar_child_link("Quotation", "Create LCL Quotation"),
        _sidebar_child_link("Quotation", "Create Distribution Quotation"),
        _sidebar_link_by_href("quotation/fcl-quotation"),
        _sidebar_link_by_href("quotation/lcl-quotation"),
        _sidebar_link_by_href("quotation/dtb-create-rate-card"),
        _sidebar_link_by_href("pricing/fcl/fcl-quotation-list"),
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='Create FCL Quotation']]",
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='FCL Quotation List']]",
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='Create LCL Quotation']]",
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='Create Distribution Quotation']]",
    ]

    customer_service_menu_selectors = [
        _sidebar_link_by_label("Customer Service"),
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='Customer Service']]",
    ]

    customer_service_expanded_selectors = [
        _sidebar_child_link("Customer Service", "Common"),
        _sidebar_child_link("Customer Service", "FCL"),
        _sidebar_child_link("Customer Service", "LCL/FTL"),
        _sidebar_child_link("Customer Service", "SOA For Outsource"),
        _sidebar_child_link("Customer Service", "Verifying Booking"),
        _sidebar_link_by_href("customer-service/common"),
        _sidebar_link_by_href("customer/waybill-pending"),
        _sidebar_link_by_href("customer/fcl"),
        _sidebar_link_by_href("customer/lcl-ftl"),
        _sidebar_link_by_href("customer/soa-for-outsource"),
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='Common']]",
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='FCL']]",
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='LCL/FTL']]",
    ]

    customer_service_fcl_toggle_selectors = [
        _sidebar_child_link("Customer Service", "FCL"),
        _sidebar_link_by_href("customer/fcl"),
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='FCL']]",
    ]

    customer_service_fcl_expanded_selectors = [
        _sidebar_child_link("Customer Service", "FCL Booking"),
        _sidebar_child_link("Customer Service", "FCL Surcharge/ Behalf"),
        _sidebar_child_link("Customer Service", "Container Deposit Management"),
        _sidebar_child_link("Customer Service", "FCL Surcharge/ Behalf (Fleet)"),
        _sidebar_link_by_href("customer/fcl-booking"),
        _sidebar_link_by_href("customer/fcl-surcharge-behalf"),
        _sidebar_link_by_href("customer/management-container-deposit"),
        _sidebar_link_by_href("customer/fcl-surcharge-behalf-fleet"),
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='FCL Booking']]",
        (
            "xpath=//a[contains(@class,'nav-link')]"
            "[.//span[normalize-space()='FCL Surcharge/ Behalf']]"
        ),
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='Container Deposit Management']]",
        (
            "xpath=//a[contains(@class,'nav-link')]"
            "[.//span[normalize-space()='FCL Surcharge/ Behalf (Fleet)']]"
        ),
    ]

    customer_service_lcl_ftl_toggle_selectors = [
        _sidebar_child_link("Customer Service", "LCL/FTL"),
        _sidebar_link_by_href("customer/lcl-ftl"),
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='LCL/FTL']]",
    ]

    customer_service_lcl_ftl_expanded_selectors = [
        _sidebar_child_link("Customer Service", "LCL/FTL Booking"),
        _sidebar_child_link("Customer Service", "LCL/FTL Transport Surcharge"),
        _sidebar_child_link("Customer Service", "LCL/FTL Surcharge/Behalf"),
        _sidebar_child_link("Customer Service", "LCL Shipment Management"),
        _sidebar_child_link("Customer Service", "LCL/FTL Surcharge/ Behalf (Fleet)"),
        _sidebar_link_by_href("customer/booking"),
        _sidebar_link_by_href("customer/lcl-ftl-transport-surcharge"),
        _sidebar_link_by_href("customer/lcl-ftl-surcharge-behalf"),
        _sidebar_link_by_href("customer/lcl-shipment-management"),
        _sidebar_link_by_href("customer/lcl-ftl-surcharge-behalf-fleet"),
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='LCL/FTL Booking']]",
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='LCL/FTL Transport Surcharge']]",
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='LCL/FTL Surcharge/Behalf']]",
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='LCL Shipment Management']]",
        (
            "xpath=//a[contains(@class,'nav-link')]"
            "[.//span[normalize-space()='LCL/FTL Surcharge/ Behalf (Fleet)']]"
        ),
    ]

    customer_service_soa_outsource_selectors = [
        _sidebar_child_link("Customer Service", "SOA For Outsource"),
        _sidebar_link_by_href("customer/soa-for-outsource"),
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='SOA For Outsource']]",
    ]

    customer_service_common_toggle_selectors = [
        _sidebar_child_link("Customer Service", "Common"),
        _sidebar_link_by_href("customer-service/common"),
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='Common']]",
    ]

    customer_service_common_expanded_selectors = [
        _sidebar_child_link("Customer Service", "Verifying Booking"),
        _sidebar_link_by_href("customer/waybill-pending"),
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='Verifying Booking']]",
    ]

    operation_menu_selectors = [
        _sidebar_link_by_label("Operation"),
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='Operation']]",
    ]

    operation_expanded_selectors = [
        _sidebar_child_link("Operation", "Common"),
        _sidebar_child_link("Operation", "FCL"),
        _sidebar_child_link("Operation", "LCL/FTL"),
        _sidebar_child_link("Operation", "Update transport info"),
        _sidebar_link_by_href("operation/common/dispatching"),
        _sidebar_link_by_href("operation/fcl-transport-request"),
        _sidebar_link_by_href("operation/lcl/lcl-ftl-transport"),
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='Common']]",
    ]

    operation_common_toggle_selectors = [
        _sidebar_child_link("Operation", "Common"),
        _sidebar_link_by_href("operation/common/dispatching"),
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='Common']]",
    ]

    operation_common_expanded_selectors = [
        _sidebar_child_link("Operation", "Update transport info"),
        _sidebar_child_link("Operation", "Dispatching"),
        _sidebar_child_link("Operation", "Trip Settlement"),
        _sidebar_child_link("Operation", "Fuel Closing"),
        _sidebar_child_link("Operation", "Unlock Transport Request"),
        _sidebar_child_link("Operation", "Confirm ePOD"),
        _sidebar_link_by_href("customer/transport-data-entry"),
        _sidebar_link_by_href("operation/common/dispatching"),
        _sidebar_link_by_href("operation/common/settlement"),
        _sidebar_link_by_href("operation/common/fuel-checking"),
        _sidebar_link_by_href("operation/common/unlock-transport"),
        _sidebar_link_by_href("operation/common/confirm-pod"),
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='Update transport info']]",
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='Dispatching']]",
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='Trip Settlement']]",
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='Fuel Closing']]",
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='Unlock Transport Request']]",
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='Confirm ePOD']]",
    ]

    operation_fcl_toggle_selectors = [
        _sidebar_child_link("Operation", "FCL"),
        _sidebar_link_by_href("operation/fcl-transport-request"),
        "xpath=//a[contains(@class,'nav-link')]"
        "[.//span[normalize-space()='Operation']]"
        "/ancestor::li[1]"
        "//ul[contains(@class,'submenu') or contains(@class,'menu-content')]"
        "//a[contains(@class,'nav-link')][.//span[normalize-space()='FCL']]",
    ]

    operation_fcl_expanded_selectors = [
        _sidebar_child_link("Operation", "FCL Transport Request List"),
        _sidebar_link_by_href("operation/fcl-transport-request"),
        "xpath=//a[contains(@class,'nav-link')]"
        "[.//span[normalize-space()='FCL Transport Request List']]",
    ]

    operation_lcl_ftl_toggle_selectors = [
        _sidebar_child_link("Operation", "LCL/FTL"),
        _sidebar_link_by_href("operation/lcl/lcl-ftl-transport"),
        "xpath=//a[contains(@class,'nav-link')]"
        "[.//span[normalize-space()='Operation']]"
        "/ancestor::li[1]"
        "//ul[contains(@class,'submenu') or contains(@class,'menu-content')]"
        "//a[contains(@class,'nav-link')][.//span[normalize-space()='LCL/FTL']]",
    ]

    operation_lcl_ftl_expanded_selectors = [
        _sidebar_child_link("Operation", "LCL/FTL Transport Request List"),
        _sidebar_child_link("Operation", "2.Pickup Run Sheet"),
        _sidebar_child_link("Operation", "4.Revenue Protection"),
        _sidebar_child_link("Operation", "5.Routing"),
        _sidebar_child_link("Operation", "6.Consolidation"),
        _sidebar_child_link("Operation", "7.Check Out"),
        _sidebar_child_link("Operation", "8.Transit"),
        _sidebar_child_link("Operation", "9.Check In"),
        _sidebar_child_link("Operation", "11.Unbag"),
        _sidebar_child_link("Operation", "13.Delivery Run Sheet"),
        _sidebar_link_by_href("operation/lcl/lcl-ftl-transport"),
        _sidebar_link_by_href("operation/lcl/pickup-run-sheet"),
        _sidebar_link_by_href("operation/lcl/revenue-protection"),
        _sidebar_link_by_href("customer/lcl-routing"),
        _sidebar_link_by_href("operation/lcl/consolidation"),
        _sidebar_link_by_href("operation/lcl/check-out"),
        _sidebar_link_by_href("operation/lcl/transit"),
        _sidebar_link_by_href("operation/lcl/check-in"),
        _sidebar_link_by_href("operation/lcl/unbagging"),
        _sidebar_link_by_href("operation/lcl/delivery-run-sheet"),
        "xpath=//a[contains(@class,'nav-link')]"
        "[.//span[normalize-space()='LCL/FTL Transport Request List']]",
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='2.Pickup Run Sheet']]",
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='4.Revenue Protection']]",
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='5.Routing']]",
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='6.Consolidation']]",
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='7.Check Out']]",
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='8.Transit']]",
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='9.Check In']]",
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='11.Unbag']]",
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='13.Delivery Run Sheet']]",
    ]

    @log_method("Wait for eTMS sidebar navigation ready")
    def wait_for_sidebar_ready(self) -> "EtmsCatalogueMenuPage":
        self.wait_for_page_stable()
        self.wait_for_visible(
            self.sidebar_ready_selectors,
            "eTMS sidebar navigation",
        )
        return self

    def _is_menu_item_visible(self, selectors: list[str]) -> bool:
        return self.find_visible(selectors) is not None

    def _poll_until_overlay_hidden(self, timeout: int | None = None) -> bool:
        """Poll until loading overlays are gone. Returns False on timeout."""
        timeout = timeout or settings.browser_timeout
        deadline = time.monotonic() + timeout / 1000
        while time.monotonic() < deadline:
            if self.find_visible(self.loading_overlay_selectors) is None:
                return True
            self.page.wait_for_timeout(settings.polling_interval)
        return False

    def wait_for_catalogue_idle(self, timeout: int | None = None) -> "EtmsCatalogueMenuPage":
        """Wait until block-ui / loading overlays are gone before sidebar navigation."""
        timeout = timeout or settings.browser_timeout
        if self._poll_until_overlay_hidden(timeout):
            return self
        raise AssertionError(
            f"Catalogue page still loading — overlay active after {timeout}ms"
        )

    def _wait_for_url_hash(self, page_hash: str, timeout: int | None = None) -> None:
        timeout = timeout or settings.page_load_timeout
        normalized_hash = page_hash.lower().replace("_", "-")
        deadline = time.monotonic() + timeout / 1000
        while time.monotonic() < deadline:
            if normalized_hash in self.current_url.lower().replace("_", "-"):
                return
            self.page.wait_for_timeout(settings.polling_interval)
        raise AssertionError(
            f"URL hash '{page_hash}' not found after {timeout}ms. "
            f"Current URL: {self.current_url}"
        )

    def wait_before_next_catalogue_navigation(self) -> "EtmsCatalogueMenuPage":
        """Ensure current page data/overlay finished before clicking another menu."""
        self.wait_for_catalogue_idle()
        self.wait_for_page_stable()
        return self

    def _scroll_sidebar_link_into_view(self, link: Locator) -> None:
        """Scroll nested sidebar menu containers so leaf items (e.g. Currency) are clickable."""
        link.evaluate(
            "(el) => el.scrollIntoView({ block: 'center', inline: 'nearest' })"
        )
        link.scroll_into_view_if_needed()

    def _find_sidebar_link(self, selectors: list[str]) -> Locator | None:
        """Resolve nested sidebar links that exist in DOM but sit below the fold."""
        for selector in selectors:
            locator = self.page.locator(selector).first
            try:
                if locator.count() == 0:
                    continue
                self._scroll_sidebar_link_into_view(locator)
                if locator.is_visible():
                    logger.info(f"Found sidebar link by selector: {selector}")
                    return locator
            except Exception:
                continue
        return None

    def _click_sidebar_link(self, selectors: list[str], element_name: str) -> None:
        self.wait_before_next_catalogue_navigation()
        timeout = settings.browser_timeout
        deadline = time.monotonic() + timeout / 1000
        while time.monotonic() < deadline:
            link = self._find_sidebar_link(selectors)
            if link is not None:
                self.wait_for_page_stable()
                link.click(force=True)
                self.wait_for_page_stable()
                return
            self.page.wait_for_timeout(settings.polling_interval)
        raise AssertionError(self._build_wait_error(element_name, selectors, timeout))

    def _open_sidebar_submenu(
        self,
        *,
        toggle_selectors: list[str],
        submenu_selectors: list[str],
        toggle_label: str,
        ready_label: str,
    ) -> "EtmsCatalogueMenuPage":
        """Expand a sidebar section when its leaf submenu is not yet visible."""
        if not self._is_menu_item_visible(submenu_selectors):
            self._click_sidebar_link(toggle_selectors, toggle_label)
        self.wait_for_visible(submenu_selectors, ready_label)
        return self

    @log_method("Open Catalogue menu")
    def open_catalogue_menu(self) -> "EtmsCatalogueMenuPage":
        self.wait_for_sidebar_ready()
        return self._open_sidebar_submenu(
            toggle_selectors=self.catalogue_menu_selectors,
            submenu_selectors=self.catalogue_expanded_selectors,
            toggle_label="Catalogue menu",
            ready_label="Catalogue submenu",
        )

    @log_method("Open Transport Network menu")
    def open_transport_network_menu(self) -> "EtmsCatalogueMenuPage":
        self.open_catalogue_menu()
        return self._open_sidebar_submenu(
            toggle_selectors=self.transport_network_toggle_selectors,
            submenu_selectors=self.transport_network_submenu_selectors,
            toggle_label="Transport Network menu",
            ready_label="Places menu under Transport Network",
        )

    @log_method("Open Partner menu")
    def open_partner_menu(self) -> "EtmsCatalogueMenuPage":
        self.open_catalogue_menu()
        return self._open_sidebar_submenu(
            toggle_selectors=self.partner_toggle_selectors,
            submenu_selectors=self.partner_submenu_selectors,
            toggle_label="Partner menu",
            ready_label="Partner Group menu under Partner",
        )

    @log_method("Open Vehicle menu")
    def open_vehicle_menu(self) -> "EtmsCatalogueMenuPage":
        self.open_catalogue_menu()
        return self._open_sidebar_submenu(
            toggle_selectors=self.vehicle_toggle_selectors,
            submenu_selectors=self.vehicle_submenu_selectors,
            toggle_label="Vehicle menu",
            ready_label="Vehicle List menu under Vehicle",
        )

    @log_method("Open Driver list menu")
    def open_driver_menu(self) -> "EtmsCatalogueMenuPage":
        self.open_catalogue_menu()
        return self._open_sidebar_submenu(
            toggle_selectors=self.driver_toggle_selectors,
            submenu_selectors=self.driver_submenu_selectors,
            toggle_label="Driver list menu",
            ready_label="Driver menu under Driver list",
        )

    @log_method("Open Commodity menu")
    def open_commodity_menu(self) -> "EtmsCatalogueMenuPage":
        self.open_catalogue_menu()
        return self._open_sidebar_submenu(
            toggle_selectors=self.commodity_toggle_selectors,
            submenu_selectors=self.commodity_submenu_selectors,
            toggle_label="Commodity menu",
            ready_label="Commodity List menu under Commodity",
        )

    @log_method("Open Pricing menu")
    def open_pricing_menu(self) -> "EtmsCatalogueMenuPage":
        self.wait_for_sidebar_ready()
        return self._open_sidebar_submenu(
            toggle_selectors=self.pricing_menu_selectors,
            submenu_selectors=self.pricing_expanded_selectors,
            toggle_label="Pricing menu",
            ready_label="Pricing submenu",
        )

    @log_method("Open Pricing > Common menu")
    def open_pricing_common_menu(self) -> "EtmsCatalogueMenuPage":
        self.open_pricing_menu()
        return self._open_sidebar_submenu(
            toggle_selectors=self.pricing_common_toggle_selectors,
            submenu_selectors=self.pricing_common_expanded_selectors,
            toggle_label="Common menu under Pricing",
            ready_label="Cost Of Route menu under Common",
        )

    @log_method("Open Pricing > FCL Pricing menu")
    def open_pricing_fcl_menu(self) -> "EtmsCatalogueMenuPage":
        self.open_pricing_menu()
        return self._open_sidebar_submenu(
            toggle_selectors=self.pricing_fcl_toggle_selectors,
            submenu_selectors=self.pricing_fcl_expanded_selectors,
            toggle_label="FCL Pricing menu under Pricing",
            ready_label="FCL Rate Card List menu under FCL Pricing",
        )

    @log_method("Open Pricing > LCL Pricing menu")
    def open_pricing_lcl_menu(self) -> "EtmsCatalogueMenuPage":
        self.open_pricing_menu()
        return self._open_sidebar_submenu(
            toggle_selectors=self.pricing_lcl_toggle_selectors,
            submenu_selectors=self.pricing_lcl_expanded_selectors,
            toggle_label="LCL Pricing menu under Pricing",
            ready_label="3. LCL Rate Card menu under LCL Pricing",
        )

    @log_method("Open Pricing > Distribution Pricing menu")
    def open_pricing_distribution_menu(self) -> "EtmsCatalogueMenuPage":
        self.open_pricing_menu()
        return self._open_sidebar_submenu(
            toggle_selectors=self.pricing_distribution_toggle_selectors,
            submenu_selectors=self.pricing_distribution_expanded_selectors,
            toggle_label="Distribution Pricing menu under Pricing",
            ready_label="2. Distribution Rate Card menu under Distribution Pricing",
        )

    @log_method("Open Pricing > Pricing Report menu")
    def open_pricing_report_menu(self) -> "EtmsCatalogueMenuPage":
        self.open_pricing_menu()
        self.wait_for_visible(
            self.pricing_report_expanded_selectors,
            "Pricing Report menu under Pricing",
        )
        return self

    @log_method("Open Quotation menu")
    def open_quotation_menu(self) -> "EtmsCatalogueMenuPage":
        self.wait_for_sidebar_ready()
        return self._open_sidebar_submenu(
            toggle_selectors=self.quotation_menu_selectors,
            submenu_selectors=self.quotation_expanded_selectors,
            toggle_label="Quotation menu",
            ready_label="Create FCL Quotation menu under Quotation",
        )

    @log_method("Open Customer Service menu")
    def open_customer_service_menu(self) -> "EtmsCatalogueMenuPage":
        self.wait_for_sidebar_ready()
        return self._open_sidebar_submenu(
            toggle_selectors=self.customer_service_menu_selectors,
            submenu_selectors=self.customer_service_expanded_selectors,
            toggle_label="Customer Service menu",
            ready_label="Common menu under Customer Service",
        )

    @log_method("Open Customer Service > Common menu")
    def open_customer_service_common_menu(self) -> "EtmsCatalogueMenuPage":
        self.open_customer_service_menu()
        return self._open_sidebar_submenu(
            toggle_selectors=self.customer_service_common_toggle_selectors,
            submenu_selectors=self.customer_service_common_expanded_selectors,
            toggle_label="Common menu under Customer Service",
            ready_label="Verifying Booking menu under Common",
        )

    @log_method("Open Customer Service > FCL menu")
    def open_customer_service_fcl_menu(self) -> "EtmsCatalogueMenuPage":
        self.open_customer_service_menu()
        return self._open_sidebar_submenu(
            toggle_selectors=self.customer_service_fcl_toggle_selectors,
            submenu_selectors=self.customer_service_fcl_expanded_selectors,
            toggle_label="FCL menu under Customer Service",
            ready_label="FCL Booking menu under FCL",
        )

    @log_method("Open Customer Service > LCL/FTL menu")
    def open_customer_service_lcl_ftl_menu(self) -> "EtmsCatalogueMenuPage":
        self.open_customer_service_menu()
        return self._open_sidebar_submenu(
            toggle_selectors=self.customer_service_lcl_ftl_toggle_selectors,
            submenu_selectors=self.customer_service_lcl_ftl_expanded_selectors,
            toggle_label="LCL/FTL menu under Customer Service",
            ready_label="LCL/FTL Booking menu under LCL/FTL",
        )

    @log_method("Open Customer Service > SOA For Outsource menu")
    def open_customer_service_soa_outsource_menu(self) -> "EtmsCatalogueMenuPage":
        self.open_customer_service_menu()
        self.wait_for_visible(
            self.customer_service_soa_outsource_selectors,
            "SOA For Outsource menu under Customer Service",
        )
        return self

    @log_method("Open Operation menu")
    def open_operation_menu(self) -> "EtmsCatalogueMenuPage":
        self.wait_for_sidebar_ready()
        return self._open_sidebar_submenu(
            toggle_selectors=self.operation_menu_selectors,
            submenu_selectors=self.operation_expanded_selectors,
            toggle_label="Operation menu",
            ready_label="Common menu under Operation",
        )

    @log_method("Open Operation > Common menu")
    def open_operation_common_menu(self) -> "EtmsCatalogueMenuPage":
        self.open_operation_menu()
        return self._open_sidebar_submenu(
            toggle_selectors=self.operation_common_toggle_selectors,
            submenu_selectors=self.operation_common_expanded_selectors,
            toggle_label="Common menu under Operation",
            ready_label="Dispatching menu under Common",
        )

    @log_method("Open Operation > FCL menu")
    def open_operation_fcl_menu(self) -> "EtmsCatalogueMenuPage":
        self.open_operation_menu()
        return self._open_sidebar_submenu(
            toggle_selectors=self.operation_fcl_toggle_selectors,
            submenu_selectors=self.operation_fcl_expanded_selectors,
            toggle_label="FCL menu under Operation",
            ready_label="FCL Transport Request List menu under FCL",
        )

    @log_method("Open Operation > LCL/FTL menu")
    def open_operation_lcl_ftl_menu(self) -> "EtmsCatalogueMenuPage":
        self.open_operation_menu()
        return self._open_sidebar_submenu(
            toggle_selectors=self.operation_lcl_ftl_toggle_selectors,
            submenu_selectors=self.operation_lcl_ftl_expanded_selectors,
            toggle_label="LCL/FTL menu under Operation",
            ready_label="LCL/FTL Transport Request List menu under LCL/FTL",
        )

    maintenance_and_repair_menu_selectors = [
        _sidebar_link_by_label("Maintenance and Repair"),
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='Maintenance and Repair']]",
    ]

    maintenance_and_repair_expanded_selectors = [
        _sidebar_child_link("Maintenance and Repair", "Vehicle need maintaining"),
        _sidebar_child_link("Maintenance and Repair", "M&R Request"),
        _sidebar_child_link("Maintenance and Repair", "Maintenance Settlement"),
        _sidebar_child_link("Maintenance and Repair", "M&R Payment Request"),
        _sidebar_child_link("Maintenance and Repair", "Vehicle M&R Plan"),
        _sidebar_child_link("Maintenance and Repair", "Maintenance quota"),
        _sidebar_child_link("Maintenance and Repair", "Maintenance place"),
        _sidebar_child_link("Maintenance and Repair", "Vehicle Repair Level"),
        _sidebar_child_link("Maintenance and Repair", "M&R Type"),
        _sidebar_link_by_href("maintenance/main-vehicle-need-repair"),
        _sidebar_link_by_href("maintenance/maintenance-request"),
        _sidebar_link_by_href("maintenance/maintenance-vehicle"),
        _sidebar_link_by_href("maintenance/main-payment-request"),
        _sidebar_link_by_href("maintenance/maintenance-vehicle-mr-plan"),
        _sidebar_link_by_href("maintenance/main-maintenance-quota"),
        _sidebar_link_by_href("maintenance/main-vehicle-maintenance-place"),
        _sidebar_link_by_href("maintenance/main-vehicle-repair-level"),
        _sidebar_link_by_href("maintenance/maintenance-and-repair-type"),
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='Vehicle need maintaining']]",
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='M&R Request']]",
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='Maintenance Settlement']]",
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='M&R Payment Request']]",
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='Vehicle M&R Plan']]",
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='Maintenance quota']]",
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='Maintenance place']]",
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='Vehicle Repair Level']]",
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='M&R Type']]",
    ]

    @log_method("Open Maintenance and Repair menu")
    def open_maintenance_and_repair_menu(self) -> "EtmsCatalogueMenuPage":
        self.wait_for_sidebar_ready()
        return self._open_sidebar_submenu(
            toggle_selectors=self.maintenance_and_repair_menu_selectors,
            submenu_selectors=self.maintenance_and_repair_expanded_selectors,
            toggle_label="Maintenance and Repair menu",
            ready_label="Vehicle need maintaining menu under Maintenance and Repair",
        )

    material_management_menu_selectors = [
        _sidebar_link_by_label("Material Management"),
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='Material Management']]",
    ]

    material_management_expanded_selectors = [
        _sidebar_child_link("Material Management", "Import Material"),
        _sidebar_child_link("Material Management", "Export Material"),
        _sidebar_child_link("Material Management", "Closing material"),
        _sidebar_link_by_href("material/import-material-management"),
        _sidebar_link_by_href("material/export-material-management"),
        _sidebar_link_by_href("material/closing-material-management"),
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='Import Material']]",
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='Export Material']]",
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='Closing material']]",
    ]

    @log_method("Open Material Management menu")
    def open_material_management_menu(self) -> "EtmsCatalogueMenuPage":
        self.wait_for_sidebar_ready()
        return self._open_sidebar_submenu(
            toggle_selectors=self.material_management_menu_selectors,
            submenu_selectors=self.material_management_expanded_selectors,
            toggle_label="Material Management menu",
            ready_label="Import Material menu under Material Management",
        )

    @log_method("Open Reporting menu")
    def open_reporting_menu(self) -> "EtmsCatalogueMenuPage":
        """Reporting is a top-level sidebar page on VFC (not under Accounting)."""
        self.wait_for_sidebar_ready()
        return self

    accounting_menu_selectors = [
        _sidebar_link_by_label("Accounting"),
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='Accounting']]",
    ]

    accounting_expanded_selectors = [
        _sidebar_child_link("Accounting", "Accrual Of Costs"),
        _sidebar_child_link("Accounting", "Payment Request"),
        _sidebar_child_link("Accounting", "Fuel Transaction"),
        _sidebar_child_link("Accounting", "SOA list"),
        _sidebar_child_link("Accounting", "Revenue Accural"),
        _sidebar_child_link("Accounting", "Driver's Allowance"),
        _sidebar_link_by_href("accounting/cost-accrual"),
        _sidebar_link_by_href("accounting/payment-request"),
        _sidebar_link_by_href("accounting/fuel-transaction"),
        _sidebar_link_by_href("accounting/soa"),
        _sidebar_link_by_href("accounting/revenue"),
        _sidebar_link_by_href("accounting/salary-driver"),
        _sidebar_child_link("Accounting", "Unlock Trip Record"),
        _sidebar_link_by_href("customer/unlock-trip-record"),
        _sidebar_link_by_href("accounting/sys-parameter"),
    ]

    @log_method("Open Accounting menu")
    def open_accounting_menu(self) -> "EtmsCatalogueMenuPage":
        self.wait_for_sidebar_ready()
        return self._open_sidebar_submenu(
            toggle_selectors=self.accounting_menu_selectors,
            submenu_selectors=self.accounting_expanded_selectors,
            toggle_label="Accounting menu",
            ready_label="Accrual Of Costs menu under Accounting",
        )

    management_menu_selectors = [
        _sidebar_link_by_label("Management"),
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='Management']]",
    ]

    management_expanded_selectors = [
        _sidebar_child_link("Management", "Authorization"),
        _sidebar_link_by_href("management/authorization"),
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='Authorization']]",
    ]

    @log_method("Open Management menu")
    def open_management_menu(self) -> "EtmsCatalogueMenuPage":
        self.wait_for_sidebar_ready()
        return self._open_sidebar_submenu(
            toggle_selectors=self.management_menu_selectors,
            submenu_selectors=self.management_expanded_selectors,
            toggle_label="Management menu",
            ready_label="Authorization menu under Management",
        )

    system_menu_selectors = [
        _sidebar_link_by_label("System"),
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='System']]",
    ]

    system_expanded_selectors = [
        _sidebar_child_link("System", "User Info"),
        _sidebar_link_by_href("system/user-infor"),
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='User Info']]",
    ]

    @log_method("Open System menu")
    def open_system_menu(self) -> "EtmsCatalogueMenuPage":
        self.wait_for_sidebar_ready()
        return self._open_sidebar_submenu(
            toggle_selectors=self.system_menu_selectors,
            submenu_selectors=self.system_expanded_selectors,
            toggle_label="System menu",
            ready_label="User Info menu under System",
        )
