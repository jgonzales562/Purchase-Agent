from __future__ import annotations
import os
from dataclasses import dataclass
from typing import Optional
from rich.console import Console

from .utils.browser import browser_context
from .sites.base import SiteDriver, PurchaseResult
from .registry import get_registry


@dataclass
class ShippingInfo:
    first_name: str
    last_name: str
    postal_code: str


class PurchaseAgent:
    def __init__(self, headed: bool = False, console: Optional[Console] = None) -> None:
        self.headed = headed
        self.console = console or Console()

    def _storage_path(self, site_key: str) -> str:
        base = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage")
        os.makedirs(base, exist_ok=True)
        return os.path.join(base, f"{site_key}.json")

    def purchase(
        self,
        site: str,
        product_name: str,
        confirm: bool = True,
        shipping: Optional[dict] = None,
    ) -> PurchaseResult:
        site_key = site.lower().strip()
        registry = get_registry()
        if site_key not in registry:
            raise ValueError(f"Unknown site '{site_key}'. Available: {', '.join(registry.keys())}")

        factory = registry[site_key]["factory"]  # type: ignore[index]
        driver: SiteDriver = factory()  # type: ignore[assignment]

        storage_path = self._storage_path(site_key)
        self.console.log(
            f"Launching browser (headed={self.headed}) for site '{site_key}' with storage='{storage_path}'"
        )
        with browser_context(
            headed=self.headed,
            storage_state_path=storage_path,
            save_storage_on_exit=True,
        ) as context:
            page = context.new_page()
            self.console.log(f"Starting purchase flow for '{product_name}' on '{site_key}'")
            result = driver.purchase(
                page=page,
                product_name=product_name,
                confirm=confirm,
                shipping=shipping or {},
                console=self.console,
            )
            return result
