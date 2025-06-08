import streamlit as st
import pandas as pd
from statisticss import StatisticsModule
from processing import ProcessingModule
from visualization import VisualizationModule
from utils import load_data, initialize_session_state, paginate_dataframe

def get_feature_descriptions():
    """Zwraca słownik z opisami cech dla datasetu Credit Approval"""
    return {
        'A1': {
            'name': 'Płeć',
            'description': 'Płeć wnioskodawcy (a/b)',
            'values': 'a, b'
        },
        'A2': {
            'name': 'Wiek',
            'description': 'Wiek wnioskodawcy',
            'values': 'wartość numeryczna'
        },
        'A3': {
            'name': 'Stosunek_zadłużenia',
            'description': 'Stosunek zadłużenia wnioskodawcy',
            'values': 'wartość numeryczna'
        },
        'A4': {
            'name': 'Status_cywilny',
            'description': 'Status cywilny wnioskodawcy',
            'values': 'u, y, l, t'
        },
        'A5': {
            'name': 'Typ_klienta_banku',
            'description': 'Typ klienta banku',
            'values': 'g, p, gg'
        },
        'A6': {
            'name': 'Poziom_wykształcenia',
            'description': 'Poziom wykształcenia wnioskodawcy',
            'values': 'c, d, cc, i, j, k, m, r, q, w, x, e, aa, ff'
        },
        'A7': {
            'name': 'Branża_zatrudnienia',
            'description': 'Branża zatrudnienia wnioskodawcy',
            'values': 'v, h, bb, j, n, z, dd, ff, o'
        },
        'A8': {
            'name': 'Staż_zatrudnienia',
            'description': 'Staż zatrudnienia wnioskodawcy',
            'values': 'wartość numeryczna'
        },
        'A9': {
            'name': 'Ma_rachunek_RO',
            'description': 'Czy wnioskodawca ma rachunek RO',
            'values': 't (tak), f (nie)'
        },
        'A10': {
            'name': 'Ma_rachunek_OS',
            'description': 'Czy wnioskodawca ma rachunek OS',
            'values': 't (tak), f (nie)'
        },
        'A11': {
            'name': 'Liczba_aktywnych_kredytów',
            'description': 'Liczba aktywnych kredytów wnioskodawcy',
            'values': 'wartość numeryczna'
        },
        'A12': {
            'name': 'Posiada_inne_zobowiązania',
            'description': 'Czy wnioskodawca posiada inne zobowiązania',
            'values': 't (tak), f (nie)'
        },
        'A13': {
            'name': 'Cel_kredytu',
            'description': 'Cel kredytu wnioskodawcy',
            'values': 'g, p, s'
        },
        'A14': {
            'name': 'Długość_historii_kredytowej',
            'description': 'Długość historii kredytowej wnioskodawcy',
            'values': 'wartość numeryczna'
        },
        'A15': {
            'name': 'Roczny_dochód',
            'description': 'Roczny dochód wnioskodawcy',
            'values': 'wartość numeryczna'
        },
        'A16': {
            'name': 'Decyzja_przyznania_kredytu',
            'description': 'Decyzja przyznania kredytu',
            'values': '+ (przyznano), - (odmówiono)'
        }
    }

def show_feature_descriptions():
    """Wyświetla tabelę z opisami cech"""
    st.markdown("### 📋 Opis cech datasetu Credit Approval")
    
    descriptions = get_feature_descriptions()
    
    # Przygotuj dane do tabeli
    table_data = []
    for code, info in descriptions.items():
        table_data.append({
            'Kod cechy': code,
            'Proponowana nazwa': info['name'],
            'Opis': info['description'],
            'Możliwe wartości': info['values']
        })
    
    # Wyświetl tabelę
    df_descriptions = pd.DataFrame(table_data)
    st.dataframe(df_descriptions, use_container_width=True, hide_index=True)
    
    st.markdown("""
    **ℹ️ Informacje dodatkowe:**
    - Dataset pochodzi z UCI Machine Learning Repository
    - Wszystkie nazwy atrybutów i wartości zostały zmienione na bezsensu symbole w celu ochrony poufności
    - Zawiera 690 instancji z 15 atrybutami + klasą
    - 37 przypadków (5%) ma brakujące wartości
    - Rozkład klas: + (przyznano): 307 (44.5%), - (odmówiono): 383 (55.5%)
    """)

def main():
    st.set_page_config(
        page_title="Analiza Danych - Streamlit App",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 Aplikacja do Analizy Danych")
    
    # Checkbox w górnej części dla opisu cech
    show_descriptions = st.checkbox(
        "📖 Pokaż opis cech datasetu", 
        help="Wyświetl tabelę z opisem wszystkich kolumn w datasecie Credit Approval"
    )
    
    if show_descriptions:
        show_feature_descriptions()
        st.markdown("---")
    
    st.markdown("---")
    
    # Inicjalizacja session state
    initialize_session_state()
    
    # Wczytywanie danych
    st.sidebar.header("📁 Wczytaj dane")
    uploaded_file = st.sidebar.file_uploader(
        "Wybierz plik CSV", 
        type=['csv'],
        help="Wczytaj plik CSV do analizy",
        key="file_uploader"
    )
    
    # Sprawdzenie czy plik został wczytany lub zmieniony
    if uploaded_file is not None:
        # Sprawdź czy to nowy plik lub czy poprzedni został usunięty
        file_changed = (
            'uploaded_file_name' not in st.session_state or 
            st.session_state.get('uploaded_file_name') != uploaded_file.name or
            'current_data' not in st.session_state or
            st.session_state['current_data'] is None
        )
        
        if file_changed:
            df = load_data(uploaded_file)
            if df is not None:
                # Reset indeksu tylko przy wczytywaniu nowego pliku
                df = df.reset_index(drop=True)
                st.session_state['original_data'] = df.copy()
                st.session_state['current_data'] = df.copy()
                st.session_state['uploaded_file_name'] = uploaded_file.name
                
                # Informacje o danych
                st.sidebar.success(f"✅ Wczytano dane: {df.shape[0]} wierszy, {df.shape[1]} kolumn")
    else:
        # Jeśli nie ma pliku, wyczyść dane
        if 'current_data' in st.session_state:
            st.session_state['current_data'] = None
            st.session_state['original_data'] = None
            if 'uploaded_file_name' in st.session_state:
                del st.session_state['uploaded_file_name']
    
    # Wyświetlanie DataFrame nad zakładkami
    if 'current_data' in st.session_state and st.session_state['current_data'] is not None:
        df = st.session_state['current_data']
        
        # Sekcja głównego datasetu
        st.header("📋 Główny dataset (edytowalny)")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Wiersze", len(df))
        with col2:
            st.metric("Kolumny", len(df.columns))
        with col3:
            st.metric("Brakujące wartości", df.isnull().sum().sum())
        with col4:
            st.metric("Duplikaty", df.duplicated().sum())
        
        # Opcje wyświetlania i kontroli
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.write("")  # Pusty placeholder
        with col2:
            refresh_button = st.button("🔄 Odśwież zmiany", help="Zastosuj wprowadzone zmiany do datasetu")
        with col3:
            reset_button = st.button("↩️ Resetuj do oryginalnych", help="Przywróć oryginalne dane")
        
        # Obsługa przycisków
        if reset_button:
            if 'original_data' in st.session_state:
                # Reset indeksu tylko przy resetowaniu do oryginalnych danych
                original_data = st.session_state['original_data'].copy().reset_index(drop=True)
                st.session_state['current_data'] = original_data
                st.success("Przywrócono oryginalne dane!")
                st.rerun()
        
        # Edytowalny DataFrame - zawsze pełny z scrollem
        st.warning("💡 Edytuj dane bezpośrednio w tabeli poniżej, następnie kliknij 'Odśwież zmiany'")
        
        # Dodanie indeksów jako kolumny dla lepszej widoczności
        df_with_index = df.copy()
        df_with_index.insert(0, 'Index', df_with_index.index)
        
        # Zawsze pełny dataset z scrollem
        edited_df = st.data_editor(
            df_with_index,
            use_container_width=True,
            height=600,  # Zwiększona wysokość dla lepszego scrollingu
            key="main_data_editor",
            num_rows="dynamic",  # Pozwala dodawać/usuwać wiersze
            column_config={
                "Index": st.column_config.NumberColumn(
                    "Index",
                    help="Indeks wiersza",
                    disabled=True,  # Nie można edytować indeksu
                    width="small"
                )
            }
        )
        
        # Zastosowanie zmian
        if refresh_button:
            if not edited_df.equals(df_with_index):
                # Usuń kolumnę Index przed zapisaniem, ale zachowaj oryginalne indeksy DataFrame
                final_df = edited_df.drop('Index', axis=1)
                # NIE rób reset_index - zachowaj oryginalne indeksy
                st.session_state['current_data'] = final_df.copy()
                st.success("✅ Zmiany zostały zastosowane do datasetu!")
                st.rerun()
            else:
                st.info("ℹ️ Brak zmian do zastosowania")
        
        st.markdown("---")
        
        # Główne zakładki
        tab1, tab2, tab3 = st.tabs(["📈 Statystyki", "🔧 Przetwarzanie", "📊 Wizualizacje"])
        
        with tab1:
            stats_module = StatisticsModule()
            stats_module.render(st.session_state['current_data'])
        
        with tab2:
            proc_module = ProcessingModule()
            # Przetwarzanie wpływa na główny dataset
            st.session_state['current_data'] = proc_module.render(st.session_state['current_data'])
        
        with tab3:
            viz_module = VisualizationModule()
            viz_module.render(st.session_state['current_data'])
    else:
        st.info("👈 Wczytaj plik CSV w panelu bocznym, aby rozpocząć analizę")
        
        # Przykładowe dane
        st.subheader("🎯 Jak używać aplikacji:")
        st.markdown("""
        1. **Wczytaj dane**: Użyj panelu bocznego, aby wczytać plik CSV
        2. **Edytuj dane**: Modyfikuj dane bezpośrednio w edytowalnej tabeli
        3. **Odśwież zmiany**: Kliknij przycisk 'Odśwież zmiany' aby zastosować edycje
        4. **Statystyki**: Przeglądaj podstawowe statystyki i korelacje
        5. **Przetwarzanie**: Modyfikuj i czyść dane (zmiany wpływają na główny dataset)
        6. **Wizualizacje**: Twórz wykresy i analizy wizualne
        """)

if __name__ == "__main__":
    main()