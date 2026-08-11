"""Visualizaciones del taller: notebook (EDA, TODOs) y mapa de calor geoespacial.

Todo gráfico usa la paleta de `config.py` para que notebook, API y frontend se
vean como un solo producto, no un collage de defaults de cada librería.
"""

import folium
import pandas as pd
import plotly.graph_objects as go
from folium.plugins import HeatMap

from lima_rent.config import COLOR_BLUE, COLOR_MAGENTA, COLOR_NAVY
from lima_rent.data.stations import TRANSIT_STATIONS


def plot_price_per_m2_by_district(df: pd.DataFrame) -> go.Figure:
    """Boxplot de precio/m² por distrito, ordenado por mediana descendente."""
    order = df.groupby("district")["price_per_m2"].median().sort_values(ascending=False).index.tolist()

    fig = go.Figure()
    for district in order:
        fig.add_trace(
            go.Box(
                y=df.loc[df["district"] == district, "price_per_m2"],
                name=district,
                marker_color=COLOR_BLUE,
                showlegend=False,
            )
        )
    fig.update_layout(
        title="Precio por m² según distrito (ordenado por mediana)",
        xaxis_title="Distrito",
        yaxis_title="S/ por m²",
        xaxis_tickangle=-45,
        template="plotly_white",
    )
    return fig


def plot_distance_vs_price(df: pd.DataFrame, n_bins: int = 20) -> go.Figure:
    """Scatter de precio/m² vs. distancia a estación, con línea de tendencia por bins."""
    df_binned = df.copy()
    df_binned["dist_bin"] = pd.cut(df_binned["dist_to_station_km"], bins=n_bins)
    trend = (
        df_binned.groupby("dist_bin", observed=True)
        .agg(dist_mid=("dist_to_station_km", "mean"), price_mean=("price_per_m2", "mean"))
        .dropna()
    )

    fig = go.Figure()
    fig.add_trace(
        go.Scattergl(
            x=df["dist_to_station_km"],
            y=df["price_per_m2"],
            mode="markers",
            marker=dict(color=COLOR_NAVY, opacity=0.25, size=5),
            name="Avisos",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=trend["dist_mid"],
            y=trend["price_mean"],
            mode="lines",
            line=dict(color=COLOR_MAGENTA, width=3),
            name="Tendencia (promedio por bin)",
        )
    )
    fig.update_layout(
        title="Precio por m² vs. distancia a la estación más cercana",
        xaxis_title="Distancia a estación (km)",
        yaxis_title="S/ por m²",
        template="plotly_white",
    )
    return fig


def build_price_heatmap(df: pd.DataFrame) -> folium.Map:
    """Mapa de calor de precio/m² por ubicación, con las estaciones de transporte marcadas."""
    center = [df["latitude"].mean(), df["longitude"].mean()]
    m = folium.Map(location=center, zoom_start=11, tiles="cartodbpositron")

    heat_data = df[["latitude", "longitude", "price_per_m2"]].values.tolist()
    HeatMap(heat_data, radius=12, blur=18, max_zoom=13).add_to(m)

    for name, lat, lon in TRANSIT_STATIONS:
        folium.CircleMarker(
            location=[lat, lon],
            radius=3,
            color=COLOR_MAGENTA,
            fill=True,
            fill_opacity=0.9,
            tooltip=name,
        ).add_to(m)

    return m
