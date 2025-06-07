import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils import get_numeric_columns, get_categorical_columns

class VisualizationModule:
    def __init__(self):
        self.chart_types = {
            'Wykres słupkowy': self._create_bar_chart,
            'Wykres liniowy': self._create_line_chart,
            'Wykres punktowy': self._create_scatter_plot,
            'Wykres kołowy': self._create_pie_chart,
            'Histogram': self._create_histogram,
            'Wykres pudełkowy': self._create_box_plot,
            'Mapa cieplna': self._create_heatmap,
            'Wykres skrzypcowy': self._create_violin_plot
        }
    
    def render(self, df: pd.DataFrame):
        """Renderuje zakładkę wizualizacji"""
        if df is None or df.empty:
            st.warning("Brak danych do wizualizacji.")
            return
            
        st.header("📊 Wizualizacje")
        
        # Podstawowe informacje o danych
        numeric_cols = get_numeric_columns(df)
        categorical_cols = get_categorical_columns(df)
        
        # Ustawienia wykresów w zakładce zamiast w sidebarze
        st.subheader("🎨 Ustawienia wykresów")
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            # Wybór typu wykresu
            chart_type = st.selectbox(
                "Wybierz typ wykresu:",
                list(self.chart_types.keys()),
                key="chart_type"
            )
        
        with col2:
            # Dynamiczne opcje w zależności od typu wykresu
            chart_options = self._get_chart_options(chart_type, df, numeric_cols, categorical_cols)
        
        st.markdown("---")
        
        if chart_options:
            # Tworzenie wykresu
            try:
                fig = self.chart_types[chart_type](df, chart_options)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Opcje eksportu
                    self._show_export_options(fig)
            except Exception as e:
                st.error(f"Błąd podczas tworzenia wykresu: {str(e)}")
        
        # Sekcja porównawczych wykresów
        self._render_comparison_charts(df, numeric_cols, categorical_cols)
        
        # Sekcja macierzy wykresów
        if len(numeric_cols) >= 2:
            self._render_scatter_matrix(df, numeric_cols)
    
    def _get_chart_options(self, chart_type: str, df: pd.DataFrame, 
                          numeric_cols: list, categorical_cols: list) -> dict:
        """Zwraca opcje dla wybranego typu wykresu"""
        options = {}
        
        if chart_type == 'Wykres słupkowy':
            if not categorical_cols:
                st.warning("Wykres słupkowy wymaga kolumn kategorycznych.")
                return None
            
            options['x'] = st.selectbox("Oś X (kategoryczna):", categorical_cols, key="bar_x")
            if numeric_cols:
                options['y'] = st.selectbox("Oś Y (numeryczna):", numeric_cols, key="bar_y")
            else:
                options['y'] = None  # Liczenie wystąpień
            
            if len(categorical_cols) > 1:
                options['color'] = st.selectbox(
                    "Kolor (opcjonalne):", 
                    [None] + categorical_cols, 
                    key="bar_color"
                )
        
        elif chart_type == 'Wykres liniowy':
            if len(numeric_cols) < 1:
                st.warning("Wykres liniowy wymaga co najmniej jednej kolumny numerycznej.")
                return None
            
            # Jeśli mamy kolumny daty/indeks, użyj ich jako X
            date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
            x_options = date_cols + numeric_cols + list(range(len(df)))
            
            if date_cols:
                options['x'] = st.selectbox("Oś X:", date_cols + ["Indeks"], key="line_x")
            else:
                options['x'] = st.selectbox("Oś X:", ["Indeks"] + numeric_cols, key="line_x")
            
            options['y'] = st.multiselect(
                "Oś Y (numeryczne):", 
                numeric_cols, 
                default=[numeric_cols[0]] if numeric_cols else [],
                key="line_y"
            )
        
        elif chart_type == 'Wykres punktowy':
            if len(numeric_cols) < 2:
                st.warning("Wykres punktowy wymaga co najmniej dwóch kolumn numerycznych.")
                return None
            
            options['x'] = st.selectbox("Oś X:", numeric_cols, key="scatter_x")
            options['y'] = st.selectbox("Oś Y:", numeric_cols, key="scatter_y")
            
            if len(numeric_cols) > 2:
                options['size'] = st.selectbox(
                    "Rozmiar (opcjonalne):", 
                    [None] + numeric_cols, 
                    key="scatter_size"
                )
            
            if categorical_cols:
                options['color'] = st.selectbox(
                    "Kolor (opcjonalne):", 
                    [None] + categorical_cols, 
                    key="scatter_color"
                )
        
        elif chart_type == 'Wykres kołowy':
            if not categorical_cols:
                st.warning("Wykres kołowy wymaga kolumn kategorycznych.")
                return None
            
            # TYLKO kategoryczne - filtruj kolumny żeby pokazać tylko kategoryczne
            available_categorical = [col for col in categorical_cols if col in df.columns]
            
            if not available_categorical:
                st.warning("Brak dostępnych kolumn kategorycznych.")
                return None
            
            options['names'] = st.selectbox(
                "Kategorie:", 
                available_categorical, 
                key="pie_names",
                help="Dostępne tylko kolumny kategoryczne (tekstowe)"
            )
        
        elif chart_type == 'Histogram':
            if not numeric_cols:
                st.warning("Histogram wymaga kolumn numerycznych.")
                return None
            
            options['x'] = st.selectbox("Kolumna:", numeric_cols, key="hist_x")
            options['bins'] = st.slider("Liczba przedziałów:", 10, 100, 30, key="hist_bins")
            
            if categorical_cols:
                options['color'] = st.selectbox(
                    "Podział według (opcjonalne):", 
                    [None] + categorical_cols, 
                    key="hist_color"
                )
        
        elif chart_type == 'Wykres pudełkowy':
            if not numeric_cols:
                st.warning("Wykres pudełkowy wymaga kolumn numerycznych.")
                return None
            
            options['y'] = st.selectbox("Kolumna numeryczna:", numeric_cols, key="box_y")
            
            if categorical_cols:
                options['x'] = st.selectbox(
                    "Grupowanie według (opcjonalne):", 
                    [None] + categorical_cols, 
                    key="box_x"
                )
        
        elif chart_type == 'Mapa cieplna':
            if len(numeric_cols) < 2:
                st.warning("Mapa cieplna wymaga co najmniej dwóch kolumn numerycznych.")
                return None
            
            options['columns'] = st.multiselect(
                "Wybierz kolumny:", 
                numeric_cols,
                default=numeric_cols[:min(10, len(numeric_cols))],
                key="heatmap_cols"
            )
        
        elif chart_type == 'Wykres skrzypcowy':
            if not numeric_cols:
                st.warning("Wykres skrzypcowy wymaga kolumn numerycznych.")
                return None
            
            options['y'] = st.selectbox("Kolumna numeryczna:", numeric_cols, key="violin_y")
            
            if categorical_cols:
                options['x'] = st.selectbox(
                    "Grupowanie według (opcjonalne):", 
                    [None] + categorical_cols, 
                    key="violin_x"
                )
        
        return options
    
    def _create_bar_chart(self, df: pd.DataFrame, options: dict):
        """Tworzy wykres słupkowy"""
        x_col = options['x']
        y_col = options.get('y')
        color_col = options.get('color')
        
        if y_col:
            # Agregacja danych
            if color_col:
                agg_df = df.groupby([x_col, color_col])[y_col].mean().reset_index()
                fig = px.bar(agg_df, x=x_col, y=y_col, color=color_col, 
                           title=f"Wykres słupkowy: {y_col} według {x_col}")
            else:
                agg_df = df.groupby(x_col)[y_col].mean().reset_index()
                fig = px.bar(agg_df, x=x_col, y=y_col, 
                           title=f"Wykres słupkowy: {y_col} według {x_col}")
        else:
            # Liczenie wystąpień
            if color_col:
                fig = px.histogram(df, x=x_col, color=color_col, 
                                 title=f"Liczność wystąpień: {x_col}")
            else:
                fig = px.histogram(df, x=x_col, 
                                 title=f"Liczność wystąpień: {x_col}")
        
        fig.update_layout(height=500)
        return fig
    
    def _create_line_chart(self, df: pd.DataFrame, options: dict):
        """Tworzy wykres liniowy"""
        x_col = options['x']
        y_cols = options['y']
        
        if not y_cols:
            return None
        
        if x_col == "Indeks":
            x_data = df.index
            x_title = "Indeks"
        else:
            x_data = df[x_col]
            x_title = x_col
        
        fig = go.Figure()
        
        for y_col in y_cols:
            fig.add_trace(go.Scatter(
                x=x_data,
                y=df[y_col],
                mode='lines+markers',
                name=y_col
            ))
        
        fig.update_layout(
            title=f"Wykres liniowy: {', '.join(y_cols)} w czasie",
            xaxis_title=x_title,
            yaxis_title="Wartość",
            height=500
        )
        
        return fig
    
    def _create_scatter_plot(self, df: pd.DataFrame, options: dict):
        """Tworzy wykres punktowy"""
        x_col = options['x']
        y_col = options['y']
        size_col = options.get('size')
        color_col = options.get('color')
        
        fig = px.scatter(
            df, 
            x=x_col, 
            y=y_col,
            size=size_col,
            color=color_col,
            title=f"Wykres punktowy: {y_col} vs {x_col}",
            height=500
        )
        
        return fig
    
    def _create_pie_chart(self, df: pd.DataFrame, options: dict):
        """Tworzy wykres kołowy"""
        names_col = options['names']
        
        # Tylko liczenie wystąpień - bez opcji wartości numerycznych
        value_counts = df[names_col].value_counts().reset_index()
        value_counts.columns = [names_col, 'count']
        
        fig = px.pie(
            value_counts, 
            names=names_col, 
            values='count',
            title=f"Rozkład wartości: {names_col}"
        )
        
        fig.update_layout(height=500)
        return fig
    
    def _create_histogram(self, df: pd.DataFrame, options: dict):
        """Tworzy histogram"""
        x_col = options['x']
        bins = options['bins']
        color_col = options.get('color')
        
        fig = px.histogram(
            df, 
            x=x_col, 
            nbins=bins,
            color=color_col,
            title=f"Histogram: {x_col}",
            height=500
        )
        
        return fig
    
    def _create_box_plot(self, df: pd.DataFrame, options: dict):
        """Tworzy wykres pudełkowy"""
        y_col = options['y']
        x_col = options.get('x')
        
        fig = px.box(
            df, 
            x=x_col, 
            y=y_col,
            title=f"Wykres pudełkowy: {y_col}" + (f" według {x_col}" if x_col else ""),
            height=500
        )
        
        return fig
    
    def _create_heatmap(self, df: pd.DataFrame, options: dict):
        """Tworzy mapę cieplną"""
        columns = options['columns']
        
        if len(columns) < 2:
            return None
        
        corr_matrix = df[columns].corr()
        
        fig = px.imshow(
            corr_matrix,
            text_auto=True,
            aspect="auto",
            title="Mapa cieplna korelacji",
            color_continuous_scale="RdBu",
            range_color=[-1, 1],
            height=500
        )
        
        return fig
    
    def _create_violin_plot(self, df: pd.DataFrame, options: dict):
        """Tworzy wykres skrzypcowy"""
        y_col = options['y']
        x_col = options.get('x')
        
        fig = px.violin(
            df, 
            x=x_col, 
            y=y_col,
            title=f"Wykres skrzypcowy: {y_col}" + (f" według {x_col}" if x_col else ""),
            height=500
        )
        
        return fig
    
    def _render_comparison_charts(self, df: pd.DataFrame, numeric_cols: list, categorical_cols: list):
        """Renderuje sekcję wykresów porównawczych"""
        st.subheader("📈 Wykresy porównawcze")
        
        if len(numeric_cols) >= 2:
            with st.expander("Porównanie zmiennych numerycznych", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    var1 = st.selectbox("Zmienna 1:", numeric_cols, key="comp_var1")
                with col2:
                    var2 = st.selectbox("Zmienna 2:", numeric_cols, key="comp_var2")
                
                if var1 != var2:
                    # Wykres porównawczy
                    fig = make_subplots(
                        rows=2, cols=2,
                        subplot_titles=(f'Rozkład {var1}', f'Rozkład {var2}', 
                                      f'Scatter plot', f'Box plot porównawczy'),
                        specs=[[{"secondary_y": False}, {"secondary_y": False}],
                               [{"secondary_y": False}, {"secondary_y": False}]]
                    )
                    
                    # Histogramy
                    fig.add_trace(go.Histogram(x=df[var1], name=var1, nbinsx=30), row=1, col=1)
                    fig.add_trace(go.Histogram(x=df[var2], name=var2, nbinsx=30), row=1, col=2)
                    
                    # Scatter plot
                    fig.add_trace(go.Scatter(x=df[var1], y=df[var2], mode='markers', 
                                           name=f'{var1} vs {var2}'), row=2, col=1)
                    
                    # Box plots
                    fig.add_trace(go.Box(y=df[var1], name=var1), row=2, col=2)
                    fig.add_trace(go.Box(y=df[var2], name=var2), row=2, col=2)
                    
                    fig.update_layout(height=600, showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
    
    def _render_scatter_matrix(self, df: pd.DataFrame, numeric_cols: list):
        """Renderuje macierz wykresów punktowych"""
        st.subheader("🎯 Macierz wykresów punktowych")
        
        with st.expander("Scatter Matrix", expanded=False):
            selected_cols = st.multiselect(
                "Wybierz kolumny (max 5):",
                numeric_cols,
                default=numeric_cols[:min(4, len(numeric_cols))],
                key="scatter_matrix_cols"
            )
            
            if len(selected_cols) >= 2:
                if len(selected_cols) > 5:
                    st.warning("Wybrano za dużo kolumn. Zostanie użytych pierwszych 5.")
                    selected_cols = selected_cols[:5]
                
                fig = px.scatter_matrix(
                    df[selected_cols],
                    title="Macierz wykresów punktowych",
                    height=600
                )
                fig.update_traces(diagonal_visible=False)
                st.plotly_chart(fig, use_container_width=True)
    
    def _show_export_options(self, fig):
        """Pokazuje opcje eksportu wykresu"""
        st.subheader("💾 Opcje eksportu")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📄 Pobierz jako HTML", key="download_html"):
                st.download_button(
                    label="💾 Zapisz HTML",
                    data=fig.to_html(),
                    file_name="wykres.html",
                    mime="text/html"
                )
        
        with col2:
            st.info("💡 Użyj opcji w prawym górnym rogu wykresu aby pobrać jako PNG/SVG")
