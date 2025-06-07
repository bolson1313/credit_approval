import streamlit as st
import pandas as pd
from statisticss import StatisticsModule
from processing import ProcessingModule
from visualization import VisualizationModule
from utils import load_data, initialize_session_state, paginate_dataframe

def main():
    st.set_page_config(
        page_title="Analiza Danych - Streamlit App",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 Aplikacja do Analizy Danych")
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
