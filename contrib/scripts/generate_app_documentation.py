#!/usr/bin/env python

import os
from pathlib import Path
import shutil
import sys

import django
from django.apps import apps

sys.path.insert(
    0, os.path.abspath('..')
)
sys.path.insert(
    1, os.path.abspath('.')
)

from mayan.settings import BASE_DIR


if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mayan.settings')
    django.setup()

    path_docs_apps = Path(BASE_DIR, '..', 'docs', 'apps')

    app_list = []

    for app_config in apps.get_app_configs():
        path_app_docs = Path(app_config.path, 'docs')

        path_docs_app = path_docs_apps / app_config.label

        if (path_app_docs / 'index.txt').exists():
            app_list.append(app_config.label)
            path_docs_app.mkdir(exist_ok=True, parents=True)

            try:
                shutil.copytree(
                    dirs_exist_ok=True, src=path_app_docs, dst=path_docs_app
                )
            except FileNotFoundError:
                """Non fatal, just means the app does not provide docs."""

    app_list.sort()

    with (path_docs_apps / 'index.txt').open(mode='w') as file_object:
        file_object.writelines(
            (
                'Apps\n', '====\n', '\n'
            )
        )

        for app in app_list:
            file_object.write(
                '- :doc:`{}/index`\n'.format(app)
            )

        file_object.write('\n.. toctree::\n')
        file_object.write('    :hidden:\n')
        file_object.write('\n')

        for app in app_list:
            file_object.write(
                '    {}/index\n'.format(app)
            )
