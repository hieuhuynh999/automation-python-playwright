from automation.config import settings
from automation.logging import log_method
from automation.pages.common.list_grid_component import ListGridComponent
from automation.pages.etms.etms_catalogue_menu_page import EtmsCatalogueMenuPage


class EtmsDistanceBetweenPlacesPage(EtmsCatalogueMenuPage):
    """Distance Between Places — Catalogue > Transport Network > Distance Between Places."""

    page_hash = "catalogue/distance-between-places"

    menu_selectors = [
        "#catPlaceDistance > a.nav-link",
        (
            "xpath=//li[@id='catPlaceDistance']"
            "//span[normalize-space()='Distance Between Places']"
            "/ancestor::a[contains(@class,'nav-link')][1]"
        ),
        "a[href*='catalogue/distance-between-places']",
    ]

    list_title_selectors = [
        "xpath=//h3[normalize-space()='Distance Between Places']",
        "h3:has-text('Distance Between Places')",
        (
            "xpath=//*[contains(@class,'page-title') "
            "and contains(normalize-space(),'Distance Between Places')]"
        ),
    ]

    list_table_selectors = [
        "xpath=//table[.//th[normalize-space()='Place From']]//th",
        (
            "xpath=//*[self::h3 or contains(@class,'page-title')]"
            "[normalize-space()='Distance Between Places' "
            "or contains(normalize-space(),'Distance Between Places')]"
            "/ancestor::div[contains(@class,'m-portlet') or contains(@class,'portlet')][1]"
            "//table//th"
        ),
        "xpath=//th[normalize-space()='Place From']",
    ]

    list_column_headers = [
        "Place From",
        "Place To",
    ]

    @property
    def list_grid(self) -> ListGridComponent:
        if not hasattr(self, "_list_grid"):
            self._list_grid = ListGridComponent(self, "Distance Between Places list grid")
        return self._list_grid

    @log_method("Click Distance Between Places menu")
    def click_distance_between_places_menu(self) -> "EtmsDistanceBetweenPlacesPage":
        self.open_transport_network_menu()
        self._click_sidebar_link(
            self.menu_selectors,
            "Distance Between Places menu",
        )

        self.page.wait_for_url(
            lambda url: self.page_hash in url.lower().replace("_", "-"),
            timeout=settings.page_load_timeout,
        )
        self.wait_for_page_stable()
        return self

    def load_page_for_performance(self, min_rows: int = 1) -> "EtmsDistanceBetweenPlacesPage":
        """Click menu and wait for table — used by performance tests (no POM step logs)."""
        self._click_sidebar_link(
            self.menu_selectors,
            "Distance Between Places menu",
        )
        self.page.wait_for_url(
            lambda url: self.page_hash in url.lower().replace("_", "-"),
            timeout=settings.page_load_timeout,
        )
        self.wait_for_page_stable()
        self.wait_for_visible(
            self.list_title_selectors,
            "Distance Between Places page title",
        )
        self.list_grid.wait_until_ready(
            self.list_table_selectors,
            "Distance Between Places table",
        )
        self.list_grid.verify_column_headers(
            self.list_column_headers,
            table_selectors=self.list_table_selectors,
        )
        self.list_grid.wait_for_data_rows(
            min_rows=min_rows,
            table_selectors=self.list_table_selectors,
        )
        return self

    @log_method("Wait for Distance Between Places list page shell")
    def wait_for_list_shell(self) -> "EtmsDistanceBetweenPlacesPage":
        self.wait_for_visible(
            self.list_title_selectors,
            "Distance Between Places page title",
        )
        self.list_grid.wait_until_ready(
            self.list_table_selectors,
            "Distance Between Places table",
        )
        return self

    @log_method("Wait for Distance Between Places table data rows")
    def wait_for_table_data(self, min_rows: int = 1) -> "EtmsDistanceBetweenPlacesPage":
        self.wait_for_list_shell()
        self.list_grid.verify_column_headers(
            self.list_column_headers,
            table_selectors=self.list_table_selectors,
        )
        self.list_grid.wait_for_data_rows(
            min_rows=min_rows,
            table_selectors=self.list_table_selectors,
        )
        return self

    @log_method("Verify Distance Between Places list page is displayed")
    def is_list_displayed(self, min_rows: int = 1) -> bool:
        self.wait_for_table_data(min_rows=min_rows)
        return self.page_hash in self.current_url.lower().replace("_", "-")
