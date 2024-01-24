import dash
from dash import dcc, html, Input, Output
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import math

# Inicialización de la aplicación Dash
app = dash.Dash(__name__)

# Parámetros iniciales
PrecioSubyacenteS = [5, 6.5, 8, 9.5, 11, 12.5, 14, 15.5, 17, 18.5, 20, 21.5, 23, 24.5, 26, 27.5, 29]
PrecioPactadoK = [5, 6.5, 8, 9.5, 11, 12.5, 14, 15.5, 17, 18.5, 20, 21.5, 23, 24.5, 26, 27.5, 29]

# Layout de la aplicación
app.layout = html.Div([
    dcc.Graph(id='heatmap-nd2'),
    dcc.Graph(id='heatmap-precio'),
    html.Label('Delta:'),
    dcc.Slider(id='delta-slider', min=0, max=0.1, step=0.01, value=0.0, marks={i: '{:.0%}'.format(i) for i in np.arange(0.01, 0.21, 0.01)}),
    html.Label('Tasa de interés libre de riesgo (r):'),
    dcc.Slider(id='r-slider', min=0.02, max=0.2, step=0.005, value=0.045, marks={i: '{:.0%}'.format(i) for i in np.arange(0.02, 0.21, 0.01)}),
    html.Label('Volatilidad (vol):'),
    dcc.Slider(id='vol-slider', min=0.1, max=0.5, step=0.05, value=0.25, marks={i: '{:.0%}'.format(i) for i in np.arange(0.1, 0.51, 0.05)}),
    html.Label('Días (n):'),
    dcc.Input(id='n-input', type='number', value=200)
])


# Callback para actualizar el primer gráfico (N(d2))
@app.callback(
    Output('heatmap-nd2', 'figure'),
    [Input('delta-slider', 'value'),
     Input('r-slider', 'value'),
     Input('vol-slider', 'value'),
     Input('n-input', 'value')]
)
def update_nd2_graph(delta, r, vol, n):
    t = n / 365
    resultados_nd2 = []
    for S in PrecioSubyacenteS:
        for K in PrecioPactadoK:
            d2 = (np.log(S / K) + (r - delta - (vol ** 2) / 2) * t) / (vol * np.sqrt(t))
            nd2 = 0.5 * (1 + math.erf(d2 / math.sqrt(2)))
            resultados_nd2.append({'PrecioSubyacenteS': S, 'PrecioPactadoK': K, 'nd2': nd2})
    df_resultados_nd2 = pd.DataFrame(resultados_nd2)
    df_pivot_nd2 = df_resultados_nd2.pivot(index='PrecioSubyacenteS', columns='PrecioPactadoK', values='nd2')

    return {
        'data': [go.Heatmap(
            z=df_pivot_nd2.values,
            x=df_pivot_nd2.columns,
            y=df_pivot_nd2.index,
            colorscale='Jet',
            text=[['{:.2f}'.format(val) for val in row] for row in df_pivot_nd2.values],  # Formatear los valores
            hoverinfo='none',  # Desactivar el hover
            texttemplate='%{text}'  # Mostrar el texto formateado en cada celda
        )],
        'layout': go.Layout(
            title='Mapa de Calor N(d2) Probabilidad que la Opción CALL expire ITM (In the Money)',
            xaxis={'title': 'Precio Pactado (K)'},
            yaxis={'title': 'Precio Subyacente (S)'}
        )
    }


# Callback para actualizar el segundo gráfico (Precio de la Opción)
@app.callback(
    Output('heatmap-precio', 'figure'),
    [Input('delta-slider', 'value'),
     Input('r-slider', 'value'),
     Input('vol-slider', 'value'),
     Input('n-input', 'value')]
)
def update_precio_graph(delta, r, vol, n):
    t = n / 365
    resultados_precio = []
    for S in PrecioSubyacenteS:
        for K in PrecioPactadoK:
            d1 = (np.log(S / K) + (r - delta + (vol ** 2) / 2) * t) / (vol * np.sqrt(t))
            nd1 = 0.5 * (1 + math.erf(d1 / math.sqrt(2)))
            d2 = (np.log(S / K) + (r - delta - (vol ** 2) / 2) * t) / (vol * np.sqrt(t))
            nd2 = 0.5 * (1 + math.erf(d2 / math.sqrt(2)))
            precio = S * math.exp(-delta * t) * nd1 - (K * math.exp(-r * t) * nd2)
            resultados_precio.append({'PrecioSubyacenteS': S, 'PrecioPactadoK': K, 'precio': precio})
    df_resultados_precio = pd.DataFrame(resultados_precio)
    df_pivot_precio = df_resultados_precio.pivot(index='PrecioSubyacenteS', columns='PrecioPactadoK', values='precio')

    return {
        'data': [go.Heatmap(
            z=df_pivot_precio.values,
            x=df_pivot_precio.columns,
            y=df_pivot_precio.index,
            colorscale='Jet',
            text=[['{:.2f}'.format(val) for val in row] for row in df_pivot_precio.values],  # Formatear los valores
            hoverinfo='none',  # Desactivar el hover
            texttemplate='%{text}'  # Mostrar el texto formateado en cada celda
        )],
        'layout': go.Layout(
            title='Mapa de Calor del Precio de la Opción CALL',
            xaxis={'title': 'Precio Pactado (K)'},
            yaxis={'title': 'Precio Subyacente (S)'}
        )
    }


# Ejecutar la aplicación
if __name__ == '__main__':
    app.run_server(debug=True)
