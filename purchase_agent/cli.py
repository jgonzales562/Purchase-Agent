from typing import Optional
import typer
from rich.console import Console
from rich.table import Table

from .agent import PurchaseAgent
from .registry import get_registry
from .watcher import watch_and_purchase
from .sites import saucedemo  # ensure driver registers on import

app = typer.Typer(help="Purchase Agent CLI")
console = Console()


@app.command("list-sites")
def list_sites() -> None:
    """List available site drivers."""
    registry = get_registry()
    table = Table(title="Available Sites")
    table.add_column("Key", style="cyan")
    table.add_column("Description", style="white")
    for key, meta in registry.items():
        table.add_row(key, meta.get("description", ""))
    console.print(table)


@app.command()
def purchase(
    site: str = typer.Option(..., help="Site key, e.g. 'saucedemo'"),
    product: str = typer.Option(..., help="Product name to purchase"),
    headed: bool = typer.Option(False, help="Run browser headed (visible)"),
    confirm: bool = typer.Option(False, help="Auto-confirm checkout without prompting"),
    first_name: str = typer.Option("Test", help="Shipping first name (for demo sites)"),
    last_name: str = typer.Option("User", help="Shipping last name (for demo sites)"),
    postal_code: str = typer.Option("00000", help="Shipping postal code (for demo sites)"),
) -> None:
    """Run a purchase flow for a product on a given site."""
    agent = PurchaseAgent(headed=headed, console=console)

    # Human-in-the-loop confirmation if not pre-confirmed
    if not confirm:
        do_confirm = typer.confirm(
            f"Proceed to place order for '{product}' on '{site}'?",
            default=False,
        )
        if not do_confirm:
            console.print("[yellow]Cancelled by user before checkout.[/yellow]")
            raise typer.Exit(code=1)

    result = agent.purchase(
        site=site,
        product_name=product,
        confirm=True,  # already confirmed above
        shipping={
            "first_name": first_name,
            "last_name": last_name,
            "postal_code": postal_code,
        },
    )

    if result.success:
        console.print(f"[green]Success:[/green] {result.message}")
        if result.order_id:
            console.print(f"Order ID: [bold]{result.order_id}[/bold]")
    else:
        console.print(f"[red]Failed:[/red] {result.message}")
        raise typer.Exit(code=1)


@app.command("watch-purchase")
def watch_purchase(
    site: str = typer.Option(..., help="Site key, e.g. 'saucedemo'"),
    product: str = typer.Option(..., help="Product name to watch and purchase"),
    interval: int = typer.Option(15, min=1, help="Polling interval in seconds"),
    timeout: int = typer.Option(0, help="Timeout in seconds (0 = no timeout)"),
    jitter: float = typer.Option(0.2, min=0.0, max=1.0, help="Interval jitter as a fraction (e.g., 0.2 = ±20%)"),
    price_max: Optional[float] = typer.Option(None, help="Max acceptable price to auto-purchase"),
    headed: bool = typer.Option(False, help="Run browser headed (visible)"),
    confirm: bool = typer.Option(True, help="Auto-confirm checkout when available"),
    webhook: Optional[str] = typer.Option(None, help="Slack-compatible webhook URL; falls back to PURCHASE_AGENT_WEBHOOK env var"),
    first_name: str = typer.Option("Test", help="Shipping first name"),
    last_name: str = typer.Option("User", help="Shipping last name"),
    postal_code: str = typer.Option("00000", help="Shipping postal code"),
) -> None:
    """Watch a product and purchase immediately when it becomes available (and within price)."""
    console.print("[cyan]Starting watch-and-purchase...[/cyan]")
    result = watch_and_purchase(
        site=site,
        product_name=product,
        interval_seconds=interval,
        timeout_seconds=timeout or None,
        jitter=jitter,
        price_max=price_max,
        headed=headed,
        auto_confirm=confirm,
        webhook_url=webhook,
        shipping={
            "first_name": first_name,
            "last_name": last_name,
            "postal_code": postal_code,
        },
        console=console,
    )
    if result.success:
        console.print(f"[green]Success:[/green] {result.message}")
    else:
        console.print(f"[yellow]{result.message}[/yellow]")

if __name__ == "__main__":
    app()


@app.command("watch-purchase")
def watch_purchase(
    site: str = typer.Option(..., help="Site key, e.g. 'saucedemo'"),
    product: str = typer.Option(..., help="Product name to watch and purchase"),
    interval: int = typer.Option(15, min=1, help="Polling interval in seconds"),
    timeout: int = typer.Option(0, help="Timeout in seconds (0 = no timeout)"),
    price_max: Optional[float] = typer.Option(None, help="Max acceptable price to auto-purchase"),
    headed: bool = typer.Option(False, help="Run browser headed (visible)"),
    confirm: bool = typer.Option(True, help="Auto-confirm checkout when available"),
    first_name: str = typer.Option("Test", help="Shipping first name"),
    last_name: str = typer.Option("User", help="Shipping last name"),
    postal_code: str = typer.Option("00000", help="Shipping postal code"),
) -> None:
    """Watch a product and purchase immediately when it becomes available (and within price)."""
    console.print("[cyan]Starting watch-and-purchase...[/cyan]")
    result = watch_and_purchase(
        site=site,
        product_name=product,
        interval_seconds=interval,
        timeout_seconds=timeout or None,
        price_max=price_max,
        headed=headed,
        auto_confirm=confirm,
        shipping={
            "first_name": first_name,
            "last_name": last_name,
            "postal_code": postal_code,
        },
        console=console,
    )
    if result.success:
        console.print(f"[green]Success:[/green] {result.message}")
    else:
        console.print(f"[yellow]{result.message}[/yellow]")
