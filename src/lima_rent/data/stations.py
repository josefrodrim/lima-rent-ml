"""Estaciones de transporte masivo usadas para calcular `dist_to_station_km`.

Coordenadas aproximadas del corredor del Metropolitano (troncal norte-sur) y
de 4 estaciones de la Línea 1 del Metro de Lima. Suficientemente realistas
para que el efecto de cercanía a una estación sea geoespacialmente creíble,
sin pretender ser un dataset oficial de paraderos.
"""

TRANSIT_STATIONS: list[tuple[str, float, float]] = [
    # Metropolitano (troncal norte-sur)
    ("Naranjal", -11.9975, -77.0592),
    ("Izaguirre", -11.9721, -77.0629),
    ("Central", -12.0524, -77.0362),
    ("Estación Central", -12.0498, -77.0330),
    ("Canadá", -12.0779, -77.0136),
    ("Javier Prado", -12.0890, -77.0059),
    ("Canaval y Moreyra", -12.0958, -77.0107),
    ("Angamos", -12.1097, -77.0106),
    ("Ricardo Palma", -12.1177, -77.0138),
    ("Benavides", -12.1257, -77.0148),
    ("Bulevar", -12.1339, -77.0157),
    ("Estadio Unión", -12.1420, -77.0157),
    ("Escuela Militar", -12.1512, -77.0165),
    ("Terán", -12.1620, -77.0170),
    ("Matellini", -12.1780, -77.0175),
    # Línea 1 del Metro
    ("Villa El Salvador", -12.2222, -76.9403),
    ("Gamarra", -12.0661, -77.0142),
    ("Grau", -12.0587, -77.0245),
    ("Bayóvar", -11.9975, -76.9975),
]
