# Aplikacja do Analizy Danych - Streamlit

Kompleksowa aplikacja do analizy, przetwarzania i wizualizacji danych CSV za pomocą Streamlit.

### Format pliku CSV:
```csv
Name,Age,City,Salary,Department
John,25,Warsaw,5000,IT
Anna,30,Krakow,6000,HR
Peter,35,Gdansk,7000,IT
```


### Statystyki
- **Wczytywanie plików CSV** z paginacją i filtrowaniem
- **Statystyki opisowe** dla danych numerycznych i kategorycznych
- **Analiza korelacji** (Pearson, Spearman)
- **Interaktywne histogramy** i mapy cieplne

### Przetwarzanie
- **Ekstrakcja podtablic** - usuwanie/zachowywanie wierszy i kolumn
- **Zastępowanie wartości** - manualne i automatyczne
- **Skalowanie danych** - MinMaxScaler, StandardScaler
- **Obsługa brakujących danych** - usuwanie lub wypełnianie
- **Usuwanie duplikatów**
- **Kodowanie zmiennych kategorycznych** - One-Hot, Binary, Label Encoding

### Wizualizacje
- **8 typów wykresów**: słupkowy, liniowy, punktowy, kołowy, histogram, pudełkowy, mapa cieplna, skrzypcowy
- **Interaktywne wykresy** z Plotly
- **Macierz wykresów punktowych**
- **Wykresy porównawcze**

## Instalacja

1. **Klonuj repozytorium**:
```bash
git clone <repo-url>
```
2. **Utwórz wirtualne środowisko**:
```bash
python -m venv .venv
```
**oraz aktywuj w zależności od shella**:
```bash
./.venv/Scripts/activate.bat
```

3. **Zainstaluj zależności**:
```bash
pip install -r requirements.txt
```

4. **Uruchom aplikację przez przegladarke**:
```bash
streamlit run src/pp.py
```

5. **Uruchom aplikacje w trybie desktopowym**:
```bash
python src/main.py
```

6. **Tworzenie pliku exe**:
```bash
pyinstaller --onefile --clean --add-binary ".venv/Scripts/streamlit.exe;." --add-data "src;src" src/main.py #plik binarny zostanie stworzony w katalogu dist
```
## Struktura projektu

```
streamlit-data-analysis/
├── requirements.txt       # Zależności
├── README.md             # Dokumentacja
└── src/                  # Moduły źródłowe
    ├── app.py            # Główny plik aplikacji
    ├── main.py           # Skrypt uruchamiajacy aplikacje w pywebview
    ├── utils.py          # Funkcje pomocnicze
    ├── statistics.py     # Moduł statystyk
    ├── processing.py     # Moduł przetwarzania
    └── visualization.py  # Moduł wizualizacji
```

## Wymagania systemowe

- Python 3.8+
- Streamlit 1.28.0+
- Pandas 2.0.0+
- NumPy 1.24.0+
- Plotly 5.15.0+
- Scikit-learn 1.3.0+
- SciPy 1.10.0+

## Jak używać

1. **Uruchom aplikację** za pomocą `streamlit run app.py`
2. **Wczytaj plik CSV** w panelu bocznym
3. **Eksploruj dane** w zakładce "Statystyki"
4. **Przetwarzaj dane** w zakładce "Przetwarzanie"
5. **Twórz wizualizacje** w zakładce "Wizualizacje"

## Przykłady użycia

### Ekstrakcja podtablic
- Usuń wiersze: `1,3,5` lub `1-5` lub `1,3-5,7`
- Zachowaj tylko wybrane kolumny
- Formatuj dane według potrzeb

### Zastępowanie wartości
- **Automatyczne**: zamień wszystkie 'a' na 'b' w wybranej kolumnie
- **Manualne**: edytuj dane bezpośrednio w tabeli

### Skalowanie danych
- **MinMaxScaler**: normalizacja do zakresu [0,1]
- **StandardScaler**: standaryzacja (średnia=0, odchylenie=1)

### Obsługa braków
- Usuń wiersze/kolumny z brakami
- Wypełnij średnią, medianą lub własną wartością

## ⚙Rozszerzenia

Aplikacja została zaprojektowana modularnie - łatwo dodać nowe funkcjonalności:

- Nowe typy wykresów w `visualization.py`
- Dodatkowe metody przetwarzania w `processing.py`
- Nowe statystyki w `statistics.py`
- Pomocnicze funkcje w `utils.py`

## 
