# Aplikacja do Analizy Danych - Streamlit

Kompleksowa aplikacja do analizy, przetwarzania i wizualizacji danych CSV za pomocą Streamlit.

## 🐛 Rozwiązywanie problemów

### Częste problemy:

1. **Błąd importu modułów**:
   - Upewnij się, że struktura katalogów jest prawidłowa
   - Dodaj pusty plik `__init__.py` w katalogu `src/`

2. **Błędy z danymi**:
   - Sprawdź kodowanie pliku CSV (UTF-8)
   - Upewnij się, że separatorem jest przecinek

3. **Problemy z wykresami**:
   - Sprawdź czy wybrane kolumny zawierają odpowiednie typy danych
   - Dla wykresów kołowych użyj danych kategorycznych

### Wskazówki:

- **Duże pliki**: Użyj filtrów i paginacji dla lepszej wydajności
- **Brakujące dane**: Sprawdź statystyki przed przetwarzaniem
- **Korelacje**: Wybierz maksymalnie 10 kolumn dla czytelności

## 📝 Przykładowe dane

Aplikacja najlepiej działa z danymi zawierającymi:
- **Kolumny numeryczne**: dla statystyk i wykresów
- **Kolumny kategoryczne**: dla filtrowania i grupowania
- **Daty**: dla wykresów czasowych

### Format pliku CSV:
```csv
Name,Age,City,Salary,Department
John,25,Warsaw,5000,IT
Anna,30,Krakow,6000,HR
Peter,35,Gdansk,7000,IT
```

## 🔧 Konfiguracja

### Dostosowanie aplikacji:

1. **Zmiana motywu**: Edytuj `.streamlit/config.toml`
2. **Dodanie logo**: Umieść w katalogu `assets/`
3. **Nowe moduły**: Dodaj w katalogu `src/`

### Parametry w `app.py`:
```python
st.set_page_config(
    page_title="Twoja Aplikacja",
    page_icon="📊",
    layout="wide"
)
```

## 📚 API Reference

### utils.py
- `load_data(file)` - Wczytuje CSV
- `parse_indices(string)` - Parsuje indeksy
- `get_numeric_columns(df)` - Zwraca kolumny numeryczne
- `paginate_dataframe(df)` - Paginacja danych

### statistics.py
- `StatisticsModule.render(df)` - Renderuje statystyki
- `_pearson_correlation(df)` - Korelacja Pearsona
- `_spearman_correlation(df)` - Korelacja Spearmana

### processing.py
- `ProcessingModule.render(df)` - Renderuje przetwarzanie
- `_handle_missing_data(df)` - Obsługa braków
- `_handle_scaling(df)` - Skalowanie danych

### visualization.py
- `VisualizationModule.render(df)` - Renderuje wykresy
- `_create_[chart_type](df, options)` - Tworzy wykresy

## 🤝 Współpraca

Aby przyczynić się do rozwoju projektu:

1. **Fork** repozytorium
2. **Utwórz branch** dla nowej funkcjonalności
3. **Dodaj testy** dla nowego kodu
4. **Wyślij Pull Request**

### Zasady kodowania:
- Używaj docstringów dla funkcji
- Przestrzegaj PEP 8
- Dodawaj komentarze dla skomplikowanej logiki
- Testuj przed commitowaniem

## 📄 Licencja

MIT License - zobacz plik LICENSE dla szczegółów.

## 👨‍💻 Autor

Aplikacja stworzona jako kompletne rozwiązanie do analizy danych w Streamlit.

---

**Uwaga**: Aplikacja jest ciągle rozwijana. Zgłaszaj błędy i sugestie przez Issues.🚀 Funkcjonalności

### 📈 Statystyki
- **Wczytywanie plików CSV** z paginacją i filtrowaniem
- **Statystyki opisowe** dla danych numerycznych i kategorycznych
- **Analiza korelacji** (Pearson, Spearman)
- **Interaktywne histogramy** i mapy cieplne

### 🔧 Przetwarzanie
- **Ekstrakcja podtablic** - usuwanie/zachowywanie wierszy i kolumn
- **Zastępowanie wartości** - manualne i automatyczne
- **Skalowanie danych** - MinMaxScaler, StandardScaler
- **Obsługa brakujących danych** - usuwanie lub wypełnianie
- **Usuwanie duplikatów**
- **Kodowanie zmiennych kategorycznych** - One-Hot, Binary, Label Encoding

### 📊 Wizualizacje
- **8 typów wykresów**: słupkowy, liniowy, punktowy, kołowy, histogram, pudełkowy, mapa cieplna, skrzypcowy
- **Interaktywne wykresy** z Plotly
- **Macierz wykresów punktowych**
- **Wykresy porównawcze**

## 🛠️ Instalacja

1. **Klonuj repozytorium**:
```bash
git clone <repo-url>
cd streamlit-data-analysis
```

2. **Zainstaluj zależności**:
```bash
pip install -r requirements.txt
```

3. **Uruchom aplikację**:
```bash
streamlit run app.py
```

## 📁 Struktura projektu

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

## 📋 Wymagania systemowe

- Python 3.8+
- Streamlit 1.28.0+
- Pandas 2.0.0+
- NumPy 1.24.0+
- Plotly 5.15.0+
- Scikit-learn 1.3.0+
- SciPy 1.10.0+

## 🎯 Jak używać

1. **Uruchom aplikację** za pomocą `streamlit run app.py`
2. **Wczytaj plik CSV** w panelu bocznym
3. **Eksploruj dane** w zakładce "Statystyki"
4. **Przetwarzaj dane** w zakładce "Przetwarzanie"
5. **Twórz wizualizacje** w zakładce "Wizualizacje"

## 📊 Przykłady użycia

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

## ⚙️ Rozszerzenia

Aplikacja została zaprojektowana modularnie - łatwo dodać nowe funkcjonalności:

- Nowe typy wykresów w `visualization.py`
- Dodatkowe metody przetwarzania w `processing.py`
- Nowe statystyki w `statistics.py`
- Pomocnicze funkcje w `utils.py`

## 