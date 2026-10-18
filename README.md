# Kalkulator Laboratoryjny Fizyki

Zaawansowany kalkulator laboratoryjny do automatyzacji obliczeń i rachunku niepewności pomiarowych (metoda typu A, typu B, niepewności złożone i rozszerzone, pochodne cząstkowe, generowanie raportów w formacie LaTeX oraz zgodność z arkuszami Excel).

---

##Struktura Projektu

Projekt został podzielony na przejrzyste moduły:

```text
.
├── main.py                     # Główny punkt startowy aplikacji
├── kalkulator_fizyczny_laby.py # Alias / wrapper dla wstecznej kompatybilności
├── constants.py                # Wbudowane stałe fizyczne (mu_0, c, h, q_e, g_krk itd.)
├── calculations.py             # Silnik analityczny (rachunek niepewności, SymPy, NumPy)
├── server.py                   # Serwer HTTP, routing statyczny i API (/api/calculate)
├── index.html                  # Szablon interfejsu użytkownika
├── static/
│   ├── style.css               # Style CSS (ciemny motyw laboratoryjny)
│   └── app.js                  # Logika frontendu (zakładki, dynamiczne formularze, AJAX)
├── requirements.txt            # Zależności bibliotek Pythona
└── README.md                   # Dokumentacja projektu
```

---

##Uruchomienie

### 1. Wymagania

- Python 3.8+
- Biblioteki: `numpy`, `sympy`

Instalacja zależności:
```bash
pip install -r requirements.txt
```

###Start aplikacji

Możesz uruchomić kalkulator na dwa sposoby:

```bash
python3 main.py
```
lub:
```bash
python3 kalkulator_fizyczny_laby.py
```

Aplikacja automatycznie wyszuka wolny port (domyślnie `8790`), uruchomi lokalny serwer HTTP i otworzy kalkulator w Twojej domyślnej przeglądarce pod adresem:
`http://127.0.0.1:8790`

---

##Główne Funkcje

1. **Wiele szukanych wielkości na raz**:
   Możliwość definiowania wielu wzorów (np. obliczenie indukcji $B$, a następnie ładunku właściwego $e/m$ z wykorzystaniem policzonego $B$).
2. **Dwa tryby obliczeń**:
   - **Tabela Punkt-po-Punkcie (jak w Excelu)**: przelicza każdy punkt pomiarowy osobno wraz z niepewnością cząstkową, a na końcu wyznacza średnią i niepewność typu A i B.
   - **Klasyczny (najpierw średnia)**: uśrednia serie zmiennych i wstawia wartości średnie do prawa przenoszenia niepewności.
3. **Analiza budżetu niepewności**:
   Automatyczne liczenie pochodnych cząstkowych za pomocą `sympy` i wskazywanie dominującego źródła błędu.
4. **Weryfikacja z wartościami tablicowymi**:
   Automatyczny test zgodności z kryterium $k \cdot u_c$ oraz $2 \cdot u_c$.
5. **Eksport do LaTeX i Excel**:
   Gotowe równania w kodzie LaTeX do wklejenia do sprawozdania oraz formatowanie liczb kompatybilne z arkuszami kalkulacyjnymi.
6. **Eksport projektu (.zip)**:
   Możliwość pobrania całej spakowanej paczki projektu bezpośrednio z paska nawigacji w przeglądarce.
