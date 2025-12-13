# device/deviceController.py
import os
import time
import requests
from typing import Dict, List, Tuple, Optional

# ===== Try reading config.settings; if it doesn't exist, use environment variables/defaults. =====
HA_API_URL : str = "http://127.0.0.1:8123"
HA_TOKEN : Optional[str] = None
REQUEST_TIMEOUT: int = 5

# try:
#     from config.settings import HA_API_URL as _URL  # type: ignore
#     from config.settings import HA_TOKEN as _TOKEN  # type: ignore
#     try:
#         from config.settings import REQUEST_TIMEOUT as _TO  # type: ignore
#     except Exception:
#         _TO = REQUEST_TIMEOUT
#     HA_API_URL = "http://127.0.0.1:5000/api"
#     HA_TOKEN = _TOKEN
#     REQUEST_TIMEOUT = _TO
# except Exception:
#     # environment configues reveal the details
#     HA_API_URL = os.getenv("HA_API_URL")
#     HA_TOKEN = os.getenv("HA_TOKEN")
#     to_env = os.getenv("REQUEST_TIMEOUT")
#     if to_env and to_env.isdigit():
#         REQUEST_TIMEOUT = int(to_env)

# HA_API_URL = "http://127.0.0.1:5000/api"
# HA_TOKEN = Optional[str] = None
# REQUEST_TIMEOUT = _TO

class DeviceController:
    def __init__(self, haUrl: Optional[str] = None, haToken: Optional[str] = None):
        # Pass parameters first, then config/env.
        self.haUrl = haUrl or HA_API_URL
        self.haToken = haToken or HA_TOKEN
        self._cache: Dict[str, Tuple[float, str]] = {}  # {entityId: (timestamp, state)}
        self.cache_expiry = 5  # seconds

        # dry-run: No URL means no actual request.
        self.dry_run = not bool(self.haUrl)

        if self.dry_run:
            print("[DeviceController] HA_API_URL not set，entering dry-run。")
        elif not self.haToken:
            print("[DeviceController] Run without token")

    # --- public headers ---
    def _headers(self) -> Dict[str, str]:
        h = {"Content-Type": "application/json"}
        if self.haToken:
            h["Authorization"] = f"Bearer {self.haToken}"
        return h

    # --- Internal: Execution requests (unified processing) ---
    def _post(self, path: str, json: dict) -> requests.Response:
        assert self.haUrl, "HA_API_URL 未设置"
        return requests.post(
            f"{self.haUrl}{path}",
            json=json,
            headers=self._headers(),
            timeout=REQUEST_TIMEOUT,
        )

    def _get(self, path: str) -> requests.Response:
        assert self.haUrl, "HA_API_URL 未设置"
        return requests.get(
            f"{self.haUrl}{path}",
            headers=self._headers(),
            timeout=REQUEST_TIMEOUT,
        )

    # --- Single device control ---
    def executeCommand(self, entityId: str, action: str) -> str:
        domain = self._extract_domain(entityId)
        service = "turn_on" if action == "turn_on" else "turn_off"

        if self.dry_run:
            msg = f"[DRY-RUN] POST /api/services/{domain}/{service} {{entity_id: {entityId}}}"
            print(msg)
            # Assuming success and updating the cache
            self._update_cache(entityId, "on" if service == "turn_on" else "off")
            return "Success (dry-run)"

        try:
            resp = self._post(f"/api/services/{domain}/{service}", {"entity_id": entityId})
            if resp.status_code == 200:
                self._update_cache(entityId, "on" if service == "turn_on" else "off")
                return "Success"
            if resp.status_code == 401:
                return "Fail: 401 (Unauthorized) — 请设置 HA_TOKEN"
            return f"Fail: {resp.status_code} {resp.text[:120]}"
        except Exception as e:
            return f"Err: {str(e)}"

    # --- Status enquiry ---
    def getDeviceStatus(self, entityId: str) -> str:
        now = time.time()
        if entityId in self._cache:
            ts, state = self._cache[entityId]
            if now - ts < self.cache_expiry:
                return state

        if self.dry_run:
            print(f"[DRY-RUN] GET /api/states/{entityId}")
            # Return cached or unknown
            state = self._cache.get(entityId, (0, "unknown"))[1]
            return state

        try:
            resp = self._get(f"/api/states/{entityId}")
            if resp.status_code == 200:
                state = resp.json().get("state", "unknown")
                self._update_cache(entityId, state)
                return state
            if resp.status_code == 401:
                return "Fail: 401 (Unauthorized) — 请设置 HA_TOKEN"
            return f"Enquire Fail: {resp.status_code}"
        except Exception as e:
            return f"Err: {str(e)}"

    # --- Batch command ---
    def batchExecute(self, commands: List[Tuple[str, str]]) -> Dict[str, str]:
        results: Dict[str, str] = {}
        for entityId, action in commands:
            results[entityId] = self.executeCommand(entityId, action)
        return results

    # --- Intent interface (可选保留) ---
    def handleAction(self, intent: dict):
        entity = intent.get("entity")
        action = intent.get("action")
        if not entity or not action:
            return "Parameter missing"
        return self.executeCommand(entity, action)

    # --- Internal utils ---
    def _extract_domain(self, entityId: str) -> str:
        return entityId.split(".")[0] if "." in entityId else "unknown"

    def _update_cache(self, entityId: str, state: str) -> None:
        self._cache[entityId] = (time.time(), state)
