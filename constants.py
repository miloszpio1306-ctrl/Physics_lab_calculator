#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stale fizyczne uzywane w obliczeniach rachunku niepewnosci pomiarowych.
"""

import math

PHYSICAL_CONSTANTS = {
    "mu_0": {"val": 4.0 * math.pi * 1e-7, "unit": "H/m", "desc": "Przenikalnosc magnetyczna prozni"},
    "c": {"val": 299792458.0, "unit": "m/s", "desc": "Predkosc swiatla w prozni"},
    "h": {"val": 6.62607015e-34, "unit": "J*s", "desc": "Stala Plancka"},
    "hbar": {"val": 1.054571817e-34, "unit": "J*s", "desc": "Zredukowana stala Plancka"},
    "q_e": {"val": 1.602176634e-19, "unit": "C", "desc": "Ladunek elementarny elektronu"},
    "m_e": {"val": 9.1093837015e-31, "unit": "kg", "desc": "Masa spoczynkowa elektronu"},
    "m_p": {"val": 1.67262192369e-27, "unit": "kg", "desc": "Masa spoczynkowa protonu"},
    "k_B": {"val": 1.380649e-23, "unit": "J/K", "desc": "Stala Boltzmanna"},
    "N_A": {"val": 6.02214076e23, "unit": "1/mol", "desc": "Stala Avogadra"},
    "R_gas": {"val": 8.314462618, "unit": "J/(mol*K)", "desc": "Uniwersalna stala gazowa R"},
    "G_grav": {"val": 6.67430e-11, "unit": "m^3/(kg*s^2)", "desc": "Stala grawitacji G"},
    "eps_0": {"val": 8.8541878128e-12, "unit": "F/m", "desc": "Przenikalnosc elektryczna prozni"},
    "g_krk": {"val": 9.8105, "unit": "m/s^2", "desc": "Przyspieszenie ziemskie (Krakow)"},
}
