"""Helper utilities for SEMP path construction."""

from __future__ import annotations

from urllib.parse import quote

# Broker-enforced name length limits (not in the SEMP swagger schema — runtime only).
NAME_MAX_LENGTHS: dict[str, int] = {
    "queueName":              200,
    "restDeliveryPointName":  100,
    "restConsumerName":        32,
    "queueBindingName":       200,
    "aclProfileName":          32,
    "clientProfileName":       32,
    "clientUsername":         189,
}


def check_name_length(field: str, value: str) -> str | None:
    """Return an error message if *value* exceeds the broker limit for *field*, else None."""
    limit = NAME_MAX_LENGTHS.get(field)
    if limit is not None and len(value) > limit:
        return (
            f"'{field}' value is {len(value)} characters but the broker limit is {limit}: "
            f"'{value}'"
        )
    return None


def enc(value: str) -> str:
    """URL-encode a SEMP path segment."""
    return quote(str(value), safe="")


def coerce_bool(value: object) -> bool:
    """Coerce a value to bool (handles YAML bools and Jinja2 string output)."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ("true", "yes", "1")
    return bool(value)


def coerce_int(value: object) -> int:
    """Coerce a value to int."""
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    return int(str(value))


def clean_payload(args: dict) -> dict:
    """Return a copy of args with None and empty-string values removed."""
    return {
        k: v for k, v in args.items()
        if v is not None and not (isinstance(v, str) and v.strip() == "")
    }
