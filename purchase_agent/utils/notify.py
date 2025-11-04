from __future__ import annotations
import json
import sys
from typing import Optional, Dict, Any
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


def post_webhook(url: str, payload: Dict[str, Any], timeout: int = 5) -> Optional[str]:
    """Post a JSON payload to a webhook URL. Returns response text or None on error."""
    data = json.dumps(payload).encode("utf-8")
    req = Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except (URLError, HTTPError) as e:
        # Don't raise to avoid breaking the main flow
        print(f"[notify] webhook post failed: {e}", file=sys.stderr)
        return None


def notify_slack(url: str, text: str, blocks: Optional[list] = None) -> Optional[str]:
    payload: Dict[str, Any] = {"text": text}
    if blocks is not None:
        payload["blocks"] = blocks
    return post_webhook(url, payload)
