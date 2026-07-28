import logging
from typing import Any

import requests

from simon.config_loader import load_config

LOGGER = logging.getLogger("simon.smart_home")


class HomeAssistantClient:
    def __init__(self) -> None:
        cfg = load_config().get("home_assistant", {})
        self.base_url = cfg.get("base_url", "http://localhost:8123").rstrip("/")
        self.token = cfg.get("token", "")
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def _request(self, method: str, path: str, payload: dict | None = None) -> Any:
        url = f"{self.base_url}{path}"
        response = requests.request(method, url, headers=self.headers, json=payload, timeout=30)
        response.raise_for_status()
        if response.status_code == 204:
            return None
        return response.json()

    def get_states(self) -> Any:
        return self._request("GET", "/api/states")

    def turn_on(self, entity_id: str) -> Any:
        return self._request("POST", "/api/services/homeassistant/turn_on", {"entity_id": entity_id})

    def turn_off(self, entity_id: str) -> Any:
        return self._request("POST", "/api/services/homeassistant/turn_off", {"entity_id": entity_id})
