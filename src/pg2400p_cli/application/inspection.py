from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from types import TracebackType
from typing import Protocol, Self

from pg2400p_cli.domain.models import DeviceInfo, PeerLink, PowerlineSettings


class InspectionClient(Protocol):
    def __enter__(self) -> Self: ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None: ...

    def authenticate(self) -> None: ...

    def read_device_info(self) -> DeviceInfo: ...

    def read_peer_links(self) -> tuple[PeerLink, ...]: ...

    def read_powerline_settings(self) -> PowerlineSettings: ...


class InspectionClientFactory(Protocol):
    def __call__(
        self,
        *,
        host: str,
        password: str,
        timeout_seconds: float,
    ) -> InspectionClient: ...


@dataclass(frozen=True, kw_only=True)
class DeviceStatus:
    device: DeviceInfo
    powerline: PowerlineSettings
    peers: tuple[PeerLink, ...]


class InspectionService:
    """Own authenticated read-only inspection workflows."""

    def __init__(
        self,
        *,
        host: str,
        password: str,
        timeout_seconds: float,
        client_factory: InspectionClientFactory,
    ) -> None:
        self._host = host
        self._password = password
        self._timeout_seconds = timeout_seconds
        self._client_factory = client_factory

    def check_authentication(self) -> None:
        with self._authenticated_client():
            return

    def read_device_info(self) -> DeviceInfo:
        with self._authenticated_client() as client:
            return client.read_device_info()

    def read_peer_links(self) -> tuple[PeerLink, ...]:
        with self._authenticated_client() as client:
            return client.read_peer_links()

    def read_powerline_settings(self) -> PowerlineSettings:
        with self._authenticated_client() as client:
            return client.read_powerline_settings()

    def read_status(self) -> DeviceStatus:
        with self._authenticated_client() as client:
            return DeviceStatus(
                device=client.read_device_info(),
                powerline=client.read_powerline_settings(),
                peers=client.read_peer_links(),
            )

    @contextmanager
    def _authenticated_client(self) -> Iterator[InspectionClient]:
        with self._client_factory(
            host=self._host,
            password=self._password,
            timeout_seconds=self._timeout_seconds,
        ) as client:
            client.authenticate()
            yield client
