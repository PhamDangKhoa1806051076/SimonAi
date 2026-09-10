"""
Simon Smart Home – Home Assistant integration.
Controls lights, switches, fans, air conditioners via Home Assistant API.
All functions are designed to be called by the Brain via Function Calling.
"""

import logging
from typing import Any, Optional

import requests

from simon.config_loader import load_config

LOGGER = logging.getLogger("simon.smart_home")


class HomeAssistantClient:
    """Client for Home Assistant local API."""

    def __init__(self) -> None:
        cfg = load_config().get("home_assistant", {})
        self.base_url = cfg.get("base_url", "http://localhost:8123").rstrip("/")
        self.token = cfg.get("token", "")
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        self._available = bool(self.token)

    @property
    def is_available(self) -> bool:
        return self._available

    def _request(self, method: str, path: str, payload: Optional[dict] = None) -> Any:
        """Make an API request to Home Assistant."""
        if not self._available:
            return {"error": "Home Assistant chưa được cấu hình (thiếu token)"}
        url = f"{self.base_url}{path}"
        try:
            response = requests.request(
                method, url, headers=self.headers, json=payload, timeout=30
            )
            response.raise_for_status()
            if response.status_code == 204:
                return {"status": "ok"}
            return response.json()
        except requests.ConnectionError:
            return {"error": f"Không kết nối được Home Assistant tại {self.base_url}"}
        except requests.Timeout:
            return {"error": "Home Assistant không phản hồi (timeout)"}
        except Exception as exc:
            return {"error": str(exc)}

    # ------------------------------------------------------------------
    # Core Actions
    # ------------------------------------------------------------------

    def get_states(self) -> Any:
        """Get all entity states."""
        return self._request("GET", "/api/states")

    def turn_on(self, entity_id: str) -> str:
        """Turn on a device."""
        result = self._request("POST", "/api/services/homeassistant/turn_on", {"entity_id": entity_id})
        if isinstance(result, dict) and "error" in result:
            return f"Lỗi: {result['error']}"
        return f"Đã bật {entity_id}"

    def turn_off(self, entity_id: str) -> str:
        """Turn off a device."""
        result = self._request("POST", "/api/services/homeassistant/turn_off", {"entity_id": entity_id})
        if isinstance(result, dict) and "error" in result:
            return f"Lỗi: {result['error']}"
        return f"Đã tắt {entity_id}"

    def toggle(self, entity_id: str) -> str:
        """Toggle a device on/off."""
        result = self._request("POST", "/api/services/homeassistant/toggle", {"entity_id": entity_id})
        if isinstance(result, dict) and "error" in result:
            return f"Lỗi: {result['error']}"
        return f"Đã chuyển đổi {entity_id}"

    # ------------------------------------------------------------------
    # Light Control
    # ------------------------------------------------------------------

    def set_brightness(self, entity_id: str, brightness: int) -> str:
        """Set light brightness (0-255)."""
        brightness = max(0, min(255, brightness))
        result = self._request(
            "POST",
            "/api/services/light/turn_on",
            {"entity_id": entity_id, "brightness": brightness},
        )
        if isinstance(result, dict) and "error" in result:
            return f"Lỗi: {result['error']}"
        pct = round(brightness / 255 * 100)
        return f"Đã đặt độ sáng {entity_id} ở {pct}%"

    def set_color(self, entity_id: str, r: int, g: int, b: int) -> str:
        """Set light color using RGB values."""
        result = self._request(
            "POST",
            "/api/services/light/turn_on",
            {"entity_id": entity_id, "rgb_color": [r, g, b]},
        )
        if isinstance(result, dict) and "error" in result:
            return f"Lỗi: {result['error']}"
        return f"Đã đổi màu {entity_id} sang RGB({r},{g},{b})"

    # ------------------------------------------------------------------
    # Climate Control
    # ------------------------------------------------------------------

    def set_temperature(self, entity_id: str, temperature: float) -> str:
        """Set climate/AC temperature."""
        result = self._request(
            "POST",
            "/api/services/climate/set_temperature",
            {"entity_id": entity_id, "temperature": temperature},
        )
        if isinstance(result, dict) and "error" in result:
            return f"Lỗi: {result['error']}"
        return f"Đã đặt nhiệt độ {entity_id} ở {temperature}°C"

    # ------------------------------------------------------------------
    # Device Listing
    # ------------------------------------------------------------------

    def list_devices(self) -> str:
        """List all connected devices and their states."""
        states = self.get_states()
        if isinstance(states, dict) and "error" in states:
            return f"Lỗi: {states['error']}"
        if not isinstance(states, list):
            return "Không lấy được danh sách thiết bị."

        # Filter to interesting device types
        device_types = {"light", "switch", "fan", "climate", "cover", "media_player"}
        devices = []
        for entity in states:
            eid = entity.get("entity_id", "")
            domain = eid.split(".")[0] if "." in eid else ""
            if domain in device_types:
                name = entity.get("attributes", {}).get("friendly_name", eid)
                state = entity.get("state", "unknown")
                devices.append(f"  • {name} ({eid}): {state}")

        if not devices:
            return "Không tìm thấy thiết bị smart home nào."
        return f"Thiết bị smart home ({len(devices)}):\n" + "\n".join(devices)


# ------------------------------------------------------------------
# Tool wrappers for Function Calling
# ------------------------------------------------------------------

_ha_client: Optional[HomeAssistantClient] = None


def _get_client() -> HomeAssistantClient:
    global _ha_client
    if _ha_client is None:
        _ha_client = HomeAssistantClient()
    return _ha_client


def smart_home_turn_on(entity_id: str) -> str:
    """Turn on a smart home device."""
    return _get_client().turn_on(entity_id)


def smart_home_turn_off(entity_id: str) -> str:
    """Turn off a smart home device."""
    return _get_client().turn_off(entity_id)


def smart_home_toggle(entity_id: str) -> str:
    """Toggle a smart home device on/off."""
    return _get_client().toggle(entity_id)


def smart_home_list_devices() -> str:
    """List all smart home devices and their states."""
    return _get_client().list_devices()


def smart_home_set_brightness(entity_id: str, brightness_percent: int) -> str:
    """Set light brightness (0-100%)."""
    brightness_255 = round(brightness_percent / 100 * 255)
    return _get_client().set_brightness(entity_id, brightness_255)


def smart_home_set_temperature(entity_id: str, temperature: float) -> str:
    """Set AC/climate temperature."""
    return _get_client().set_temperature(entity_id, temperature)
