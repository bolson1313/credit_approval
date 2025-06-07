import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import pearsonr, spearmanr
from utils import get_numeric_columns, get_categorical_columns, paginate_dataframe, filter_dataframe, safe_mode, format_number

class StatisticsModule:
    def __init__(self):
        self.correlation_methods = {
            'Pearson': self._pearson_correlation,
            'Spearman': self._spearman_correlation
        }
    
    def render(self, df: pd.DataFrame):
        """Renderuje zakładkę statystyk"""
        if df is None or df.empty:
            st.warning("Brak danych do analizy statystycznej.")
            return
            
        st.header("📈 Statystyki Opisowe")
        
        # Filtry
        st.subheader("🔍 Filtry danych")
        filtered_df = filter_dataframe(df)
        
        # Sprawdzenie czy dane zostały przefiltrowane
        if filtered_df is None or filtered_df.empty:
            st.warning("Brak danych po zastosowaniu filtrów.")
            return
        
        # Wyświetlanie informacji o filtracji
        if len(filtered_df) != len(df):
            st.info(f"Wyświetlane dane: {len(filtered_df)} z {len(df)} wierszy (zastosowano filtry)")
        
        # Wyświetlanie przefiltrowanych danych z scrollem
        st.markdown("**Przefiltrowane dane:**")
        st.dataframe(filtered_df, use_container_width=True, height=400)
        
        # Podstawowe informacje o przefiltrowanych danych
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Wiersze (przefiltrowane)", len(filtered_df))
        with col2:
            st.metric("Kolumny", len(filtered_df.columns))
        with col3:
            st.metric("Brakujące wartości", filtered_df.isnull().sum().sum())
        with col4:
            st.metric("Duplikaty", filtered_df.duplicated().sum())
        
        # Statystyki opisowe
        self._render_descriptive_stats(filtered_df)
        
        # Korelacje
        self._render_correlations(filtered_df)
    
    def _render_descriptive_stats(self, df: pd.DataFrame):
        """Renderuje statystyki opisowe"""
        st.subheader("📊 Statystyki opisowe")
        
        # Kolumny numeryczne
        numeric_cols = get_numeric_columns(df)
        categorical_cols = get_categorical_columns(df)
        
        if numeric_cols:
            st.markdown("**Dane numeryczne:**")
            numeric_stats = []
            
            for col in numeric_cols:
                series = df[col].dropna()
                if len(series) > 0:
                    stats = {
                        'Kolumna': col,
                        'Minimum': format_number(series.min()),
                        'Maksimum': format_number(series.max()),
                        'Średnia': format_number(series.mean()),
                        'Mediana': format_number(series.median()),
                        'Odchylenie std': format_number(series.std()),
                        'Moda': format_number(safe_mode(series))
                    }
                    numeric_stats.append(stats)
            
            if numeric_stats:
                st.dataframe(pd.DataFrame(numeric_stats), use_container_width=True)
        
        if categorical_cols:
            st.markdown("**Dane kategoryczne:**")
            categorical_stats = []
            
            for col in categorical_cols:
                series = df[col].dropna()
                if len(series) > 0:
                    value_counts = series.value_counts()
                    stats = {
                        'Kolumna': col,
                        'Unikalne wartości': len(value_counts),
                        'Najczęstsza wartość': str(value_counts.index[0]) if len(value_counts) > 0 else 'N/A',
                        'Liczność najczęstszej': value_counts.iloc[0] if len(value_counts) > 0 else 0,
                        'Moda': str(safe_mode(series)) if safe_mode(series) is not None else 'N/A'
                    }
                    categorical_stats.append(stats)
            
            if categorical_stats:
                st.dataframe(pd.DataFrame(categorical_stats), use_container_width=True)
        
        # Histogram dla wybranej kolumny numerycznej
        if numeric_cols:
            st.markdown("**Rozkład wartości:**")
            selected_col = st.selectbox(
                "Wybierz kolumnę do histogramu:",
                numeric_cols,
                key="hist_column"
            )
            
            if selected_col:
                fig = px.histogram(
                    df, 
                    x=selected_col, 
                    title=f"Rozkład wartości: {selected_col}",
                    nbins=30
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
    
    def _render_correlations(self, df: pd.DataFrame):
        """Renderuje analizę korelacji"""
        st.subheader("🔗 Analiza korelacji")
        
        numeric_cols = get_numeric_columns(df)
        
        if len(numeric_cols) < 2:
            st.warning("Potrzebujesz co najmniej 2 kolumn numerycznych do analizy korelacji.")
            return
        
        # Wybór metody korelacji
        method = st.selectbox(
            "Wybierz metodę korelacji:",
            list(self.correlation_methods.keys()),
            key="correlation_method"
        )
        
        # Wybór kolumn
        selected_cols = st.multiselect(
            "Wybierz kolumny do analizy korelacji:",
            numeric_cols,
            default=numeric_cols[:min(5, len(numeric_cols))],
            key="correlation_columns"
        )
        
        if len(selected_cols) >= 2:
            # Obliczanie korelacji
            correlation_matrix = self.correlation_methods[method](df[selected_cols])
            
            # Wyświetlanie macierzy korelacji
            st.markdown("**Macierz korelacji:**")
            st.dataframe(correlation_matrix.round(4), use_container_width=True)
            
            # Heatmapa korelacji
            fig = px.imshow(
                correlation_matrix,
                text_auto=True,
                aspect="auto",
                title=f"Mapa cieplna korelacji ({method})",
                color_continuous_scale="RdBu",
                range_color=[-1, 1]
            )
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
            
            # Najsilniejsze korelacje
            self._show_strongest_correlations(correlation_matrix)
    
    def _pearson_correlation(self, df: pd.DataFrame) -> pd.DataFrame:
        """Oblicza korelację Pearsona"""
        return df.corr(method='pearson')
    
    def _spearman_correlation(self, df: pd.DataFrame) -> pd.DataFrame:
        """Oblicza korelację Spearmana"""
        return df.corr(method='spearman')
    
    def _show_strongest_correlations(self, corr_matrix: pd.DataFrame):
        """Pokazuje najsilniejsze korelacje"""
        st.markdown("**Najsilniejsze korelacje:**")
        
        # Tworzenie listy korelacji (bez przekątnej)
        correlations = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                col1 = corr_matrix.columns[i]
                col2 = corr_matrix.columns[j]
                corr_value = corr_matrix.iloc[i, j]
                if not pd.isna(corr_value):
                    correlations.append({
                        'Kolumna 1': col1,
                        'Kolumna 2': col2,
                        'Korelacja': corr_value,
                        'Siła': abs(corr_value)
                    })
        
        if correlations:
            # Sortowanie po sile korelacji
            correlations_df = pd.DataFrame(correlations)
            correlations_df = correlations_df.sort_values('Siła', ascending=False)
            
            # Wyświetlanie top 10
            top_correlations = correlations_df.head(10).copy()
            top_correlations['Korelacja'] = top_correlations['Korelacja'].round(4)
            st.dataframe(
                top_correlations[['Kolumna 1', 'Kolumna 2', 'Korelacja']], 
                use_container_width=True,
                hide_index=True
            )
