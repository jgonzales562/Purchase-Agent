# Purchase-Agent

An extensible browser automation agent that can make purchases on your behalf, starting with a safe demo flow (no real payments) against a public test store.

## What it does

- Pluggable site "drivers" with a common purchase contract
- Playwright-powered browser automation (Chromium)
- Human-in-the-loop confirmation before checkout
- Demo driver for Saucedemo (login, add to cart, checkout)
- Watch-and-purchase: automatically buys when an item becomes available (with optional price cap)
  - Uses interval jitter to reduce bot-like patterns
  - Supports persistent sessions (Playwright storage) per site to cut login latency

## Security & ethics

- No real payment credentials are stored or transmitted by default.
- For real sites, prefer official APIs; respect site ToS and anti-bot policies.
- Keep a human confirmation step for all monetary actions.

## Setup

1. Create a virtual environment and install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install
```

2. Run a demo purchase on Saucedemo in headed mode

```bash
python -m purchase_agent.cli purchase --site saucedemo --product "Sauce Labs Backpack" --headed --confirm
```

Notes:

- Saucedemo uses test creds `standard_user` / `secret_sauce` and simulates checkout; no real payment.
- If you omit `--confirm`, the agent will stop before placing the order and prompt you.

### Watch and auto-purchase when available

Automatically watch a product and purchase as soon as it’s in stock and within a price cap.

```bash
python -m purchase_agent.cli watch-purchase \
  --site saucedemo \
  --product "Sauce Labs Backpack" \
  --interval 10 \
  --jitter 0.2 \
  --timeout 600 \
  --price-max 35 \
  --webhook https://hooks.slack.com/services/XXX/YYY/ZZZ \
  --confirm
```

Flags:

- `--interval`: polling frequency in seconds (default 15)
- `--jitter`: randomize interval by ±X% (default 0.2 = ±20%)
- `--webhook`: Slack-compatible webhook URL (or set env var `PURCHASE_AGENT_WEBHOOK`)
- `--timeout`: stop after N seconds (omit or 0 for no timeout)
- `--price-max`: only purchase if price is at or below this value
- `--headed`: show the browser window
- `--confirm`: auto-confirm checkout when available

### Persistent login (optional)

The agent will persist a site session in `storage/<site>.json` and load it on future runs. This can reduce
login time and improve first-action latency. You can delete the file to reset the session.

### Webhook notifications (optional)

If a webhook is set (via `--webhook` or `PURCHASE_AGENT_WEBHOOK`), the watcher will send:

- An "in stock" notification before attempting purchase (with price if available)
- A result notification after purchase (success/failure, includes order id when present)

## Project layout

```
purchase_agent/
  cli.py                # Typer CLI entrypoint
  agent.py              # Base agent and driver registry
  watcher.py            # Availability watcher and auto-purchase
  utils/
    browser.py          # Playwright helpers
  sites/
    base.py             # Site driver interface and availability contract
    saucedemo.py        # Demo site implementation
```

## Next steps

- Add profile storage per site (addresses, preferences) via encrypted keyring
- Add more site drivers or API integrations where available
- Introduce a rules engine for selection/pricing thresholds
- Add tests (pytest) and CI
