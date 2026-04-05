"""
Runtime application settings stored in the database (see AppSetting model).
When no row exists for a key, the value from Django settings (e.g. settings.py) is used.
"""

from typing import Optional

from django.conf import settings

AI_CONNECTOR_KEY = "AI_CONNECTOR"


def _setting_default(key: str):
    return getattr(settings, key, "") or ""


def get_appsetting_value(key: str) -> Optional[str]:
    """
    Return the raw stored value for key, or None if there is no DB override.
    """
    from django.db import DatabaseError, OperationalError

    from .models import AppSetting

    try:
        row = AppSetting.objects.filter(key=key).first()
    except (DatabaseError, OperationalError):
        return None
    if row is None:
        return None
    return row.value


def get_ai_connector() -> str:
    """
    Effective AI connector module name (e.g. 'gemini'), or '' if AI is off.
    DB override wins when present; otherwise settings.AI_CONNECTOR.
    """
    stored = get_appsetting_value(AI_CONNECTOR_KEY)
    if stored is not None:
        return stored
    return _setting_default("AI_CONNECTOR")


def get_ai_connector_form_state():
    """
    For the Web GUI: resolved value, file default, and how the override is stored.
    """
    stored = get_appsetting_value(AI_CONNECTOR_KEY)
    file_default = _setting_default("AI_CONNECTOR")
    if stored is None:
        return {
            "mode": "inherit",
            "effective": file_default,
            "file_default": file_default,
        }
    if stored == "":
        return {
            "mode": "disabled",
            "effective": "",
            "file_default": file_default,
        }
    return {
        "mode": "named",
        "effective": stored,
        "file_default": file_default,
    }
