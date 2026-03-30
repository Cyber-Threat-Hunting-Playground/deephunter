# Fix: Resilient Plugin Loading

## Problem

When a plugin is installed (symlinked from `plugins/catalog/` to `plugins/`) but its
Python dependencies are missing or the module is otherwise broken, **the entire Django
application crashes on startup**. This prevents all management commands (`loaddata`,
`migrate`, `createsuperuser`, etc.) from running and makes the web UI completely
unavailable.

### Error example

```
File "/data/deephunter/qm/utils.py", line 17, in <module>
    module = importlib.import_module(f"plugins.{module_name}")
ModuleNotFoundError: No module named 'plugins.openai_custom'
```

## Root Cause

Three files import all plugin modules **at module load time** without any error handling.
If any single plugin fails to import, the exception propagates up through Django's app
startup chain (`qm/apps.py` → `qm/signals.py` → `qm/utils.py`) and kills the process.

## Affected Files

| File | What it loads |
|------|---------------|
| `qm/utils.py` | All **installed** plugins from `plugins/` |
| `connectors/views.py` | All **catalog** plugins from `plugins/catalog/` |
| `repos/views.py` | All **installed** plugins from `plugins/` |

## Proposed Changes

### 1. `qm/utils.py` — wrap installed plugin imports in try/except

**Before:**

```python
import importlib
import pkgutil
import plugins
all_connectors = {}
for loader, module_name, is_pkg in pkgutil.iter_modules(plugins.__path__):
    module = importlib.import_module(f"plugins.{module_name}")
    all_connectors[module_name] = module
```

**After:**

```python
import importlib
import logging
import pkgutil
import plugins

logger = logging.getLogger(__name__)

all_connectors = {}
for loader, module_name, is_pkg in pkgutil.iter_modules(plugins.__path__):
    try:
        module = importlib.import_module(f"plugins.{module_name}")
        all_connectors[module_name] = module
    except Exception as e:
        logger.warning("Could not import plugin %s: %s", module_name, e)
```

### 2. `repos/views.py` — same fix for installed plugin imports

**Before:**

```python
import importlib
import pkgutil
import plugins
all_connectors = {}
for loader, module_name, is_pkg in pkgutil.iter_modules(plugins.__path__):
    module = importlib.import_module(f"plugins.{module_name}")
    all_connectors[module_name] = module
```

**After:**

```python
import importlib
import logging
import pkgutil
import plugins

logger = logging.getLogger(__name__)

all_connectors = {}
for loader, module_name, is_pkg in pkgutil.iter_modules(plugins.__path__):
    try:
        module = importlib.import_module(f"plugins.{module_name}")
        all_connectors[module_name] = module
    except Exception as e:
        logger.warning("Could not import plugin %s: %s", module_name, e)
```

### 3. `connectors/views.py` — same fix for catalog plugin imports

**Before:**

```python
import importlib
import pkgutil
import plugins.catalog
all_catalog_connectors = {}
for loader, module_name, is_pkg in pkgutil.iter_modules(plugins.catalog.__path__):
    module = importlib.import_module(f"plugins.catalog.{module_name}")
    all_catalog_connectors[module_name] = module
```

**After:**

```python
import importlib
import logging
import pkgutil
import plugins.catalog

logger = logging.getLogger(__name__)

all_catalog_connectors = {}
for loader, module_name, is_pkg in pkgutil.iter_modules(plugins.catalog.__path__):
    try:
        module = importlib.import_module(f"plugins.catalog.{module_name}")
        all_catalog_connectors[module_name] = module
    except Exception as e:
        logger.warning("Could not import catalog plugin %s: %s", module_name, e)
```

### 4. `connectors/views.py` — add pip-to-import name mapping in prerequisite check

Some pip package names differ from their Python import names. The current prerequisite
check uses the pip name for `importlib.util.find_spec()`, which fails for packages like
`beautifulsoup4` (imported as `bs4`), `google-genai` (imported as `google.genai`), or
`Pillow` (imported as `PIL`).

**Before:**

```python
def connector_prerequisites(connector_name):
    requirements = all_catalog_connectors.get(connector_name).get_requirements()

    missing = []
    for requirement in requirements:
        if importlib.util.find_spec(requirement) is None:
            missing.append(requirement)
    if missing:
        add_error_notification(f"Cannot install connector {connector_name}. Missing prerequisites: {', '.join(missing)}")
        return False

    return True
```

**After:**

```python
PIP_TO_IMPORT = {
    'beautifulsoup4': 'bs4',
    'google-genai':   'google.genai',
    'Pillow':         'PIL',
}

def connector_prerequisites(connector_name):
    requirements = all_catalog_connectors.get(connector_name).get_requirements()

    missing = []
    for requirement in requirements:
        import_name = PIP_TO_IMPORT.get(requirement, requirement)
        if importlib.util.find_spec(import_name) is None:
            missing.append(requirement)
    if missing:
        add_error_notification(f"Cannot install connector {connector_name}. Missing prerequisites: {', '.join(missing)}")
        return False

    return True
```

## Testing

1. **Broken plugin resilience**: Create a symlink to a non-existent catalog file
   (`ln -s plugins/catalog/fake.py plugins/fake.py`). Verify Django starts normally and
   logs a warning instead of crashing.
2. **Missing dependency resilience**: Install a plugin whose pip dependency is not
   installed. Verify Django starts normally with a warning and the plugin is simply
   unavailable.
3. **Normal operation**: Verify all existing connectors (SentinelOne, VirusTotal, GitHub,
   Bitbucket, OpenAI, Gemini, etc.) continue to load and function correctly.
4. **Prerequisite check**: Uninstall `beautifulsoup4`, then try to install a connector
   that requires it via the Catalog UI. Verify the error message correctly reports the
   missing package.
