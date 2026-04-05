"""
FR #327 - Create config_appsetting table for Web GUI application settings (e.g. AI_CONNECTOR).

Run after deploying code that adds config.models.AppSetting:

$ source /data/venv/bin/activate
(venv) $ cd /data/deephunter/
(venv) $ python manage.py runscript upgrade.fr_327_app_setting

Alternatively: ``python manage.py makemigrations config && python manage.py migrate config``
(if you use Django migrations for the config app).
"""

from django.db import connection

from config.models import AppSetting


def run():
    table_name = AppSetting._meta.db_table
    with connection.cursor() as cursor:
        if table_name in connection.introspection.table_names(cursor):
            print(f"[i] Table {table_name} already exists — nothing to do.")
            return

    with connection.schema_editor() as editor:
        editor.create_model(AppSetting)

    print(f"[+] Created table {table_name} for AppSetting.")
