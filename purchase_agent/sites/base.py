from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol, Optional, Optional as Opt
from playwright.sync_api import Page
from rich.console import Console


@dataclass
class PurchaseResult:
    success: bool
    message: str
    order_id: Optional[str] = None


@dataclass
class AvailabilityResult:
    in_stock: bool
    price: Optional[float] = None
    currency: str = "USD"
    message: str = ""


class SiteDriver(Protocol):
    key: str
    description: str

    def purchase(
        self,
        page: Page,
        product_name: str,
        confirm: bool,
        shipping: dict,
        console: Console,
    ) -> PurchaseResult:
        ...

    # Optional: If not implemented by a site, watcher will fall back to attempting purchase
    def check_availability(
        self,
        page: Page,
        product_name: str,
        console: Console,
    ) -> AvailabilityResult:
        ...
