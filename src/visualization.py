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
            'Wykres słupkowy': {
                'function': self._create_bar_chart,
                'help': 'Pokazuje rozkład kategorii lub porównuje wartości między grupami. Idealny do porównywania liczebności lub średnich wartości.'
            },
            'Wykres punktowy': {
                'function': self._create_scatter_plot,
                'help': 'Pokazuje związek między dwiema zmiennymi numerycznymi. Pomocny w identyfikacji korelacji, trendów i outlierów.'
            },
            'Wykres kołowy': {
                'function': self._create_pie_chart,
                'help': 'Pokazuje proporcje części względem całości. Najlepszy dla maksymalnie 5-7 kategorii z wyraźnymi różnicami.'
            },
            'Histogram': {
                'function': self._create_histogram,
                'help': 'Pokazuje rozkład wartości zmiennej numerycznej. Pozwala ocenić normalność, skośność i obecność wartości odstających.'
            },
            'Wykres pudełkowy': {
                'function': self._create_box_plot,
                'help': 'Pokazuje medianę, kwartyle i outliers. Idealny do porównywania rozkładów między grupami i identyfikacji wartości odstających.'
            },
            'Wykres skrzypcowy': {
                'function': self._create_violin_plot,
                'help': 'Łączy box plot z wykresem gęstości. Pokazuje pełny kształt rozkładu danych oraz outliers.'
            }
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
            # Wybór typu wykresu z pomocą
            chart_type = st.selectbox(
                "Wybierz typ wykresu:",
                list(self.chart_types.keys()),
                key="chart_type",
                help="Wybierz typ wykresu odpowiedni dla Twoich danych"
            )
            
            # Wyświetl pomoc dla wybranego wykresu
            if chart_type:
                st.info(f"💡 **{chart_type}**: {self.chart_types[chart_type]['help']}")
        
        with col2:
            # Dynamiczne opcje w zależności od typu wykresu
            chart_options = self._get_chart_options(chart_type, df, numeric_cols, categorical_cols)
        
        st.markdown("---")
        
        if chart_options:
            # Tworzenie wykresu
            try:
                fig = self.chart_types[chart_type]['function'](df, chart_options)
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
                st.warning("⚠️ Wykres słupkowy wymaga kolumn kategorycznych.")
                st.info("💡 Spróbuj przekonwertować niektóre kolumny na kategoryczne w zakładce Przetwarzanie.")
                return None
            
            # Domyślnie wybierz pierwszą kolumnę kategoryczną
            default_x_index = 0
            options['x'] = st.selectbox(
                "Oś X (kategoryczna):", 
                categorical_cols, 
                index=default_x_index,
                key="bar_x",
                help="Wybierz kolumnę kategoryczną dla osi X"
            )
            
            if numeric_cols:
                # Domyślnie wybierz pierwszą kolumnę numeryczną
                default_y_index = 0
                options['y'] = st.selectbox(
                    "Oś Y (numeryczna):", 
                    numeric_cols, 
                    index=default_y_index,
                    key="bar_y",
                    help="Wybierz kolumnę numeryczną do agregacji (średnia)"
                )
            else:
                options['y'] = None  # Liczenie wystąpień
                st.info("ℹ️ Brak kolumn numerycznych - zostanie pokazana liczebność kategorii")
            
            if len(categorical_cols) > 1:
                # Filtruj opcje kolorów - usuń już wybraną kolumnę X
                color_options = [None] + [col for col in categorical_cols if col != options['x']]
                options['color'] = st.selectbox(
                    "Kolor (opcjonalne):", 
                    color_options, 
                    index=0,  # Domyślnie None
                    key="bar_color",
                    help="Dodatkowe grupowanie według kolumny kategorycznej"
                )
        
        elif chart_type == 'Wykres punktowy':
            if len(numeric_cols) < 2:
                st.warning("⚠️ Wykres punktowy wymaga co najmniej dwóch kolumn numerycznych.")
                st.info("💡 Upewnij się, że masz dane numeryczne lub przekonwertuj tekst na liczby.")
                return None
            
            # Domyślnie wybierz pierwszą kolumnę dla X
            default_x_index = 0
            options['x'] = st.selectbox(
                "Oś X:", 
                numeric_cols, 
                index=default_x_index,
                key="scatter_x",
                help="Zmienna niezależna (objaśniająca)"
            )
            
            # Domyślnie wybierz drugą kolumnę dla Y (różną od X)
            y_options = [col for col in numeric_cols if col != options['x']]
            default_y_index = 0 if y_options else 0
            options['y'] = st.selectbox(
                "Oś Y:", 
                y_options if y_options else numeric_cols, 
                index=default_y_index,
                key="scatter_y",
                help="Zmienna zależna (objaśniana)"
            )
            
            if len(numeric_cols) > 2:
                # Opcje rozmiaru - wykluczamy już wybrane X i Y
                size_options = [None] + [col for col in numeric_cols if col not in [options['x'], options['y']]]
                default_size_index = 1 if len(size_options) > 1 else 0  # Wybierz pierwszą dostępną
                options['size'] = st.selectbox(
                    "Rozmiar (opcjonalne):", 
                    size_options, 
                    index=default_size_index,
                    key="scatter_size",
                    help="Trzeci wymiar - rozmiar punktów według wartości"
                )
            
            if categorical_cols:
                # Domyślnie wybierz pierwszą kolumnę kategoryczną
                color_options = [None] + categorical_cols
                default_color_index = 1 if len(color_options) > 1 else 0
                options['color'] = st.selectbox(
                    "Kolor (opcjonalne):", 
                    color_options, 
                    index=default_color_index,
                    key="scatter_color",
                    help="Kolorowanie punktów według kategorii"
                )
        
        elif chart_type == 'Wykres kołowy':
            if not categorical_cols:
                st.warning("⚠️ Wykres kołowy wymaga kolumn kategorycznych.")
                st.info("💡 Wybierz kolumnę z kategoriami, której rozkład chcesz pokazać.")
                return None
            
            # TYLKO kategoryczne - filtruj kolumny żeby pokazać tylko kategoryczne
            available_categorical = [col for col in categorical_cols if col in df.columns]
            
            if not available_categorical:
                st.warning("Brak dostępnych kolumn kategorycznych.")
                return None
            
            # Domyślnie wybierz pierwszą dostępną kolumnę kategoryczną
            default_names_index = 0
            options['names'] = st.selectbox(
                "Kategorie:", 
                available_categorical, 
                index=default_names_index,
                key="pie_names",
                help="Kolumna kategoryczna do podziału na segmenty koła"
            )
            
            # Sprawdź liczbę unikalnych wartości
            if options['names']:
                unique_count = df[options['names']].nunique()
                if unique_count > 10:
                    st.warning(f"⚠️ Kolumna ma {unique_count} unikalnych wartości. Wykres może być nieczytelny.")
                    st.info("💡 Rozważ grupowanie rzadkich kategorii przed utworzeniem wykresu.")
        
        elif chart_type == 'Histogram':
            if not numeric_cols:
                st.warning("⚠️ Histogram wymaga kolumn numerycznych.")
                st.info("💡 Histogram pokazuje rozkład wartości liczbowych.")
                return None
            
            # Domyślnie wybierz pierwszą kolumnę numeryczną
            default_x_index = 0
            options['x'] = st.selectbox(
                "Kolumna:", 
                numeric_cols, 
                index=default_x_index,
                key="hist_x",
                help="Zmienna numeryczna do analizy rozkładu"
            )
            options['bins'] = st.slider(
                "Liczba przedziałów:", 
                10, 100, 30, 
                key="hist_bins",
                help="Więcej przedziałów = bardziej szczegółowy rozkład"
            )
            
            if categorical_cols:
                # Domyślnie bez podziału kolorowego
                options['color'] = st.selectbox(
                    "Podział według (opcjonalne):", 
                    [None] + categorical_cols, 
                    index=0,
                    key="hist_color",
                    help="Porównaj rozkłady między grupami"
                )
        
        elif chart_type == 'Wykres pudełkowy':
            if not numeric_cols:
                st.warning("⚠️ Wykres pudełkowy wymaga kolumn numerycznych.")
                st.info("💡 Box plot pokazuje medianę, kwartyle i wartości odstające.")
                return None
            
            # Domyślnie wybierz pierwszą kolumnę numeryczną
            default_y_index = 0
            options['y'] = st.selectbox(
                "Kolumna numeryczna:", 
                numeric_cols, 
                index=default_y_index,
                key="box_y",
                help="Zmienna do analizy rozkładu i outlierów"
            )
            
            if categorical_cols:
                # Domyślnie bez grupowania
                options['x'] = st.selectbox(
                    "Grupowanie według (opcjonalne):", 
                    [None] + categorical_cols, 
                    index=0,
                    key="box_x",
                    help="Porównaj rozkłady między grupami kategorycznymi"
                )
        
        elif chart_type == 'Wykres skrzypcowy':
            if not numeric_cols:
                st.warning("⚠️ Wykres skrzypcowy wymaga kolumn numerycznych.")
                st.info("💡 Violin plot łączy box plot z wykresem gęstości.")
                return None
            
            # Domyślnie wybierz pierwszą kolumnę numeryczną
            default_y_index = 0
            options['y'] = st.selectbox(
                "Kolumna numeryczna:", 
                numeric_cols, 
                index=default_y_index,
                key="violin_y",
                help="Zmienna do analizy kształtu rozkładu"
            )
            
            if categorical_cols:
                # Domyślnie bez grupowania
                options['x'] = st.selectbox(
                    "Grupowanie według (opcjonalne):", 
                    [None] + categorical_cols, 
                    index=0,
                    key="violin_x",
                    help="Porównaj kształty rozkładów między grupami"
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
                           title=f"Wykres słupkowy: Średnia {y_col} według {x_col}")
            else:
                agg_df = df.groupby(x_col)[y_col].mean().reset_index()
                fig = px.bar(agg_df, x=x_col, y=y_col, 
                           title=f"Wykres słupkowy: Średnia {y_col} według {x_col}")
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
        
        # Dodaj linię trendu jeśli brak kategorii kolorowych
        if not color_col:
            fig.add_traces(px.scatter(df, x=x_col, y=y_col, trendline="ols").data[1:])
        
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
        
        # Dodaj linię średniej
        mean_val = df[x_col].mean()
        fig.add_vline(x=mean_val, line_dash="dash", line_color="red", 
                     annotation_text=f"Średnia: {mean_val:.2f}")
        
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
    
    def _create_violin_plot(self, df: pd.DataFrame, options: dict):
        """Tworzy wykres skrzypcowy"""
        y_col = options['y']
        x_col = options.get('x')
        
        fig = px.violin(
            df, 
            x=x_col, 
            y=y_col,
            title=f"Wykres skrzypcowy: {y_col}" + (f" według {x_col}" if x_col else ""),
            height=500,
            box=True  # Dodaj box plot wewnątrz
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
                key="scatter_matrix_cols",
                help="Macierz pokazuje związki między wszystkimi parami zmiennych"
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