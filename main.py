#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Główny punkt wejścia (entrypoint) do Kalkulatora Laboratoryjnego Fizyki v4.0.
Uruchomienie:
    python3 main.py
"""

import sys


def check_dependencies():
    """Weryfikuje dostepnosc wymaganych bibliotek zewnetrznych."""
    missing = []
    try:
        import numpy  # noqa: F401
    except ImportError:
        missing.append("numpy")

    try:
        import sympy  # noqa: F401
    except ImportError:
        missing.append("sympy")

    if missing:
        print("=================================================================")
        print(f"BŁĄD: Brak wymaganych bibliotek: {', '.join(missing)}")
        print("Zainstaluj je komendą: pip install -r requirements.txt")
        print("=================================================================")
        sys.exit(1)


def main():
    check_dependencies()
    from server import run_server
    run_server()


if __name__ == "__main__":
    main()
