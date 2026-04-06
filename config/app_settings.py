"""
Runtime application settings stored in the database (see AppSetting model).
When no row exists for a key, the value from Django settings (e.g. settings.py) is used.

SETTINGS_REGISTRY is the single source of truth for all settings exposed in the
Web GUI.  To add a new setting: append an entry to the list and it will appear
automatically on the Application tab.
"""

from typing import Optional

from django.conf import settings


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------
# Each entry describes one setting.  Fields:
#   key          – the Django settings attribute name
#   label        – human-readable label (defaults to key)
#   type         – 'bool' | 'int' | 'string' | 'choice' | 'ai_connector'
#   description  – short help text shown under the field
#   choices      – for type='choice': list of (value, label) tuples
#   group        – logical grouping shown as an accordion header
#   readonly     – if True the field is shown but not editable (info only)

SETTINGS_REGISTRY = [
    # ── General ──────────────────────────────────────────────────────────
    {
        "key": "DEBUG",
        "type": "bool",
        "description": "Display debug information. Always set to False in production.",
        "group": "General",
    },
    {
        "key": "UPDATE_ON",
        "type": "choice",
        "choices": [("commit", "commit"), ("release", "release")],
        "description": "How you are notified about updates (latest commit vs. tagged release).",
        "group": "General",
    },
    {
        "key": "SHOW_LOGIN_FORM",
        "type": "bool",
        "description": "Show a username/password login form. Disable if authentication is purely SSO.",
        "group": "General",
    },
    {
        "key": "AUTH_PROVIDER",
        "type": "choice",
        "choices": [("", "(local authentication)"), ("pingid", "pingid"), ("entraid", "entraid")],
        "description": "External authentication provider (leave empty for local auth).",
        "group": "General",
    },

    # ── Paths / Deployment ───────────────────────────────────────────────
    {
        "key": "TEMP_FOLDER",
        "type": "string",
        "description": "Temporary location used by the upgrade script for rollback.",
        "group": "Paths / Deployment",
    },
    {
        "key": "VENV_PATH",
        "type": "string",
        "description": "Python virtual-env path used by the upgrade script.",
        "group": "Paths / Deployment",
    },
    {
        "key": "USER_GROUP",
        "type": "string",
        "description": "user:group used by the deployment script to fix permissions.",
        "group": "Paths / Deployment",
    },
    {
        "key": "SERVER_USER",
        "type": "string",
        "description": "User running the web server (e.g. www-data).",
        "group": "Paths / Deployment",
    },
    {
        "key": "GITHUB_REPO",
        "type": "string",
        "description": "GitHub repository in owner/repo format. Other GitHub URLs are derived from this.",
        "group": "Paths / Deployment",
    },

    # ── Data retention / Campaigns ───────────────────────────────────────
    {
        "key": "DB_DATA_RETENTION",
        "type": "int",
        "description": "Number of days to keep data in the local database (default 90).",
        "group": "Data retention / Campaigns",
    },
    {
        "key": "RARE_OCCURRENCES_THRESHOLD",
        "type": "int",
        "description": "Distinct-host threshold below which an analytic is flagged as a rare occurrence.",
        "group": "Data retention / Campaigns",
    },
    {
        "key": "CAMPAIGN_MAX_HOSTS_THRESHOLD",
        "type": "int",
        "description": "Max distinct hosts stored per analytic per campaign day (default 1000).",
        "group": "Data retention / Campaigns",
    },
    {
        "key": "ON_MAXHOSTS_REACHED__THRESHOLD",
        "label": "ON_MAXHOSTS_REACHED → THRESHOLD",
        "type": "int",
        "description": "How many times CAMPAIGN_MAX_HOSTS_THRESHOLD must be hit before auto-actions fire.",
        "group": "Data retention / Campaigns",
    },
    {
        "key": "ON_MAXHOSTS_REACHED__DISABLE_RUN_DAILY",
        "label": "ON_MAXHOSTS_REACHED → DISABLE_RUN_DAILY",
        "type": "bool",
        "description": "Automatically remove the analytic from future campaigns when threshold is hit.",
        "group": "Data retention / Campaigns",
    },
    {
        "key": "ON_MAXHOSTS_REACHED__DELETE_STATS",
        "label": "ON_MAXHOSTS_REACHED → DELETE_STATS",
        "type": "bool",
        "description": "Automatically delete associated statistics when threshold is hit.",
        "group": "Data retention / Campaigns",
    },

    # ── Analytics ─────────────────────────────────────────────────────────
    {
        "key": "ANALYTICS_PER_PAGE",
        "type": "int",
        "description": "Number of analytics displayed per page in the list view.",
        "group": "Analytics",
    },
    {
        "key": "DAYS_BEFORE_REVIEW",
        "type": "int",
        "description": "Number of days before an analytic is considered for review.",
        "group": "Analytics",
    },
    {
        "key": "DISABLE_ANALYTIC_ON_REVIEW",
        "type": "bool",
        "description": "Automatically disable analytics whose status becomes REVIEW.",
        "group": "Analytics",
    },
    {
        "key": "AUTO_STATS_REGENERATION",
        "type": "bool",
        "description": "Regenerate stats automatically when an analytic's query is changed or created.",
        "group": "Analytics",
    },

    # ── Repo import ───────────────────────────────────────────────────────
    {
        "key": "REPO_IMPORT_DEFAULT_STATUS",
        "type": "choice",
        "choices": [("DRAFT", "DRAFT"), ("PUB", "PUB")],
        "description": "Default status assigned to analytics imported from a remote repo.",
        "group": "Repo import",
    },
    {
        "key": "REPO_IMPORT_DEFAULT_RUN_DAILY",
        "type": "bool",
        "description": "Include imported analytics in campaigns (run_daily flag).",
        "group": "Repo import",
    },
    {
        "key": "REPO_IMPORT_CREATE_FIELD_IF_NOT_EXIST__category",
        "label": "REPO_IMPORT auto-create → category",
        "type": "bool",
        "description": "Automatically create missing category relations on repo import.",
        "group": "Repo import",
    },
    {
        "key": "REPO_IMPORT_CREATE_FIELD_IF_NOT_EXIST__threats",
        "label": "REPO_IMPORT auto-create → threats",
        "type": "bool",
        "description": "Automatically create missing threat relations on repo import.",
        "group": "Repo import",
    },
    {
        "key": "REPO_IMPORT_CREATE_FIELD_IF_NOT_EXIST__actors",
        "label": "REPO_IMPORT auto-create → actors",
        "type": "bool",
        "description": "Automatically create missing actor relations on repo import.",
        "group": "Repo import",
    },
    {
        "key": "REPO_IMPORT_CREATE_FIELD_IF_NOT_EXIST__vulnerabilities",
        "label": "REPO_IMPORT auto-create → vulnerabilities",
        "type": "bool",
        "description": "Automatically create missing vulnerability relations on repo import.",
        "group": "Repo import",
    },

    # ── Notifications ─────────────────────────────────────────────────────
    {
        "key": "AUTO_DELETE_NOTIFICATIONS_AFTER__debug",
        "label": "Auto-delete notifications → debug (days)",
        "type": "int",
        "description": "Days before debug-level notifications are auto-deleted.",
        "group": "Notifications",
    },
    {
        "key": "AUTO_DELETE_NOTIFICATIONS_AFTER__info",
        "label": "Auto-delete notifications → info (days)",
        "type": "int",
        "description": "Days before info-level notifications are auto-deleted.",
        "group": "Notifications",
    },
    {
        "key": "AUTO_DELETE_NOTIFICATIONS_AFTER__success",
        "label": "Auto-delete notifications → success (days)",
        "type": "int",
        "description": "Days before success-level notifications are auto-deleted.",
        "group": "Notifications",
    },
    {
        "key": "AUTO_DELETE_NOTIFICATIONS_AFTER__warning",
        "label": "Auto-delete notifications → warning (days)",
        "type": "int",
        "description": "Days before warning-level notifications are auto-deleted.",
        "group": "Notifications",
    },
    {
        "key": "AUTO_DELETE_NOTIFICATIONS_AFTER__error",
        "label": "Auto-delete notifications → error (days)",
        "type": "int",
        "description": "Days before error-level notifications are auto-deleted.",
        "group": "Notifications",
    },

    # ── AI ─────────────────────────────────────────────────────────────────
    {
        "key": "AI_CONNECTOR",
        "type": "ai_connector",
        "description": "AI plugin used for MITRE suggestions and the query assistant.",
        "group": "AI",
    },

    # ── Proxy ──────────────────────────────────────────────────────────────
    {
        "key": "PROXY__http",
        "label": "PROXY → http",
        "type": "string",
        "description": "HTTP proxy URL (e.g. http://proxy:port). Leave empty for no proxy.",
        "group": "Proxy",
    },
    {
        "key": "PROXY__https",
        "label": "PROXY → https",
        "type": "string",
        "description": "HTTPS proxy URL (e.g. http://proxy:port). Leave empty for no proxy.",
        "group": "Proxy",
    },
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _file_default(key: str):
    """
    Resolve the value in settings.py for *key*.
    Supports nested keys separated by '__' (e.g. PROXY__http → settings.PROXY['http']).
    """
    parts = key.split("__")
    val = getattr(settings, parts[0], "")
    for sub in parts[1:]:
        if isinstance(val, dict):
            val = val.get(sub, "")
        else:
            val = ""
            break
    if val is None:
        val = ""
    return val


_table_missing = None  # tri-state cache: None=unchecked, True, False


def _is_table_present() -> bool:
    global _table_missing
    if _table_missing is not None:
        return not _table_missing
    from django.db import connection, DatabaseError, OperationalError
    try:
        with connection.cursor() as cursor:
            tables = connection.introspection.table_names(cursor)
        _table_missing = "config_appsetting" not in tables
    except (DatabaseError, OperationalError):
        _table_missing = True
    return not _table_missing


def get_appsetting_value(key: str) -> Optional[str]:
    """
    Return the raw stored value for key, or None if there is no DB override.
    """
    if not _is_table_present():
        return None

    from django.db import DatabaseError, OperationalError
    from .models import AppSetting

    try:
        row = AppSetting.objects.filter(key=key).first()
    except (DatabaseError, OperationalError):
        return None
    if row is None:
        return None
    return row.value


def get_effective(key: str) -> str:
    """
    Return the effective value: DB override if present, else settings.py.
    """
    stored = get_appsetting_value(key)
    if stored is not None:
        return stored
    return str(_file_default(key))


def get_ai_connector() -> str:
    """
    Effective AI connector module name (e.g. 'gemini'), or '' if AI is off.
    """
    return get_effective("AI_CONNECTOR")


# ---------------------------------------------------------------------------
# Build context for the template
# ---------------------------------------------------------------------------

def _serialize_bool(val) -> str:
    """Normalise to 'True' / 'False' string."""
    if isinstance(val, bool):
        return str(val)
    s = str(val).strip().lower()
    return "True" if s in ("true", "1", "yes") else "False"


def is_appsetting_table_ready() -> bool:
    return _is_table_present()


def build_settings_context():
    """
    Return a list of groups, each containing their setting entries with
    current effective values, file defaults, and override state.
    Called by the view to populate the template.
    """
    from collections import OrderedDict
    from connectors.models import Connector

    groups = OrderedDict()
    for entry in SETTINGS_REGISTRY:
        key = entry["key"]
        label = entry.get("label", key)
        stype = entry["type"]
        desc = entry.get("description", "")
        choices = entry.get("choices", [])
        group = entry.get("group", "Other")
        readonly = entry.get("readonly", False)

        file_default = _file_default(key)
        stored = get_appsetting_value(key)
        has_override = stored is not None

        if stype == "bool":
            effective = _serialize_bool(stored if has_override else file_default)
            file_default_display = _serialize_bool(file_default)
        elif stype == "int":
            effective = stored if has_override else str(file_default)
            file_default_display = str(file_default)
        elif stype == "ai_connector":
            effective = stored if has_override else str(file_default)
            file_default_display = str(file_default) if file_default else "(empty)"
            ai_connectors = list(
                Connector.objects.filter(domain="ai")
                .order_by("name")
                .values_list("name", "enabled")
            )
            choices = ai_connectors
        else:
            effective = stored if has_override else str(file_default)
            file_default_display = str(file_default) if file_default else "(empty)"

        item = {
            "key": key,
            "label": label,
            "type": stype,
            "description": desc,
            "choices": choices,
            "readonly": readonly,
            "effective": effective,
            "file_default_display": file_default_display,
            "has_override": has_override,
        }

        groups.setdefault(group, []).append(item)

    return [{"name": name, "settings": items} for name, items in groups.items()]
