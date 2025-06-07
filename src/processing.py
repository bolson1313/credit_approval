import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.preprocessing import LabelEncoder
from utils import parse_indices, get_numeric_columns, get_categorical_columns, safe_metric_delta

class ProcessingModule:
    def __init__(self):
        self.scalers = {
            'MinMaxScaler': MinMaxScaler,
            'StandardScaler': StandardScaler
        }
    
    def render(self, df: pd.DataFrame) -> pd.DataFrame:
        """Renderuje zakładkę przetwarzania"""
        if df is None or df.empty:
            st.warning("Brak danych do przetwarzania.")
            return df if df is not None else pd.DataFrame()
            
        st.header("🔧 Przetwarzanie Danych")
        st.info("⚠️ Wszystkie zmiany będą zastosowane do głównego datasetu!")
        
        # Przechowujemy oryginalny stan dla porównania
        original_df = df.copy()
        processed_df = df.copy()
        
        # Sekcje przetwarzania
        with st.expander("✂️ Ekstrakcja podtablic", expanded=False):
            new_df = self._handle_data_extraction(processed_df)
            if new_df is not None and not new_df.equals(processed_df):
                processed_df = new_df
                st.success("✅ Zastosowano zmiany w ekstrakcji danych")
        
        with st.expander("🔄 Zastępowanie wartości", expanded=False):
            new_df = self._handle_value_replacement(processed_df)
            if new_df is not None and not new_df.equals(processed_df):
                processed_df = new_df
                st.success("✅ Zastosowano zastępowanie wartości")
        
        with st.expander("📏 Skalowanie i standaryzacja", expanded=False):
            new_df = self._handle_scaling(processed_df)
            if new_df is not None and not new_df.equals(processed_df):
                processed_df = new_df
                st.success("✅ Zastosowano skalowanie danych")
        
        with st.expander("🕳️ Obsługa brakujących danych", expanded=False):
            new_df = self._handle_missing_data(processed_df)
            if new_df is not None and not new_df.equals(processed_df):
                processed_df = new_df
                st.success("✅ Zastosowano obsługę brakujących danych")
        
        with st.expander("🔂 Usuwanie duplikatów", expanded=False):
            new_df = self._handle_duplicates(processed_df)
            if new_df is not None and not new_df.equals(processed_df):
                processed_df = new_df
                st.success("✅ Usunięto duplikaty")
        
        with st.expander("🔢 Kodowanie kolumn symbolicznych", expanded=False):
            new_df = self._handle_encoding(processed_df)
            if new_df is not None and not new_df.equals(processed_df):
                processed_df = new_df
                st.success("✅ Zastosowano kodowanie kolumn")
        
        # Porównanie przed/po
        if not processed_df.equals(original_df):
            self._show_comparison(original_df, processed_df)
        
        return processed_df
    
    def _handle_data_extraction(self, df: pd.DataFrame) -> pd.DataFrame:
        """Obsługuje ekstrakcję podtablic"""
        st.subheader("Ekstrakcja wierszy i kolumn")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Wiersze:**")
            action_rows = st.radio(
                "Akcja dla wierszy:",
                ["Brak zmian", "Usuń wybrane", "Zachowaj tylko wybrane"],
                key="rows_action"
            )
            
            # Input zawsze widoczny
            rows_input = st.text_input(
                "Podaj numery wierszy (np. 0,2,4 lub 0-4 lub 0,2-4,6):",
                key="rows_input",
                help="Numeracja od 0 (pierwszy wiersz to 0)",
                disabled=(action_rows == "Brak zmian")
            )
            
            if action_rows != "Brak zmian" and rows_input:
                if st.button("Zastosuj dla wierszy", key="apply_rows"):
                    # Parsuj indeksy (już 0-based)
                    indices = parse_indices(rows_input, len(df))
                    if indices:
                        if action_rows == "Usuń wybrane":
                            # Usuń wybrane indeksy
                            remaining_indices = [i for i in range(len(df)) if i not in indices]
                            df = df.iloc[remaining_indices]
                            # NIE resetuj indeksu - zachowaj oryginalne numerowanie
                            st.success(f"Usunięto {len(indices)} wierszy")
                        else:  # Zachowaj tylko wybrane
                            df = df.iloc[indices]
                            # NIE resetuj indeksu - zachowaj oryginalne numerowanie
                            st.success(f"Zachowano {len(indices)} wierszy")
        
        with col2:
            st.markdown("**Kolumny:**")
            action_cols = st.radio(
                "Akcja dla kolumn:",
                ["Brak zmian", "Usuń wybrane", "Zachowaj tylko wybrane"],
                key="cols_action"
            )
            
            if action_cols != "Brak zmian":
                selected_cols = st.multiselect(
                    "Wybierz kolumny:",
                    df.columns.tolist(),
                    key="selected_cols"
                )
                
                if selected_cols and st.button("Zastosuj dla kolumn", key="apply_cols"):
                    if action_cols == "Usuń wybrane":
                        df = df.drop(columns=selected_cols)
                        st.success(f"Usunięto {len(selected_cols)} kolumn")
                    else:  # Zachowaj tylko wybrane
                        df = df[selected_cols]
                        st.success(f"Zachowano {len(selected_cols)} kolumn")
        
        return df
    
    def _handle_value_replacement(self, df: pd.DataFrame) -> pd.DataFrame:
        """Obsługuje zastępowanie wartości"""
        st.subheader("Zastępowanie wartości")
        
        tab1, tab2 = st.tabs(["Manual", "Automatyczne"])
        
        with tab1:
            st.markdown("**Edycja manualna:**")
            if st.checkbox("Włącz edycję manualną", key="enable_manual_edit"):
                edited_df = st.data_editor(
                    df,
                    use_container_width=True,
                    height=300,
                    key="manual_editor"
                )
                if st.button("Zastosuj zmiany manualne", key="apply_manual"):
                    df = edited_df.copy()
                    st.success("Zastosowano zmiany manualne")
        
        with tab2:
            st.markdown("**Automatyczne zastępowanie:**")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                replace_column = st.selectbox(
                    "Wybierz kolumnę:",
                    df.columns.tolist(),
                    key="replace_column"
                )
            
            with col2:
                old_value = st.text_input("Stara wartość:", key="old_value")
            
            with col3:
                new_value = st.text_input("Nowa wartość:", key="new_value")
            
            if st.button("Zastąp wartości", key="apply_replacement"):
                if replace_column and old_value:
                    count = (df[replace_column] == old_value).sum()
                    df[replace_column] = df[replace_column].replace(old_value, new_value)
                    st.success(f"Zastąpiono {count} wystąpień '{old_value}' na '{new_value}' w kolumnie '{replace_column}'")
        
        return df
    
    def _handle_scaling(self, df: pd.DataFrame) -> pd.DataFrame:
        """Obsługuje skalowanie i standaryzację"""
        st.subheader("Skalowanie i standaryzacja")
        
        # Pobierz wszystkie kolumny numeryczne z aktualnego DataFrame
        numeric_cols = get_numeric_columns(df)
        
        if not numeric_cols:
            st.warning("Brak kolumn numerycznych do skalowania.")
            return df
        
        st.info(f"Znalezione kolumny numeryczne: {', '.join(numeric_cols)}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            scaler_type = st.selectbox(
                "Wybierz metodę skalowania:",
                list(self.scalers.keys()),
                key="scaler_type"
            )
        
        with col2:
            cols_to_scale = st.multiselect(
                "Wybierz kolumny do skalowania:",
                numeric_cols,
                default=numeric_cols[:min(5, len(numeric_cols))],  # Pokaż więcej domyślnie
                key="cols_to_scale"
            )
        
        if cols_to_scale and st.button("Zastosuj skalowanie", key="apply_scaling"):
            try:
                scaler = self.scalers[scaler_type]()
                df[cols_to_scale] = scaler.fit_transform(df[cols_to_scale])
                st.success(f"Zastosowano {scaler_type} dla {len(cols_to_scale)} kolumn: {', '.join(cols_to_scale)}")
            except Exception as e:
                st.error(f"Błąd podczas skalowania: {str(e)}")
        
        return df
    
    def _handle_missing_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Obsługuje brakujące dane"""
        st.subheader("Obsługa brakujących danych")
        
        # Sprawdź różne oznaczenia braków i skonwertuj je na NaN
        st.info("🔍 Sprawdzanie oznaczeń brakujących danych...")
        
        # Lista możliwych oznaczeń braków
        missing_indicators = ['?', 'NA', 'N/A', 'null', 'NULL', '', ' ', 'nan', 'NaN', 'missing']
        
        # Znajdź i skonwertuj różne oznaczenia braków
        original_missing_count = df.isnull().sum().sum()
        
        # Zamień różne oznaczenia braków na NaN
        df_cleaned = df.copy()
        for indicator in missing_indicators:
            df_cleaned = df_cleaned.replace(indicator, np.nan)
        
        new_missing_count = df_cleaned.isnull().sum().sum()
        
        if new_missing_count > original_missing_count:
            st.success(f"🔧 Znaleziono i skonwertowano {new_missing_count - original_missing_count} dodatkowych oznaczeń braków")
            df = df_cleaned
        
        # Informacje o brakujących danych
        missing_info = df.isnull().sum()
        missing_cols = missing_info[missing_info > 0]
        
        if len(missing_cols) == 0:
            st.success("✅ Brak brakujących danych w zbiorze!")
            return df
        
        st.markdown("**Podsumowanie brakujących danych:**")
        missing_summary_df = pd.DataFrame({
            'Kolumna': missing_cols.index,
            'Liczba braków': missing_cols.values,
            'Procent braków': (missing_cols.values / len(df) * 100).round(2)
        })
        st.dataframe(missing_summary_df, use_container_width=True, hide_index=True)
        
        # Wyświetlanie szczegółowych informacji o brakujących danych
        st.markdown("**Szczegółowe informacje o lokalizacji braków:**")
        
        # Znajdź wszystkie komórki z brakującymi danymi
        missing_details = []
        
        for col in missing_cols.index:
            missing_mask = df[col].isnull()
            missing_indices = df[missing_mask].index.tolist()
            
            # Ogranicz wyświetlanie do pierwszych 20 indeksów
            indices_display = missing_indices[:20]
            if len(missing_indices) > 20:
                indices_str = f"{indices_display} ... (i {len(missing_indices) - 20} więcej)"
            else:
                indices_str = str(missing_indices)
            
            missing_details.append({
                'Kolumna': col,
                'Typ kolumny': str(df[col].dtype),
                'Liczba braków': len(missing_indices),
                'Indeksy z brakami': indices_str,
                'Procent': f"{(len(missing_indices) / len(df) * 100):.2f}%"
            })
        
        if missing_details:
            # Tabela z szczegółami braków
            details_df = pd.DataFrame(missing_details)
            st.dataframe(details_df, use_container_width=True, hide_index=True)
            
            # Znajdź wszystkie wiersze z jakimikolwiek brakami
            rows_with_any_missing = df[df.isnull().any(axis=1)]
            unique_missing_indices = sorted(rows_with_any_missing.index.tolist())
            
            st.markdown(f"**📊 Podsumowanie:**")
            st.write(f"• **Łączna liczba wierszy z brakami:** {len(unique_missing_indices)}")
            st.write(f"• **Procent wierszy z brakami:** {(len(unique_missing_indices) / len(df) * 100):.2f}%")
            st.write(f"• **Indeksy wierszy z brakami:** {unique_missing_indices}")
            
            # Pokaż próbkę wierszy z brakami
            if len(unique_missing_indices) > 0:
                st.markdown("**📋 Próbka wierszy z brakującymi danymi:**")
                sample_size = min(10, len(unique_missing_indices))
                sample_missing = rows_with_any_missing.head(sample_size)
                
                # Dodaj kolumnę z oryginalnym indeksem
                sample_display = sample_missing.copy()
                sample_display.insert(0, 'Original_Index', sample_display.index)
                
                st.dataframe(sample_display, use_container_width=True, height=300)
                
                # Prosta mapa braków
                st.markdown("**🗺️ Mapa brakujących danych (próbka):**")
                st.caption("✅ = dane dostępne, ❌ = brak danych")
                
                # Konwertuj na mapę braków
                missing_map = sample_missing.isnull()
                display_map = missing_map.copy()
                
                for col in display_map.columns:
                    display_map[col] = display_map[col].map({True: '❌', False: '✅'})
                
                display_map.insert(0, 'Index', sample_missing.index)
                st.dataframe(display_map, use_container_width=True, height=250)
        
        # Strategia obsługi braków
        st.markdown("---")
        st.markdown("**🛠️ Wybierz strategię obsługi braków:**")
        
        strategy = st.radio(
            "Strategia:",
            ["Usuń wiersze z brakami", "Usuń kolumny z brakami", "Wypełnij braki"],
            key="missing_strategy"
        )
        
        if strategy == "Usuń wiersze z brakami":
            st.warning(f"⚠️ Ta operacja usunie {len(unique_missing_indices)} wierszy")
            if st.button("🗑️ Usuń wiersze z brakami", key="remove_rows_missing"):
                original_len = len(df)
                df = df.dropna()
                removed = original_len - len(df)
                st.success(f"✅ Usunięto {removed} wierszy z brakującymi danymi")
        
        elif strategy == "Usuń kolumny z brakami":
            cols_to_remove = st.multiselect(
                "Wybierz kolumny do usunięcia:",
                missing_cols.index.tolist(),
                key="cols_to_remove_missing"
            )
            if cols_to_remove:
                st.warning(f"⚠️ Ta operacja usunie kolumny: {cols_to_remove}")
                if st.button("🗑️ Usuń wybrane kolumny", key="remove_cols_missing"):
                    df = df.drop(columns=cols_to_remove)
                    st.success(f"✅ Usunięto {len(cols_to_remove)} kolumn")
        
        else:  # Wypełnij braki
            col1, col2 = st.columns(2)
            
            with col1:
                fill_column = st.selectbox(
                    "Wybierz kolumnę do wypełnienia:",
                    missing_cols.index.tolist(),
                    key="fill_column"
                )
            
            with col2:
                if fill_column in get_numeric_columns(df):
                    fill_method = st.selectbox(
                        "Metoda wypełniania (kolumna numeryczna):",
                        ["Średnia", "Mediana", "Wartość własna"],
                        key="fill_method"
                    )
                else:
                    fill_method = st.selectbox(
                        "Metoda wypełniania (kolumna tekstowa):",
                        ["Moda", "Wartość własna"],
                        key="fill_method_cat"
                    )
            
            if fill_method == "Wartość własna":
                custom_value = st.text_input("Podaj wartość do wypełnienia:", key="custom_fill_value")
            
            if st.button("🔧 Wypełnij braki", key="fill_missing"):
                missing_count = df[fill_column].isnull().sum()
                
                if fill_method == "Średnia":
                    fill_value = df[fill_column].mean()
                elif fill_method == "Mediana":
                    fill_value = df[fill_column].median()
                elif fill_method == "Moda":
                    mode_values = df[fill_column].mode()
                    fill_value = mode_values.iloc[0] if len(mode_values) > 0 else "Unknown"
                else:  # Wartość własna
                    fill_value = custom_value
                
                if fill_value is not None:
                    df[fill_column] = df[fill_column].fillna(fill_value)
                    st.success(f"✅ Wypełniono {missing_count} braków w kolumnie '{fill_column}' wartością: {fill_value}")
                else:
                    st.error("❌ Nie można wypełnić braków - brak odpowiedniej wartości")
        
        return df
    
    def _handle_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Obsługuje duplikaty"""
        st.subheader("Usuwanie duplikatów")
        
        # Informacje o duplikatach
        duplicates_count = df.duplicated().sum()
        st.info(f"Znaleziono {duplicates_count} zduplikowanych wierszy")
        
        if duplicates_count > 0:
            # Opcje usuwania duplikatów
            subset_cols = st.multiselect(
                "Wybierz kolumny do sprawdzania duplikatów (puste = wszystkie):",
                df.columns.tolist(),
                key="duplicate_subset"
            )
            
            keep_option = st.selectbox(
                "Które duplikaty zachować:",
                ["first", "last", "false"],
                format_func=lambda x: {"first": "Pierwszy", "last": "Ostatni", "false": "Usuń wszystkie"}[x],
                key="keep_duplicates"
            )
            
            if st.button("Usuń duplikaty", key="remove_duplicates"):
                original_len = len(df)
                subset = subset_cols if subset_cols else None
                keep = keep_option if keep_option != "false" else False
                
                df = df.drop_duplicates(subset=subset, keep=keep)
                removed = original_len - len(df)
                st.success(f"Usunięto {removed} duplikatów")
        
        return df
    
    def _handle_encoding(self, df: pd.DataFrame) -> pd.DataFrame:
        """Obsługuje kodowanie kolumn symbolicznych"""
        st.subheader("Kodowanie kolumn symbolicznych")
        
        categorical_cols = get_categorical_columns(df)
        
        if not categorical_cols:
            st.info("Brak kolumn kategorycznych do kodowania.")
            return df
        
        col1, col2 = st.columns(2)
        
        with col1:
            encoding_method = st.selectbox(
                "Wybierz metodę kodowania:",
                ["One-Hot Encoding", "Binary Encoding", "Label Encoding"],
                key="encoding_method"
            )
        
        with col2:
            cols_to_encode = st.multiselect(
                "Wybierz kolumny do kodowania:",
                categorical_cols,
                key="cols_to_encode"
            )
        
        if cols_to_encode and st.button("Zastosuj kodowanie", key="apply_encoding"):
            if encoding_method == "One-Hot Encoding":
                df = self._apply_one_hot_encoding(df, cols_to_encode)
            elif encoding_method == "Binary Encoding":
                df = self._apply_binary_encoding(df, cols_to_encode)
            else:  # Label Encoding
                df = self._apply_label_encoding(df, cols_to_encode)
            
            st.success(f"Zastosowano {encoding_method} dla {len(cols_to_encode)} kolumn")
        
        return df
    
    def _apply_one_hot_encoding(self, df: pd.DataFrame, columns: list) -> pd.DataFrame:
        """Stosuje One-Hot Encoding"""
        for col in columns:
            dummies = pd.get_dummies(df[col], prefix=col)
            df = pd.concat([df, dummies], axis=1)
            df = df.drop(columns=[col])
        return df
    
    def _apply_binary_encoding(self, df: pd.DataFrame, columns: list) -> pd.DataFrame:
        """Stosuje Binary Encoding (uproszczona wersja)"""
        for col in columns:
            # Konwertuj na liczby
            le = LabelEncoder()
            encoded = le.fit_transform(df[col])
            
            # Konwertuj na binarny
            max_val = max(encoded)
            n_bits = len(bin(max_val)[2:])
            
            for i in range(n_bits):
                df[f"{col}_bit_{i}"] = [(x >> i) & 1 for x in encoded]
            
            df = df.drop(columns=[col])
        return df
    
    def _apply_label_encoding(self, df: pd.DataFrame, columns: list) -> pd.DataFrame:
        """Stosuje Label Encoding"""
        for col in columns:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col])
        return df
    
    def _show_comparison(self, original_df: pd.DataFrame, processed_df: pd.DataFrame):
        """Pokazuje porównanie przed i po przetworzeniu"""
        st.subheader("📊 Porównanie przed/po")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            delta_rows = safe_metric_delta(len(processed_df) - len(original_df))
            st.metric(
                "Wiersze",
                len(processed_df),
                delta=delta_rows
            )
        
        with col2:
            delta_cols = safe_metric_delta(len(processed_df.columns) - len(original_df.columns))
            st.metric(
                "Kolumny",
                len(processed_df.columns),
                delta=delta_cols
            )
        
        with col3:
            processed_missing = processed_df.isnull().sum().sum()
            original_missing = original_df.isnull().sum().sum()
            delta_missing = safe_metric_delta(processed_missing - original_missing)
            st.metric(
                "Brakujące wartości",
                processed_missing,
                delta=delta_missing
            )
        
        with col4:
            processed_duplicates = processed_df.duplicated().sum()
            original_duplicates = original_df.duplicated().sum()
            delta_duplicates = safe_metric_delta(processed_duplicates - original_duplicates)
            st.metric(
                "Duplikaty",
                processed_duplicates,
                delta=delta_duplicates
            )
        
        # Podgląd przetworzonej tabeli
        if not processed_df.equals(original_df):
            st.markdown("**Przetworzone dane:**")
            st.dataframe(processed_df.head(10), use_container_width=True)