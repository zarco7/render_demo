import dash
from dash import dcc, html, Input, Output
import plotly.graph_objs as go
import numpy as np
import math

# Inicialización de la aplicación Dash
app = dash.Dash(__name__)

# Layout de la aplicación
app.layout = html.Div([
    dcc.Graph(id='grafico-opciones'),
    html.Label('Delta (%):'),
    dcc.Slider(id='delta-slider', min=0, max=0.1, step=0.01, value=0.0,
               marks={i: '{:.0%}'.format(i) for i in np.arange(0, 0.11, 0.01)}),
    html.Label('Tasa de interés libre de riesgo (r %):'),
    dcc.Slider(id='r-slider', min=0.02, max=0.2, step=0.005, value=0.045,
               marks={i: '{:.0%}'.format(i) for i in np.arange(0.02, 0.21, 0.01)}),
    html.Label('Volatilidad (vol %):'),
    dcc.Slider(id='vol-slider', min=0.1, max=0.5, step=0.05, value=0.25,
               marks={i: '{:.0%}'.format(i) for i in np.arange(0.1, 0.51, 0.05)}),
    html.Label('Días (n):'),
    dcc.Input(id='n-input', type='number', value=1000)
])


# Callback para actualizar el gráfico basado en los valores de los controles deslizantes
@app.callback(
    Output('grafico-opciones', 'figure'),
    [Input('delta-slider', 'value'),
     Input('r-slider', 'value'),
     Input('vol-slider', 'value'),
     Input('n-input', 'value')]
)
def update_graph(delta, r, vol, n):
    # Rango de precios subyacentes para el gráfico
    St_rango = np.arange(5, 30.5, 0.5)
    S = 12.25
    K = 13  # PrecioPactadoK
    t = n / 365

    # Cálculos de los precios de las opciones
    valores_call = []
    valores_put = []
    for St in St_rango:
        # print(St, K, r, delta, vol, t)
        d1 = (np.log(S / K) + (r - delta + (vol ** 2) / 2) * t) / (vol * np.sqrt(t))
        d2 = (np.log(S / K) + (r - delta - (vol ** 2) / 2) * t) / (vol * np.sqrt(t))
        # print(d1, d2)
        nd1 = 0.5 * (1 + math.erf(d1 / math.sqrt(2)))
        nd2 = 0.5 * (1 + math.erf(d2 / math.sqrt(2)))
        nmenosd1 = 0.5 * (1 + math.erf(-d1 / math.sqrt(2)))
        nmenosd2 = 0.5 * (1 + math.erf(-d2 / math.sqrt(2)))

        PrecioCall = -1*(S * math.exp(-delta * t) * nd1 - (K * math.exp(-r * t) * nd2))
        PrecioPut = -1*((K * math.exp(-r * t) * nmenosd2) - (S * math.exp(-delta * t) * nmenosd1))
        # print(PrecioPut)

        # Ajustar PrecioCall y PrecioPut según la comparación entre St y K
        if St < K:
            PrecioCall = PrecioCall
        else:
            PrecioCall = St - (K - PrecioCall)
            # valores_call.append(PrecioCall)
        if St > K:
            PrecioPut = PrecioPut
        else:
            PrecioPut = K - (St - PrecioPut)
            # print(PrecioPut)

        valores_call.append(PrecioCall)
        valores_put.append(PrecioPut)

    # Crear el gráfico con Plotly
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=St_rango, y=valores_call, mode='lines', name='Beneficio Call'))
    fig.add_trace(go.Scatter(x=St_rango, y=valores_put, mode='lines', name='Beneficio Put'))
    fig.update_layout(
        title='Precios de Opciones Call y Put en función del Precio Subyacente',
        xaxis_title='Precio Subyacente S(t)',
        yaxis_title='Precio de la Opción',
        hovermode='x'
    )
    return fig


# Ejecutar la aplicación
if __name__ == '__main__':
    app.run_server(debug=True)
