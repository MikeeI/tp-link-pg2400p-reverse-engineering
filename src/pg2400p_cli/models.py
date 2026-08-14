from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class DeviceInfo:
    host: str
    product: str
    hardware_revision: str
    firmware_version: str
    language: str


@dataclass(frozen=True, kw_only=True)
class PeerLink:
    mac: str
    rx_mbps: int
    tx_mbps: int
    rx_raw: int
    tx_raw: int


@dataclass(frozen=True, kw_only=True)
class PowerlineSettings:
    local_mac: str
    device_name: str
    network_name: str
    lan_power_saving: bool
    traffic_power_saving: bool
    automatic_compatibility: bool
    phy_mode: str
    technical_standard: str
    qos_mode: str
