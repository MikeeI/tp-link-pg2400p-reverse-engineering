import pytest

from pg2400p_cli.errors import ProtocolError
from pg2400p_cli.protocol import parse_key_value_response, password_digest


def test_password_digest_matches_observed_pg2400p_login() -> None:
    assert password_digest("MyStrongPassword") == "f78e7ab810633ab3a6bbaa49d7d6d5eb"


def test_parse_key_value_response_preserves_equals_in_values() -> None:
    assert parse_key_value_response("ERROR=000\nTOKEN=a=b=c\n") == {
        "ERROR": "000",
        "TOKEN": "a=b=c",
    }


@pytest.mark.parametrize(
    "body",
    ["", "not-a-field", "=value", "ERROR=000\nERROR=006"],
)
def test_parse_key_value_response_rejects_ambiguous_input(body: str) -> None:
    with pytest.raises(ProtocolError):
        parse_key_value_response(body)
