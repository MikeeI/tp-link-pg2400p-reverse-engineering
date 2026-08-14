from hashlib import md5

from pg2400p_cli.errors import ProtocolError


def password_digest(password: str) -> str:
    return md5(password.encode("utf-8"), usedforsecurity=False).hexdigest()


def parse_key_value_response(body: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line_number, raw_line in enumerate(body.splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        if "=" not in line:
            raise ProtocolError(
                f"response line {line_number} has no key/value separator"
            )

        key, value = line.split("=", maxsplit=1)
        key = key.strip()
        if not key:
            raise ProtocolError(f"response line {line_number} has an empty key")
        if key in values:
            raise ProtocolError(f"response contains duplicate key {key!r}")
        values[key] = value.strip()

    if not values:
        raise ProtocolError("response contains no key/value fields")
    return values
