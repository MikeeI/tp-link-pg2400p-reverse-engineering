from types import TracebackType

import httpx

from pg2400p_cli.domain.errors import (
    AuthenticationError,
    DeviceConnectionError,
    PG2400PError,
    ProtocolError,
)
from pg2400p_cli.domain.models import DeviceInfo, PeerLink, PowerlineSettings
from pg2400p_cli.infrastructure.protocol import parse_key_value_response, password_digest

DEFAULT_TIMEOUT_SECONDS = 8.0
LOGIN_PASSWORD_KEY = "TPLINK.GENERAL.LOGIN_PASSWORD"
SUCCESS_CODE = "000"
SESSION_WARMUP_CODE = "004"
INVALID_PASSWORD_CODE = "006"
PRODUCT_KEY = "SYSTEM.PRODUCTION.HW_PRODUCT"
HARDWARE_REVISION_KEY = "SYSTEM.PRODUCTION.HW_REVISION"
FIRMWARE_VERSION_KEY = "SYSTEM.GENERAL.FW_VERSION"
LANGUAGE_KEY = "TPLINK.GENERAL.LANGUAGE"
LOCAL_MAC_KEY = "SYSTEM.PRODUCTION.MAC_ADDR"
PEER_MACS_KEY = "DIDMNG.GENERAL.MACS"
PEER_RX_RATE_KEY = "DIDMNG.GENERAL.RX_BPS"
PEER_TX_RATE_KEY = "DIDMNG.GENERAL.TX_BPS"
DEVICE_NAME_KEY = "NODE.GENERAL.DEVICE_NAME"
NETWORK_NAME_KEY = "NODE.GENERAL.DOMAIN_NAME"
LAN_POWER_SAVING_KEY = "POWERSAVING.GENERAL.MODE"
TRAFFIC_POWER_SAVING_KEY = "MSPS.THROUGHPUT.ENABLE"
AUTOMATIC_COMPATIBILITY_KEY = "INTERFMITIGATION.XDSL.ENABLED"
PHY_MODE_KEY = "PHYMNG.GENERAL.RUNNING_PHYMODE_ID"
TECHNICAL_STANDARD_COMMAND = "get compatibility mode"
QOS_COMMAND = "get qos"
LOGOUT_COMMAND = "logout"
ZERO_MAC = "00:00:00:00:00:00"
RATE_SCALE = 32

_PHY_MODES = {"7": "mimo", "23": "siso"}
_TECHNICAL_STANDARDS = {"1": "full_power", "2": "vdsl_17a", "3": "vdsl_35b"}
_QOS_MODES = {"1": "fair", "2": "gaming", "3": "streaming", "4": "voice"}
_ALLOWED_COMMANDS = frozenset(
    {
        TECHNICAL_STANDARD_COMMAND,
        QOS_COMMAND,
        LOGOUT_COMMAND,
    }
)
_BROWSER_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0"
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
        password: str | None = None,
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
        try:
            self.close()
        except PG2400PError as cleanup_error:
            if exc_value is None:
                raise
            exc_value.add_note(f"session cleanup failed: {cleanup_error}")

    def close(self) -> None:
        try:
            if self._token is not None:
                self.logout()
        finally:
            self._client.close()

    def authenticate(self) -> None:
        self._preflight()
        response = self._login_request()
        if response.get("ERROR") == SESSION_WARMUP_CODE:
            self._preflight()
            response = self._login_request()
        self._token = _require_login_token(response)

    def logout(self) -> None:
        if self._token is None:
            return
        try:
            self._post_command(LOGOUT_COMMAND)
        finally:
            self._token = None

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

    def read_peer_links(self) -> tuple[PeerLink, ...]:
        values = self._read_fields(
            LOCAL_MAC_KEY,
            PEER_MACS_KEY,
            PEER_RX_RATE_KEY,
            PEER_TX_RATE_KEY,
        )
        local_mac = values[LOCAL_MAC_KEY].lower()
        macs = _split_csv(values[PEER_MACS_KEY])
        rx_rates = _parse_rates(values[PEER_RX_RATE_KEY], key=PEER_RX_RATE_KEY)
        tx_rates = _parse_rates(values[PEER_TX_RATE_KEY], key=PEER_TX_RATE_KEY)
        if len(macs) != len(rx_rates) or len(macs) != len(tx_rates):
            raise ProtocolError("peer MAC and rate arrays have different lengths")

        peers = []
        for mac, rx_raw, tx_raw in zip(macs, rx_rates, tx_rates, strict=True):
            normalized_mac = mac.lower()
            if normalized_mac in (ZERO_MAC, local_mac):
                continue
            peers.append(
                PeerLink(
                    mac=normalized_mac,
                    rx_mbps=rx_raw // RATE_SCALE,
                    tx_mbps=tx_raw // RATE_SCALE,
                    rx_raw=rx_raw,
                    tx_raw=tx_raw,
                ),
            )
        return tuple(peers)

    def read_powerline_settings(self) -> PowerlineSettings:
        values = self._read_fields(
            LOCAL_MAC_KEY,
            DEVICE_NAME_KEY,
            NETWORK_NAME_KEY,
            LAN_POWER_SAVING_KEY,
            TRAFFIC_POWER_SAVING_KEY,
            AUTOMATIC_COMPATIBILITY_KEY,
            PHY_MODE_KEY,
        )
        technical = self._post_command(TECHNICAL_STANDARD_COMMAND)
        qos = self._post_command(QOS_COMMAND)
        return PowerlineSettings(
            local_mac=values[LOCAL_MAC_KEY].lower(),
            device_name=values[DEVICE_NAME_KEY],
            network_name=values[NETWORK_NAME_KEY],
            lan_power_saving=_parse_boolean(
                values[LAN_POWER_SAVING_KEY],
                key=LAN_POWER_SAVING_KEY,
                true_value="1",
                false_value="0",
            ),
            traffic_power_saving=_parse_boolean(
                values[TRAFFIC_POWER_SAVING_KEY],
                key=TRAFFIC_POWER_SAVING_KEY,
                true_value="YES",
                false_value="NO",
            ),
            automatic_compatibility=_parse_boolean(
                values[AUTOMATIC_COMPATIBILITY_KEY],
                key=AUTOMATIC_COMPATIBILITY_KEY,
                true_value="YES",
                false_value="NO",
            ),
            phy_mode=_mapped_value(_PHY_MODES, values[PHY_MODE_KEY]),
            technical_standard=_mapped_value(
                _TECHNICAL_STANDARDS,
                _require_result(technical, command=TECHNICAL_STANDARD_COMMAND),
            ),
            qos_mode=_mapped_value(
                _QOS_MODES,
                _require_result(qos, command=QOS_COMMAND),
            ),
        )

    def _preflight(self) -> None:
        try:
            response = self._client.get("/", headers=_PREFLIGHT_HEADERS)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise DeviceConnectionError(f"preflight failed for http://{self.host}/") from exc

    def _login_request(self) -> dict[str, str]:
        if self._password is None:
            raise AuthenticationError("a password is required for authentication")
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

    def _read_fields(
        self,
        *keys: str,
        require_authentication: bool = True,
    ) -> dict[str, str]:
        if require_authentication and self._token is None:
            raise AuthenticationError("authenticate before reading protected device data")

        params = tuple((key, "") for key in keys)
        if self._token is not None:
            params = (("_t", self._token), *params)
        query = httpx.QueryParams(params)
        headers = {**_AJAX_HEADERS, "Referer": f"http://{self.host}/"}
        try:
            response = self._client.get("/", params=query, headers=headers)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise DeviceConnectionError(f"read request failed for http://{self.host}/") from exc

        values = _parse_success_response(response.text, operation="field read")
        missing = [key for key in keys if key not in values]
        if missing:
            raise ProtocolError(f"device omitted requested field(s): {', '.join(missing)}")
        return {key: values[key] for key in keys}

    def _post_command(self, command: str) -> dict[str, str]:
        if command not in _ALLOWED_COMMANDS:
            raise ProtocolError(f"command {command!r} is not approved by the safety boundary")
        if self._token is None:
            raise AuthenticationError("authenticate before running a protected command")
        base_url = f"http://{self.host}"
        headers = {
            **_AJAX_HEADERS,
            "Origin": base_url,
            "Referer": f"{base_url}/",
        }
        try:
            response = self._client.post(
                "/",
                params={"_t": self._token},
                data={"COMMAND": command},
                headers=headers,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise DeviceConnectionError(f"command failed for {base_url}/") from exc
        return _parse_success_response(response.text, operation=f"command {command!r}")


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",")]


def _parse_rates(value: str, *, key: str) -> list[int]:
    try:
        rates = [int(item) for item in _split_csv(value)]
    except ValueError as exc:
        raise ProtocolError(f"{key} contains a non-integer rate") from exc
    if any(rate < 0 for rate in rates):
        raise ProtocolError(f"{key} contains a negative rate")
    return rates


def _parse_success_response(body: str, *, operation: str) -> dict[str, str]:
    values = parse_key_value_response(body)
    error_code = values.pop("ERROR", None)
    if error_code != SUCCESS_CODE:
        raise ProtocolError(
            f"device returned {operation} error {error_code or '<missing>'}",
        )
    return values


def _parse_boolean(
    value: str,
    *,
    key: str,
    true_value: str,
    false_value: str,
) -> bool:
    if value == true_value:
        return True
    if value == false_value:
        return False
    raise ProtocolError(f"{key} contains unsupported value {value!r}")


def _mapped_value(values: dict[str, str], value: str) -> str:
    return values.get(value, f"unknown:{value}")


def _require_result(values: dict[str, str], *, command: str) -> str:
    result = values.get("RESULT")
    if result is None:
        raise ProtocolError(f"command {command!r} returned no RESULT")
    return result


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
