from typing import Callable, Dict
from .sites.base import SiteDriver

# Simple driver registry: key -> {"factory": callable, "description": str}
_REGISTRY: Dict[str, Dict[str, object]] = {}


def register_driver(key: str, factory: Callable[[], SiteDriver], description: str = "") -> None:
    key = key.lower().strip()
    _REGISTRY[key] = {"factory": factory, "description": description}


def get_registry() -> Dict[str, Dict[str, object]]:
    return dict(_REGISTRY)
