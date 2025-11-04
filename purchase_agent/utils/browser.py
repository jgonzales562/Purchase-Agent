import os
from contextlib import contextmanager
from typing import Iterator, Optional
from playwright.sync_api import sync_playwright, BrowserContext


@contextmanager
def browser_context(
    headed: bool = False,
    storage_state_path: Optional[str] = None,
    save_storage_on_exit: bool = False,
) -> Iterator[BrowserContext]:
    """Yield a Playwright Chromium BrowserContext and ensure cleanup.

    - storage_state_path: path to a JSON file to load/save Playwright storage (cookies, localStorage).
    - save_storage_on_exit: if True and storage_state_path is provided, saves state on context close.
    """
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=not headed, args=["--no-sandbox"])  # --no-sandbox helps in some CI/Linux envs
        if storage_state_path and os.path.exists(storage_state_path):
            context = browser.new_context(storage_state=storage_state_path)
        else:
            context = browser.new_context()
        try:
            yield context
        finally:
            if save_storage_on_exit and storage_state_path:
                # Ensure directory exists before saving
                os.makedirs(os.path.dirname(storage_state_path), exist_ok=True)
                context.storage_state(path=storage_state_path)
            context.close()
            browser.close()
