#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Silnik obliczeniowy rachunku niepewnosci pomiarowych (typ A, typ B, niepewnosc zlozona i rozszerzona).
Obsluguje obliczenia punkt-po-punkcie (jak w arkuszach Excel) oraz metode klasyczna.
"""

import math
import re
import numpy as np
import sympy as sp
from constants import PHYSICAL_CONSTANTS


def parse_number_series(raw_str: str):
    """
    Parsuje ciag znakow zawierajacy serie liczb oddzielonych spacjami, przecinkami lub srednikami.
    Obsluguje zarowno kropke jak i przecinek jako separator dziesietny.
    """
    if not raw_str or not str(raw_str).strip():
        return []
    s = str(raw_str).strip()
    if "." in s:
        tokens = re.split(r"[\s,;]+", s)
    else:
        if re.search(r"[\s;\n]", s):
            s_norm = s.replace(",", ".")
            tokens = re.split(r"[\s;]+", s_norm)
        else:
            s_norm = s.replace(",", ".")
            tokens = [s_norm]
    return [float(t.strip()) for t in tokens if t.strip()]


def format_with_uncertainty(value: float, unc: float, sig_digits: int = 2):
    """
    Formatuje wynik wraz z niepewnoscia zgodnie z zasadami zaokraglania (domyslnie 2 cyfry znaczace niepewnosci).
    Zwraca krotke: (tekst_zwykly, niepewnosc_tekst, tekst_latex).
    """
    if unc <= 0 or math.isnan(unc) or math.isinf(unc):
        return f"{value:.6g}", "0", f"{value:.6g} \\pm 0"
    exponent = math.floor(math.log10(abs(unc)))
    decimals = -exponent + (sig_digits - 1)
    if abs(value) >= 1e4 or (abs(value) > 0 and abs(value) < 1e-3):
        base_exp = math.floor(math.log10(abs(value))) if value != 0 else exponent
        scaled_val = value / (10 ** base_exp)
        scaled_unc = unc / (10 ** base_exp)
        unc_exp = math.floor(math.log10(abs(scaled_unc)))
        dec = max(0, -unc_exp + (sig_digits - 1))
        val_s = f"{scaled_val:.{dec}f}"
        unc_s = f"{scaled_unc:.{dec}f}"
        latex_s = f"({val_s} \\pm {unc_s}) \\cdot 10^{{{base_exp}}}"
        return f"({val_s} +/- {unc_s}) * 10^{base_exp}", f"{unc_s}e{base_exp}", latex_s
    if decimals >= 0:
        val_s = f"{round(value, decimals):.{decimals}f}"
        unc_s = f"{round(unc, decimals):.{decimals}f}"
    else:
        factor = 10 ** (-decimals)
        val_s = f"{int(round(value / factor) * factor)}"
        unc_s = f"{int(round(unc / factor) * factor)}"
    return f"{val_s} +/- {unc_s}", unc_s, f"{val_s} \\pm {unc_s}"


def compute_u_b(val: float, delta_val: float, dist_type: str):
    """
    Oblicza niepewnosc standardowa typu B w zaleznosci od przyjetego rozkladu prawdopodobienstwa.
    - 'uniform': rozklad prostokatny (delta / sqrt(3))
    - 'triangular': rozklad trojkatny (delta / sqrt(6))
    - 'direct' lub inny: bezposrednia wartosc niepewnosci dzialki
    """
    if dist_type == "uniform":
        return delta_val / math.sqrt(3.0)
    elif dist_type == "triangular":
        return delta_val / math.sqrt(6.0)
    else:
        return delta_val


def compute_multi_targets(payload: dict):
    """
    Glowna funkcja analityczna kalkulatora.
    Przelicza wiele szukanych wielkosci (wzorow) na wspolnym zestawie zmiennych pomiarowych.
    """
    calc_mode = payload.get("calc_mode", "point_by_point")
    sig_digits = int(payload.get("sig_digits", 2))
    k_factor = float(payload.get("k_factor", 1.0))
    variables_input = payload.get("variables", [])
    targets_input = payload.get("targets", [])

    # Kompatybilnosc wsteczna gdyby przeslano pojedynczy wzor
    if not targets_input and payload.get("formula"):
        targets_input = [{
            "symbol": payload.get("target_symbol", "y"),
            "unit": payload.get("target_unit", ""),
            "formula": payload.get("formula", ""),
            "ref_value": payload.get("ref_value", "")
        }]

    active_targets = [t for t in targets_input if str(t.get("formula", "")).strip()]
    if not active_targets:
        raise ValueError("Wprowadz co najmniej jeden wzor pomiarowy w sekcji 1.")

    local_dict = {}
    const_subs = {}
    for c_name, c_info in PHYSICAL_CONSTANTS.items():
        sym = sp.Symbol(c_name, real=True)
        local_dict[c_name] = sym
        const_subs[sym] = c_info["val"]

    parsed_vars = []
    var_symbols = {}
    for v in variables_input:
        v_name = v.get("name", "").strip()
        if not v_name:
            continue
        if v_name in PHYSICAL_CONSTANTS:
            raise ValueError(f"Symbol '{v_name}' jest wbudowana stala fizyczna (nie dodawaj go jako zmiennej).")
        series = parse_number_series(v.get("raw_values", ""))
        if not series:
            raise ValueError(f"Zmienna '{v_name}' nie ma wpisanych wartosci pomiarowych.")
        delta_raw = str(v.get("delta", "0")).strip().replace(",", ".")
        delta_val = float(delta_raw) if delta_raw else 0.0
        dist_type = v.get("dist_type", "direct")

        sym = sp.Symbol(v_name, real=True)
        local_dict[v_name] = sym
        var_symbols[v_name] = sym
        parsed_vars.append({
            "name": v_name,
            "unit": v.get("unit", "").strip(),
            "series": series,
            "delta": delta_val,
            "dist_type": dist_type,
            "sym": sym,
        })

    if not parsed_vars:
        raise ValueError("Dodaj i uzupelnij co najmniej jedna zmienna pomiarowa w sekcji 2.")

    # Statystyki zmiennych wejsciowych
    val_subs_mean = dict(const_subs)
    var_stats = []
    for pv in parsed_vars:
        series = pv["series"]
        n = len(series)
        mean_val = float(np.mean(series))
        u_a = float(np.std(series, ddof=1) / math.sqrt(n)) if (n > 1 and calc_mode == "mean_first") else 0.0
        u_b = compute_u_b(mean_val, pv["delta"], pv["dist_type"])
        u_c = math.hypot(u_a, u_b)
        val_subs_mean[pv["sym"]] = mean_val
        var_stats.append({
            "name": pv["name"],
            "unit": pv["unit"],
            "n": n,
            "mean": mean_val,
            "u_a": u_a,
            "u_b": u_b,
            "u_c": u_c,
        })

    # Pozwalamy, aby kolejne wzory mogly korzystac z wczesniej zdefiniowanych szukanych wielkosci (np. B -> e_m)
    defined_target_exprs = {}
    results_list = []

    for idx_t, t_item in enumerate(active_targets):
        target_symbol = str(t_item.get("symbol", f"y_{idx_t+1}")).strip() or f"y_{idx_t+1}"
        target_unit = str(t_item.get("unit", "")).strip()
        formula_str = str(t_item.get("formula", "")).strip()
        ref_val_raw = str(t_item.get("ref_value", "")).strip()

        formula_clean = formula_str.replace("^", "**")
        try:
            raw_expr = sp.sympify(formula_clean, locals=local_dict)
        except Exception as e:
            raise ValueError(f"Blad skladni we wzorze na '{target_symbol}' ({formula_str}): {e}")

        # Podstawienie wczesniej wyliczonych szukanych wielkosci (jesli uzyto ich symbolu we wzorze)
        expr = raw_expr.subs(defined_target_exprs)

        for fs in expr.free_symbols:
            if fs not in const_subs and fs not in var_symbols.values():
                raise ValueError(
                    f"Symbol '{fs}' we wzorze na '{target_symbol}' nie zostal zdefiniowany w zmiennych pomiarowych."
                )

        # Zapisujemy wyrazenie pod symbolem tej niewiadomej dla kolejnych wzorow
        t_sym = sp.Symbol(target_symbol, real=True)
        local_dict[target_symbol] = t_sym
        defined_target_exprs[t_sym] = expr

        derivatives = {pv["name"]: sp.diff(expr, pv["sym"]) for pv in parsed_vars}

        if calc_mode == "point_by_point":
            max_len = max(len(pv["series"]) for pv in parsed_vars)
            for pv in parsed_vars:
                if len(pv["series"]) != 1 and len(pv["series"]) != max_len:
                    raise ValueError(
                        f"Zmienna '{pv['name']}' ma {len(pv['series'])} wartosci, a inne maja {max_len}. "
                        f"Wpisz albo 1 wartosc (stala), albo dokladnie {max_len} wartosci."
                    )

            point_rows = []
            y_list = []
            ub_list = []

            for idx in range(max_len):
                subs_i = dict(const_subs)
                row_vals = {}
                for pv in parsed_vars:
                    val_i = pv["series"][0] if len(pv["series"]) == 1 else pv["series"][idx]
                    subs_i[pv["sym"]] = val_i
                    row_vals[pv["name"]] = val_i

                y_i = float(expr.evalf(subs=subs_i))
                var_b_i = 0.0
                for pv in parsed_vars:
                    val_i = row_vals[pv["name"]]
                    u_b_xi = compute_u_b(val_i, pv["delta"], pv["dist_type"])
                    d_val_i = float(derivatives[pv["name"]].evalf(subs=subs_i))
                    var_b_i += (d_val_i * u_b_xi) ** 2

                u_b_yi = math.sqrt(var_b_i)
                y_list.append(y_i)
                ub_list.append(u_b_yi)
                point_rows.append({"idx": idx + 1, "vals": row_vals, "y": y_i, "u_b": u_b_yi})

            y_val = float(np.mean(y_list))
            u_a_y = float(np.std(y_list, ddof=1) / math.sqrt(max_len)) if max_len > 1 else 0.0
            u_b_y = float(np.mean(ub_list))
            u_c_y = math.hypot(u_a_y, u_b_y)
        else:
            point_rows = None
            u_a_y = 0.0
            u_b_y = 0.0

        partials_info = []
        variance_sum = 0.0
        variance_a_sum = 0.0
        variance_b_sum = 0.0
        latex_partial_terms = []

        for vs in var_stats:
            v_name = vs["name"]
            d_expr = derivatives[v_name]
            d_val = float(d_expr.evalf(subs=val_subs_mean))
            contrib = abs(d_val) * vs["u_c"]
            variance_contrib = contrib ** 2
            variance_sum += variance_contrib
            variance_a_sum += (abs(d_val) * vs["u_a"]) ** 2
            variance_b_sum += (abs(d_val) * vs["u_b"]) ** 2
            d_latex = sp.latex(d_expr)
            if d_expr != 0 and vs["u_c"] > 0:
                latex_partial_terms.append(f"\\left( {d_latex} \\cdot u({v_name}) \\right)^2")
            partials_info.append({
                "name": v_name,
                "derivative_expr": str(d_expr),
                "derivative_val": d_val,
                "contribution": contrib,
                "variance_contrib": variance_contrib,
            })

        for p in partials_info:
            p["share_pct"] = (p["variance_contrib"] / variance_sum * 100.0) if variance_sum > 0 else 0.0

        partials_sorted = sorted(partials_info, key=lambda x: x["share_pct"], reverse=True)
        dominant_source = partials_sorted[0] if partials_sorted else None

        if calc_mode == "mean_first":
            y_val = float(expr.evalf(subs=val_subs_mean))
            u_a_y = math.sqrt(variance_a_sum)
            u_b_y = math.sqrt(variance_b_sum)
            u_c_y = math.sqrt(variance_sum)

        u_exp_y = k_factor * u_c_y
        rel_y_pct = (u_c_y / abs(y_val) * 100.0) if y_val != 0 else 0.0
        fmt_y, _, fmt_y_latex = format_with_uncertainty(y_val, u_c_y, sig_digits)
        fmt_y_exp, _, _ = format_with_uncertainty(y_val, u_exp_y, sig_digits)

        ref_comparison = None
        if ref_val_raw:
            ref_val = float(ref_val_raw.replace(",", "."))
            diff = abs(y_val - ref_val)
            rel_diff_pct = (diff / abs(ref_val) * 100.0) if ref_val != 0 else 0.0
            z_score = (diff / u_c_y) if u_c_y > 0 else 0.0
            fits_k = diff <= u_exp_y
            fits_2 = diff <= (2.0 * u_c_y)
            ref_comparison = {
                "ref_val": ref_val,
                "diff": diff,
                "rel_diff_pct": rel_diff_pct,
                "k_factor": k_factor,
                "u_exp": u_exp_y,
                "lower_bound": y_val - u_exp_y,
                "upper_bound": y_val + u_exp_y,
                "z_score": z_score,
                "fits_k": fits_k,
                "fits_2": fits_2,
            }

        formula_latex = sp.latex(raw_expr)
        explicit_sum_latex = " + ".join(latex_partial_terms) if latex_partial_terms else "0"
        unit_suffix = f"\\;\\mathrm{{[{target_unit}]}}" if target_unit else ""

        latex_report = f"""% --- WZOR POMIAROWY ({target_symbol}) ---
\\begin{{equation}}
    {target_symbol} = {formula_latex}
\\end{{equation}}

\\begin{{equation}}
    u_B({target_symbol}) = \\sqrt{{{explicit_sum_latex}}}
\\end{{equation}}

% Srednia: {y_val:.5e}, u_A = {u_a_y:.4e}, u_B = {u_b_y:.4e}, u_c = {u_c_y:.4e}
\\begin{{equation}}
    {target_symbol} = {fmt_y_latex}{unit_suffix} \\quad \\left( \\delta {target_symbol} = {rel_y_pct:.2f}\\% \\right)
\\end{{equation}}
"""

        results_list.append({
            "calc_mode": calc_mode,
            "target_symbol": target_symbol,
            "target_unit": target_unit,
            "formula_str": formula_str,
            "formula_latex": formula_latex,
            "explicit_sum_latex": explicit_sum_latex,
            "y_val": y_val,
            "u_a_y": u_a_y,
            "u_b_y": u_b_y,
            "u_c_y": u_c_y,
            "u_exp_y": u_exp_y,
            "k_factor": k_factor,
            "rel_y_pct": rel_y_pct,
            "formatted_result": fmt_y,
            "formatted_expanded": fmt_y_exp,
            "partials": partials_info,
            "dominant_source": dominant_source,
            "point_rows": point_rows,
            "ref_comparison": ref_comparison,
            "latex_report": latex_report,
        })

    return {
        "calc_mode": calc_mode,
        "k_factor": k_factor,
        "var_stats": var_stats,
        "targets_results": results_list,
    }
