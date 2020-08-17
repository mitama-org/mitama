#!/usr/bin/python

import mitama

def main():
    try:
        from mitama.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Mitama. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line()


if __name__ == '__main__':
    main()
