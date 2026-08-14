from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class DeviceInfo:
    host: str
    product: str
    hardware_revision: str
    firmware_version: str
    language: str
