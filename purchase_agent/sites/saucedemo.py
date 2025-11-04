from __future__ import annotations
import os
from typing import Optional
from playwright.sync_api import Page, expect
from rich.console import Console

from ..registry import register_driver
from .base import PurchaseResult, AvailabilityResult


class SauceDemoDriver:
    key = "saucedemo"
    description = "SauceDemo public test store (no real payments)"

    BASE_URL = "https://www.saucedemo.com/"

    def _login(self, page: Page, console: Console) -> None:
        username = os.getenv("SAUCEDEMO_USER", "standard_user")
        password = os.getenv("SAUCEDEMO_PASSWORD", "secret_sauce")

        page.goto(self.BASE_URL, wait_until="domcontentloaded")
        # If already logged in, the inventory header should be present
        if page.get_by_text("Products").count() > 0 or "inventory.html" in page.url:
            console.log("Already authenticated on Saucedemo")
            return

        # Otherwise perform login
        page.get_by_placeholder("Username").fill(username)
        page.get_by_placeholder("Password").fill(password)
        page.get_by_role("button", name="Login").click()
        # Verify we're on the inventory page
        expect(page.get_by_text("Products")).to_be_visible(timeout=10_000)
        console.log("Logged into Saucedemo")

    def _add_product_to_cart(self, page: Page, product_name: str, console: Console) -> None:
        # Products listed on /inventory.html
        # Click the product by exact name to go to detail page for reliable 'Add to cart'
        item_link = page.get_by_text(product_name, exact=True)
        if not item_link:
            raise ValueError(f"Product '{product_name}' not found")
        item_link.click()
        # On detail page, click Add to cart
        page.get_by_role("button", name="Add to cart").click()
        console.log(f"Added '{product_name}' to cart")

    def check_availability(self, page: Page, product_name: str, console: Console) -> AvailabilityResult:
        # For Saucedemo, all items are generally available; we'll inspect the product card and button state.
        # Login to ensure inventory page is accessible.
        self._login(page, console)
        # Navigate to product detail page for consistent selectors
        item_link = page.get_by_text(product_name, exact=True)
        if not item_link:
            return AvailabilityResult(in_stock=False, message=f"Product '{product_name}' not found")
        item_link.click()

        # Price text, e.g., $29.99
        price_text = page.locator(".inventory_details_price").first.inner_text()
        try:
            price_value = float(price_text.replace("$", "").strip())
        except Exception:
            price_value = None

        # If the button shows 'Add to cart', it's available
        add_button = page.get_by_role("button", name="Add to cart")
        in_stock = add_button.count() > 0
        return AvailabilityResult(
            in_stock=in_stock,
            price=price_value,
            currency="USD",
            message="In stock" if in_stock else "Out of stock",
        )

    def _checkout(self, page: Page, shipping: dict, confirm: bool, console: Console) -> PurchaseResult:
        # Go to cart
        page.locator(".shopping_cart_link").click()
        page.get_by_role("button", name="Checkout").click()

        # Fill info (demo site)
        page.get_by_placeholder("First Name").fill(shipping.get("first_name", "Test"))
        page.get_by_placeholder("Last Name").fill(shipping.get("last_name", "User"))
        page.get_by_placeholder("Zip/Postal Code").fill(shipping.get("postal_code", "00000"))
        page.get_by_role("button", name="Continue").click()

        # Overview page
        expect(page.get_by_text("Checkout: Overview")).to_be_visible(timeout=10_000)
        if not confirm:
            return PurchaseResult(success=False, message="Awaiting human confirmation before placing order")

        page.get_by_role("button", name="Finish").click()
        expect(page.get_by_text("Thank you for your order!")).to_be_visible(timeout=10_000)
        order_msg = page.get_by_text("Thank you for your order!").inner_text()
        console.log("Order placed on Saucedemo")
        return PurchaseResult(success=True, message=order_msg, order_id=None)

    def purchase(self, page: Page, product_name: str, confirm: bool, shipping: dict, console: Console) -> PurchaseResult:
        self._login(page, console)
        self._add_product_to_cart(page, product_name, console)
        return self._checkout(page, shipping, confirm, console)


# Register driver on import
register_driver(SauceDemoDriver.key, lambda: SauceDemoDriver(), SauceDemoDriver.description)
