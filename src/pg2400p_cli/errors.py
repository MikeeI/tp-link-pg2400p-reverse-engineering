class PG2400PError(Exception):
    """Base error for expected PG2400P operations."""


class DeviceConnectionError(PG2400PError):
    """The device did not complete the expected HTTP exchange."""


class AuthenticationError(PG2400PError):
    """The device rejected authentication."""


class ProtocolError(PG2400PError):
    """The device returned a malformed or unsupported response."""
