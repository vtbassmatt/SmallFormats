#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smallformats.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SECRET_KEY', 'django-insecure-r1ch4rd-g4rf13ld,-p.h.d.')

    try:
        with open('./.env') as f:
            for line in f:
                line = line.strip()
                key, value = line.split('=', 1)
                print(f"Read {key} from .env")
                os.environ.setdefault(key, value)
    except FileNotFoundError:
        pass

    main()
