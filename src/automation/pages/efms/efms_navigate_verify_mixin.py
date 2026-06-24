from __future__ import annotations

from automation.config import settings
from automation.pages.common.list_grid_component import ListGridComponent
from automation.pages.common.shipment_list_component import ShipmentListComponent


class EfmsNavigateVerifyMixin:
    """Shared navigate verification — ngx-datatable grids and Services shipment cards."""

    @property
    def list_grid(self) -> ListGridComponent:
        if not hasattr(self, "_list_grid"):
            self._list_grid = ListGridComponent(self, "List grid")
        return self._list_grid

    @property
    def shipment_list(self) -> ShipmentListComponent:
        if not hasattr(self, "_shipment_list"):
            self._shipment_list = ShipmentListComponent(self, "Shipment list")
        return self._shipment_list

    def _verify_list_page_displayed(
        self,
        hash_fragment: str,
        title_selectors: list[str],
        table_selectors: list[str],
        title_name: str,
        table_name: str,
        column_headers: list[str],
        min_rows: int = 1,
    ) -> bool:
        self.wait_for_visible(title_selectors, title_name)
        self.list_grid.wait_until_ready(table_selectors, table_name)
        self.list_grid.verify_column_headers(column_headers, table_selectors=table_selectors)
        self.list_grid.wait_for_data_rows(min_rows=min_rows, table_selectors=table_selectors)
        return hash_fragment in self.current_url

    def _verify_shipment_page_displayed(
        self,
        hash_fragment: str,
        title_selectors: list[str],
        title_name: str,
        shipment_item_selectors: list[str],
        shipment_item_name: str = "Shipment list",
        min_shipment_items: int = 1,
    ) -> bool:
        self.wait_for_visible(
            title_selectors,
            title_name,
            timeout=settings.page_load_timeout,
        )
        self.shipment_list.wait_for_items(
            shipment_item_selectors,
            shipment_item_name,
            min_items=min_shipment_items,
        )
        return hash_fragment in self.current_url
