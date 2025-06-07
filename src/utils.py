import streamlit as st
import pandas as pd
import numpy as np
from typing import List, Union, Optional

def load_data(uploaded_file) -> Optional[pd.DataFrame]:
    """Wczytuje dane z pliku CSV z obsługą błędów i specjalnych wartości brakujących"""
    try:
        # Wczytaj CSV z obsługą różnych oznaczeń brakujących wartości
        df = pd.read_csv(
            uploaded_file, 
            na_values=['?', 'NA', 'N/A', 'null', 'NULL', '', ' ', 'nan', 'NaN'],
            keep_default_na=True
        )
        
        # Próbuj skonwertować kolumny na właściwe typy
        df = auto_convert_dtypes(df)
        
        return df
    except Exception as e:
        st.error(f"Błąd podczas wczytywania pliku: {str(e)}")
        return None

def auto_convert_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    """Automatycznie konwertuje typy danych kolumn"""
    df_converted = df.copy()
    
    for col in df_converted.columns:
        # Sprawdź czy można skonwertować na numeric
        if df_converted[col].dtype == 'object':
            # Usuń braki i spróbuj konwertować
            non_null_values = df_converted[col].dropna()
            
            if len(non_null_values) > 0:
                # Sprawdź czy wszystkie wartości można skonwertować na liczby
                numeric_count = 0
                for val in non_null_values:
                    try:
                        pd.to_numeric(str(val), errors='raise')
                        numeric_count += 1
                    except (ValueError, TypeError):
                        break
                
                # Jeśli wszystkie wartości są numeryczne, konwertuj kolumnę
                if numeric_count == len(non_null_values):
                    try:
                        df_converted[col] = pd.to_numeric(df_converted[col], errors='coerce')
                        st.info(f"Kolumna '{col}' została skonwertowana na typ numeryczny")
                    except:
                        pass  # Zostaw jako object jeśli konwersja się nie powiedzie
    
    return df_converted

def initialize_session_state():
    """Inicjalizuje session state dla aplikacji"""
    if 'original_data' not in st.session_state:
        st.session_state['original_data'] = None
    if 'current_data' not in st.session_state:
        st.session_state['current_data'] = None

def parse_indices(indices_str: str, max_index: int) -> List[int]:
    """
    Parsuje string z indeksami w formacie "0,2,4" lub "0-4" lub "0,2-4,6"
    Zwraca listę indeksów (0-based)
    """
    if not indices_str.strip():
        return []
    
    indices = []
    parts = indices_str.split(',')
    
    for part in parts:
        part = part.strip()
        if '-' in part:
            # Zakres
            try:
                start, end = map(int, part.split('-'))
                # Już 0-based, sprawdź granice
                start = max(0, start)
                end = min(max_index - 1, end)
                indices.extend(range(start, end + 1))
            except ValueError:
                st.error(f"Nieprawidłowy zakres: {part}")
        else:
            # Pojedynczy indeks
            try:
                idx = int(part)
                if 0 <= idx < max_index:
                    indices.append(idx)
                else:
                    st.error(f"Indeks {idx} poza zakresem (0-{max_index-1})")
            except ValueError:
                st.error(f"Nieprawidłowy indeks: {part}")
    
    return sorted(list(set(indices)))

def get_numeric_columns(df: pd.DataFrame) -> List[str]:
    """Zwraca listę kolumn numerycznych (int, float)"""
    if df is None or df.empty:
        return []
    
    # Pobierz kolumny numeryczne
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    return numeric_cols

def get_categorical_columns(df: pd.DataFrame) -> List[str]:
    """Zwraca listę kolumn kategorycznych (tylko rzeczywiście tekstowe)"""
    if df is None or df.empty:
        return []
    
    # Pobierz kolumny object i category
    potential_categorical = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    # Sprawdź które kolumny są rzeczywiście kategoryczne (nie numeryczne w stringu)
    truly_categorical = []
    
    for col in potential_categorical:
        # Pobierz próbkę bez braków
        sample = df[col].dropna()
        
        if len(sample) == 0:
            continue  # Pomiń kolumny z samymi brakami
        
        # Sprawdź czy próbka zawiera głównie tekst
        numeric_convertible = 0
        total_values = min(100, len(sample))  # Sprawdź maksymalnie 100 wartości
        
        for val in sample.head(total_values):
            try:
                # Próbuj skonwertować na float
                float(str(val).strip())
                numeric_convertible += 1
            except (ValueError, TypeError):
                pass
        
        # Jeśli mniej niż 70% wartości to liczby, traktuj jako kategoryczną
        if total_values > 0 and (numeric_convertible / total_values) < 0.7:
            truly_categorical.append(col)
    
    return truly_categorical

def paginate_dataframe(df: pd.DataFrame, page_size: int = 50) -> pd.DataFrame:
    """Paginuje DataFrame"""
    if len(df) <= page_size:
        return df
    
    num_pages = len(df) // page_size + (1 if len(df) % page_size > 0 else 0)
    page = st.selectbox(
        f"Strona (wyświetlane {page_size} wierszy na stronę):",
        range(1, num_pages + 1),
        key="pagination"
    )
    
    start_idx = (page - 1) * page_size
    end_idx = min(start_idx + page_size, len(df))
    
    st.info(f"Wyświetlane wiersze {start_idx + 1}-{end_idx} z {len(df)}")
    
    return df.iloc[start_idx:end_idx]

def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Dodaje filtry dla DataFrame"""
    if df is None or df.empty:
        st.warning("Brak danych do filtrowania.")
        return df if df is not None else pd.DataFrame()
    
    # Filtry dla kolumn kategorycznych
    categorical_cols = get_categorical_columns(df)
    filters = {}
    
    if categorical_cols:
        st.markdown(f"**Dostępne filtry kategoryczne:** {', '.join(categorical_cols)}")
        cols = st.columns(min(len(categorical_cols), 3))
        for i, col in enumerate(categorical_cols):
            with cols[i % 3]:
                unique_values = df[col].dropna().unique()
                if len(unique_values) <= 50:  # Zwiększona liczba unikalnych wartości
                    selected = st.multiselect(
                        f"Filtruj {col}:",
                        options=sorted(unique_values),  # Posortowane opcje
                        key=f"filter_{col}"
                    )
                    if selected:
                        filters[col] = selected
                else:
                    st.info(f"Kolumna {col} ma za dużo unikalnych wartości ({len(unique_values)}) do filtrowania")
    else:
        st.info("Brak kolumn kategorycznych dostępnych do filtrowania")
    
    # Zastosowanie filtrów
    filtered_df = df.copy()
    for col, values in filters.items():
        filtered_df = filtered_df[filtered_df[col].isin(values)]
    
    if filters:
        st.success(f"✅ Po zastosowaniu filtrów: {len(filtered_df)} z {len(df)} wierszy")
    
    return filtered_df

def safe_mode(series: pd.Series):
    """Bezpieczne obliczanie mody"""
    try:
        mode_result = series.mode()
        if len(mode_result) > 0:
            return mode_result.iloc[0]
        return None
    except:
        return None

def format_number(value):
    """Formatuje liczby do wyświetlenia"""
    if pd.isna(value):
        return "N/A"
    if isinstance(value, (int, float)):
        if abs(value) < 0.01 and value != 0:
            return f"{value:.2e}"
        return f"{value:.4f}"
    return str(value)

def safe_metric_delta(value):
    """Bezpiecznie konwertuje wartość dla st.metric delta"""
    if value is None:
        return None
    if isinstance(value, (np.integer, np.floating)):
        return float(value)
    if isinstance(value, (int, float, str)):
        return value
    return None
