from __future__ import annotations
import os
import random
import time
from datetime import datetime, timedelta
from typing import Optional
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table

from .utils.browser import browser_context
from .utils.notify import notify_slack
from .registry import get_registry
from .sites.base import SiteDriver, AvailabilityResult, PurchaseResult


def watch_and_purchase(
    *,
    site: str,
    product_name: str,
    interval_seconds: int = 15,
    timeout_seconds: Optional[int] = None,
    price_max: Optional[float] = None,
    headed: bool = False,
    auto_confirm: bool = True,
    shipping: Optional[dict] = None,
    console: Optional[Console] = None,
    jitter: float = 0.2,
    webhook_url: Optional[str] = None,
) -> PurchaseResult:
    console = console or Console()
    registry = get_registry()
    site_key = site.lower().strip()
    if site_key not in registry:
        raise ValueError(f"Unknown site '{site_key}'. Available: {', '.join(registry.keys())}")

    factory = registry[site_key]["factory"]  # type: ignore[index]
    driver: SiteDriver = factory()  # type: ignore[assignment]

    deadline = datetime.utcnow() + timedelta(seconds=timeout_seconds) if timeout_seconds else None
    # Resolve webhook from env if not provided
    if webhook_url is None:
        webhook_url = os.getenv("PURCHASE_AGENT_WEBHOOK")

    console.log(
        f"Watching '{product_name}' on '{site_key}' every {interval_seconds}s"
        + (f", price <= ${price_max:.2f}" if price_max is not None else "")
        + (f", timeout {timeout_seconds}s" if timeout_seconds else "")
    )

    # Prepare persistent storage per site
    storage_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage")
    os.makedirs(storage_dir, exist_ok=True)
    storage_path = os.path.join(storage_dir, f"{site_key}.json")

    with browser_context(
        headed=headed,
        storage_state_path=storage_path,
        save_storage_on_exit=True,
    ) as context:
        page = context.new_page()

        last_status = "Starting"
        def render_status(avail: Optional[AvailabilityResult]) -> Panel:
            table = Table.grid(padding=(0,1))
            table.add_row("Product:", product_name)
            table.add_row("Site:", site_key)
            table.add_row("Status:", avail.message if avail else last_status)
            if avail and avail.price is not None:
                table.add_row("Price:", f"${avail.price:.2f} {avail.currency}")
            table.add_row("Interval:", f"{interval_seconds}s ±{int(jitter*100)}%")
            if deadline:
                remaining = max((deadline - datetime.utcnow()).total_seconds(), 0)
                table.add_row("Time left:", f"{int(remaining)}s")
            return Panel(table, title="Watch & Purchase", border_style="cyan")

        with Live(render_status(None), console=console, refresh_per_second=4):
            while True:
                if deadline and datetime.utcnow() >= deadline:
                    return PurchaseResult(success=False, message="Timeout reached while watching")

                try:
                    # Try availability if implemented
                    avail: Optional[AvailabilityResult] = None
                    if hasattr(driver, "check_availability"):
                        avail = driver.check_availability(page=page, product_name=product_name, console=console)  # type: ignore[attr-defined]
                    else:
                        last_status = "Driver has no availability check; attempting purchase directly"

                    if avail:
                        last_status = avail.message
                        console.log(f"Availability: in_stock={avail.in_stock}, price={avail.price}")
                        if avail.in_stock and (price_max is None or (avail.price is not None and avail.price <= price_max)):
                            # Notify before purchase if webhook configured
                            if webhook_url:
                                try:
                                    notify_slack(
                                        webhook_url,
                                        text=(
                                            f"In stock: {product_name} @ {site_key}"
                                            + (f" for ${avail.price:.2f}" if avail.price is not None else "")
                                        ),
                                    )
                                except Exception:
                                    pass
                            # Proceed to purchase
                            result = driver.purchase(
                                page=page,
                                product_name=product_name,
                                confirm=auto_confirm,
                                shipping=shipping or {"first_name": "Test", "last_name": "User", "postal_code": "00000"},
                                console=console,
                            )
                            # Notify after purchase
                            if webhook_url:
                                try:
                                    msg = (
                                        f"Purchase {'succeeded' if result.success else 'failed'}: {product_name} @ {site_key}"
                                    )
                                    if result.order_id:
                                        msg += f" (Order ID: {result.order_id})"
                                    notify_slack(webhook_url, text=msg)
                                except Exception:
                                    pass
                            return result

                    # Sleep with jitter to reduce bot-like regularity
                    if jitter > 0:
                        delta = max(interval_seconds * jitter, 0)
                        low = max(interval_seconds - delta, 0.1)
                        high = interval_seconds + delta
                        sleep_for = random.uniform(low, high)
                    else:
                        sleep_for = interval_seconds
                    time.sleep(sleep_for)
                except KeyboardInterrupt:
                    return PurchaseResult(success=False, message="Cancelled by user")
                except Exception as e:
                    console.log(f"[yellow]Watch error:[/yellow] {e}")
                    # Backoff a bit on error
                    time.sleep(min(interval_seconds * 1.5, interval_seconds + 10))
