from automation.pages.efms.commercial import (
    EfmsAgentPage,
    EfmsBookingReceiptPage,
    EfmsCustomerPage,
    EfmsWorkOrderPage,
)
from automation.pages.efms.logistics import (
    EfmsCustomClearancePage,
    EfmsJobManagementPage,
    EfmsTruckingInlandPage,
)
from automation.pages.efms.services import EfmsServicesDocumentationPage
from automation.pages.efms.efms_home_page import EfmsHomePage
from automation.pages.efms.efms_login_page import EfmsLoginPage

__all__ = [
    "EfmsLoginPage",
    "EfmsHomePage",
    "EfmsAgentPage",
    "EfmsCustomerPage",
    "EfmsWorkOrderPage",
    "EfmsBookingReceiptPage",
    "EfmsJobManagementPage",
    "EfmsCustomClearancePage",
    "EfmsTruckingInlandPage",
    "EfmsServicesDocumentationPage",
]
