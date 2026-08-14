from types import TracebackType

import httpx

from pg2400p_cli.errors import AuthenticationError, DeviceConnectionError, ProtocolError
from pg2400p_cli.models import DeviceInfo
from pg2400p_cli.protocol import parse_key_value_response, password_digest

DEFAULT_TIMEOUT_SECONDS = 8.0
LOGIN_PASSWORD_KEY = "TPLINK.GENERAL.LOGIN_PASSWORD"
SUCCESS_CODE = "000"
SESSION_WARMUP_CODE = "004"
INVALID_PASSWORD_CODE = "006"
PRODUCT_KEY = "SYSTEM.PRODUCTION.HW_PRODUCT"
HARDWARE_REVISION_KEY = "SYSTEM.PRODUCTION.HW_REVISION"
FIRMWARE_VERSION_KEY = "SYSTEM.GENERAL.FW_VERSION"
LANGUAGE_KEY = "TPLINK.GENERAL.LANGUAGE"

_BROWSER_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) "
    "Gecko/20100101 Firefox/143.0"
)
_AJAX_HEADERS = {
    "Accept": "text/plain, */*; q=0.01",
    "Accept-Language": "en-GB,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Content-Type": "application/x-www-form-urlencoded",
    "Connection": "keep-alive",
    "User-Agent": _BROWSER_USER_AGENT,
    "X-Requested-With": "XMLHttpRequest",
}
_PREFLIGHT_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-GB,en;q=0.5",
    "User-Agent": _BROWSER_USER_AGENT,
}


class PG2400PClient:
    def __init__(
        self,
        *,
        host: str,
        password: str,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        normalized_host = _normalize_host(host)
        self.host = normalized_host
        self._password = password
        self._token: str | None = None
        self._client = httpx.Client(
            base_url=f"http://{normalized_host}",
            headers={"User-Agent": _BROWSER_USER_AGENT},
            timeout=timeout_seconds,
            transport=transport,
            trust_env=False,
        )

    @property
    def authenticated(self) -> bool:
        return self._token is not None

    def __enter__(self) -> "PG2400PClient":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()

    def close(self) -> None:
        self._client.close()

    def authenticate(self) -> None:
        self._preflight()
        response = self._login_request()
        if response.get("ERROR") == SESSION_WARMUP_CODE:
            self._preflight()
            response = self._login_request()
        self._token = _require_login_token(response)

    def read_device_info(self) -> DeviceInfo:
        values = self._read_fields(
            PRODUCT_KEY,
            HARDWARE_REVISION_KEY,
            FIRMWARE_VERSION_KEY,
            LANGUAGE_KEY,
        )
        return DeviceInfo(
            host=self.host,
            product=values[PRODUCT_KEY],
            hardware_revision=values[HARDWARE_REVISION_KEY],
            firmware_version=values[FIRMWARE_VERSION_KEY],
            language=values[LANGUAGE_KEY],
        )

    def _preflight(self) -> None:
        try:
            response = self._client.get("/", headers=_PREFLIGHT_HEADERS)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise DeviceConnectionError(f"preflight failed for http://{self.host}/") from exc

    def _login_request(self) -> dict[str, str]:
        body = f"{LOGIN_PASSWORD_KEY}={password_digest(self._password)}"
        base_url = f"http://{self.host}"
        headers = {
            **_AJAX_HEADERS,
            "Origin": base_url,
            "Referer": f"{base_url}/",
        }
        try:
            response = self._client.post("/", content=body, headers=headers)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise DeviceConnectionError(f"login request failed for {base_url}/") from exc
        return parse_key_value_response(response.text)

    def _read_fields(self, *keys: str) -> dict[str, str]:
        if self._token is None:
            raise AuthenticationError("authenticate before reading device data")

        params = [("_t", self._token), *((key, "") for key in keys)]
        try:
            response = self._client.get("/", params=params, headers=_AJAX_HEADERS)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise DeviceConnectionError(f"read request failed for http://{self.host}/") from exc

        values = parse_key_value_response(response.text)
        error_code = values.pop("ERROR", None)
        if error_code != SUCCESS_CODE:
            raise ProtocolError(f"device returned read error {error_code or '<missing>'}")
        missing = [key for key in keys if key not in values]
        if missing:
            raise ProtocolError(f"device omitted requested field(s): {', '.join(missing)}")
        return {key: values[key] for key in keys}


def _normalize_host(host: str) -> str:
    normalized = host.strip()
    if not normalized:
        raise ValueError("host must not be empty")
    if any(character in normalized for character in ("/", "?", "#")) or "://" in normalized:
        raise ValueError("host must not include a scheme, path, query, or fragment")
    if any(character.isspace() for character in normalized):
        raise ValueError("host must not contain whitespace")
    return normalized


def _require_login_token(response: dict[str, str]) -> str:
    error_code = response.get("ERROR")
    if error_code == INVALID_PASSWORD_CODE:
        attempts = response.get("LOGIN_TIMES")
        detail = f" after {attempts} failed attempt(s)" if attempts else ""
        raise AuthenticationError(f"device rejected the password{detail}")
    if error_code != SUCCESS_CODE:
        raise ProtocolError(f"device returned login error {error_code or '<missing>'}")

    token = response.get("TOKEN")
    if not token:
        raise ProtocolError("successful login response has no TOKEN")
    return token
