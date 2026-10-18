#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kalkulator Laboratoryjny Fizyki v4.0
Plik zachowujacy kompatybilnosc wsteczna.
Projekt zostal podzielony na modulowa strukture:
  - calculations.py (silnik obliczen niepewnosci pomiarowych)
  - constants.py    (stale fizyczne)
  - server.py       (serwer HTTP i API)
  - main.py         (glowny punkt wejscia)
  - index.html      (struktura widoku)
  - static/style.css(arkusz stylow)
  - static/app.js   (logika frontendowa)

Uruchomienie:
    python3 kalkulator_fizyczny_laby.py
lub:
    python3 main.py
"""

from constants import PHYSICAL_CONSTANTS
from calculations import (
    parse_number_series,
    format_with_uncertainty,
    compute_u_b,
    compute_multi_targets,
)
from server import LabCalculatorHandler, find_free_port, run_server
from main import main

__all__ = [
    "PHYSICAL_CONSTANTS",
    "parse_number_series",
    "format_with_uncertainty",
    "compute_u_b",
    "compute_multi_targets",
    "LabCalculatorHandler",
    "find_free_port",
    "run_server",
    "main",
]

if __name__ == "__main__":
    main()