from automation.config import settings
from automation.logging import log_method
from automation.pages.common.list_grid_component import ListGridComponent
from automation.pages.etms.etms_catalogue_menu_page import EtmsCatalogueMenuPage


class EtmsPlacesPage(EtmsCatalogueMenuPage):
    """Places list — Catalogue > Transport Network > Places."""

    places_page_hash = "catalogue/other-place"
    page_hash = places_page_hash

    places_menu_selectors = [
        "#catOtherPlace > a.nav-link",
        "xpath=//li[@id='catOtherPlace']//span[normalize-space()='Places']/ancestor::a[contains(@class,'nav-link')][1]",
        "a[href*='catalogue/other-place']",
    ]

    list_title_selectors = [
        "xpath=//h3[normalize-space()='Places']",
        "h3:has-text('Places')",
        "xpath=//*[contains(@class,'page-title') and contains(normalize-space(),'Places')]",
    ]

    list_table_selectors = [
        "xpath=//table[.//th[normalize-space()='Code']]//th",
        (
            "xpath=//*[self::h3 or contains(@class,'page-title')]"
            "[normalize-space()='Places' or contains(normalize-space(),'Places')]"
            "/ancestor::div[contains(@class,'m-portlet') or contains(@class,'portlet')][1]"
            "//table//th"
        ),
        "xpath=//th[normalize-space()='Code']",
    ]

    list_column_headers = [
        "Code",
        "Name (VI)",
    ]

    @property
    def list_grid(self) -> ListGridComponent:
        if not hasattr(self, "_list_grid"):
            self._list_grid = ListGridComponent(self, "Places list grid")
        return self._list_grid

    @log_method("Click Places menu")
    def click_places_menu(self) -> "EtmsPlacesPage":
        self.open_transport_network_menu()
        self._click_sidebar_link(
            self.places_menu_selectors,
            "Places menu",
        )

        self.page.wait_for_url(
            lambda url: self.places_page_hash in url.lower().replace("_", "-"),
            timeout=settings.page_load_timeout,
        )
        self.wait_for_page_stable()
        return self

    def load_page_for_performance(self, min_rows: int = 1) -> "EtmsPlacesPage":
        """Click Places and wait for table — used by performance tests (no POM step logs)."""
        self._click_sidebar_link(
            self.places_menu_selectors,
            "Places menu",
        )
        self.page.wait_for_url(
            lambda url: self.places_page_hash in url.lower().replace("_", "-"),
            timeout=settings.page_load_timeout,
        )
        self.wait_for_page_stable()
        self.wait_for_visible(
            self.list_title_selectors,
            "Places page title",
        )
        self.list_grid.wait_until_ready(
            self.list_table_selectors,
            "Places table",
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

    @log_method("Wait for Places list page shell")
    def wait_for_places_list_shell(self) -> "EtmsPlacesPage":
        self.wait_for_visible(
            self.list_title_selectors,
            "Places page title",
        )
        self.list_grid.wait_until_ready(
            self.list_table_selectors,
            "Places table",
        )
        return self

    @log_method("Wait for Places table data rows")
    def wait_for_places_table_data(self, min_rows: int = 1) -> "EtmsPlacesPage":
        self.wait_for_places_list_shell()
        self.list_grid.verify_column_headers(
            self.list_column_headers,
            table_selectors=self.list_table_selectors,
        )
        self.list_grid.wait_for_data_rows(
            min_rows=min_rows,
            table_selectors=self.list_table_selectors,
        )
        return self

    @log_method("Verify Places list page is displayed")
    def is_places_list_displayed(self, min_rows: int = 1) -> bool:
        self.wait_for_places_table_data(min_rows=min_rows)
        return self.places_page_hash in self.current_url.lower().replace("_", "-")
