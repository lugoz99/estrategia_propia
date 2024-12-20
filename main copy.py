import threading
import time
import numpy as np
import random
import math
import os
import sys
from dash import Dash, html, dcc, Input, Output, State, no_update
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
from dash.exceptions import PreventUpdate
from Estrategia3 import Estrategia3
from ProbabilidadEp import ProbabilidadEP

# Crear una instancia de la aplicación Dash con el tema de Bootstrap
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Proyecto Final: Análisis y Diseño de Algoritmos"


# Función para generar grafos bipartitos
def generar_grafos_bipartitos_correctos(particion):
    grafo1, grafo2 = particion

    # Primer grafo: conexiones entre grafo1 presente y futuro
    nodes_grafo1 = [
        {"data": {"id": nodo, "label": nodo}, "classes": "futuro"} for nodo in grafo1[0]
    ]
    nodes_grafo1 += [
        {"data": {"id": nodo, "label": nodo}, "classes": "presente"}
        for nodo in grafo1[1]
    ]
    edges_grafo1 = [
        {"data": {"source": presente, "target": futuro}, "classes": "highlight"}
        for presente in grafo1[1]
        for futuro in grafo1[0]
    ]

    # Segundo grafo: conexiones entre grafo2 presente y futuro
    nodes_grafo2 = [
        {"data": {"id": nodo, "label": nodo}, "classes": "futuro"} for nodo in grafo2[0]
    ]
    nodes_grafo2 += [
        {"data": {"id": nodo, "label": nodo}, "classes": "presente"}
        for nodo in grafo2[1]
    ]
    edges_grafo2 = [
        {"data": {"source": presente, "target": futuro}, "classes": "highlight-alt"}
        for presente in grafo2[1]
        for futuro in grafo2[0]
    ]

    return (nodes_grafo1, edges_grafo1), (nodes_grafo2, edges_grafo2)


# Layout de la aplicación
app.layout = dbc.Container(
    [
        dbc.Navbar(
            dbc.Container(
                [
                    dbc.NavbarBrand(
                        "Proyecto Final: Análisis y Diseño de Algoritmos 2024-2",
                        className="ms-2",
                    ),
                ]
            ),
            color="primary",
            dark=True,
        ),
        dbc.Card(
            [
                dbc.CardBody(
                    [
                        html.Div(
                            [
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            html.Label("Seleccione una matriz:"),
                                            width=3,
                                        ),
                                        dbc.Col(
                                            dcc.Dropdown(
                                                id="matriz-dropdown",
                                                options=[],
                                                placeholder="Cargando matrices...",
                                                className="mb-2",
                                            ),
                                            width=9,
                                        ),
                                    ]
                                ),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            html.Label("Estado actual (Ejemplo: 0,1):"),
                                            width=3,
                                        ),
                                        dbc.Col(
                                            dcc.Input(
                                                id="estado-actual",
                                                type="text",
                                                placeholder="0,1",
                                                className="mb-2",
                                            ),
                                            width=9,
                                        ),
                                    ]
                                ),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            html.Label(
                                                "Factor de enfriamiento (Ejemplo: 0.85):"
                                            ),
                                            width=3,
                                        ),
                                        dbc.Col(
                                            dcc.Input(
                                                id="factor-enfriamiento",
                                                type="number",
                                                placeholder="0.85",
                                                className="mb-2",
                                            ),
                                            width=9,
                                        ),
                                    ]
                                ),
                            ],
                            className="mb-3",
                        ),
                        dbc.Button(
                            "Ejecutar Algoritmo",
                            id="ejecutar-btn",
                            color="primary",
                            className="w-100",
                        ),
                    ]
                )
            ],
            className="my-4",
        ),
        dbc.Alert(
            id="resultado",
            color="info",
            is_open=False,
            dismissable=True,
            className="my-4",
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H3("Primer Grafo Bipartito", className="text-center mb-3"),
                        cyto.Cytoscape(
                            id="grafo1",
                            layout={"name": "circle", "nodeSpacing": 50},
                            style={
                                "width": "100%",
                                "height": "500px",
                                "backgroundColor": "#f8f9fa",
                            },
                            stylesheet=[
                                {
                                    "selector": ".presente",
                                    "style": {
                                        "background-color": "#0074D9",
                                        "label": "data(label)",
                                    },
                                },
                                {
                                    "selector": ".futuro",
                                    "style": {
                                        "background-color": "#2ECC40",
                                        "label": "data(label)",
                                    },
                                },
                                {
                                    "selector": ".highlight",
                                    "style": {"line-color": "#FF4136", "width": 3},
                                },
                            ],
                            elements=[],
                        ),
                    ],
                    width=6,
                ),
                dbc.Col(
                    [
                        html.H3(
                            "Segundo Grafo Bipartito", className="text-center mb-3"
                        ),
                        cyto.Cytoscape(
                            id="grafo2",
                            layout={"name": "circle", "nodeSpacing": 50},
                            style={
                                "width": "100%",
                                "height": "500px",
                                "backgroundColor": "#f8f9fa",
                            },
                            stylesheet=[
                                {
                                    "selector": ".presente",
                                    "style": {
                                        "background-color": "#0074D9",
                                        "label": "data(label)",
                                    },
                                },
                                {
                                    "selector": ".futuro",
                                    "style": {
                                        "background-color": "#2ECC40",
                                        "label": "data(label)",
                                    },
                                },
                                {
                                    "selector": ".highlight-alt",
                                    "style": {"line-color": "#FF851B", "width": 3},
                                },
                            ],
                            elements=[],
                        ),
                    ],
                    width=6,
                ),
            ]
        ),
    ],
    fluid=True,
)


@app.callback(
    [
        Output("matriz-dropdown", "options"),
        Output("resultado", "children"),
        Output("resultado", "is_open"),
        Output("grafo1", "elements"),
        Output("grafo2", "elements"),
    ],
    [Input("ejecutar-btn", "n_clicks")],
    [
        State("matriz-dropdown", "value"),
        State("estado-actual", "value"),
        State("factor-enfriamiento", "value"),
    ],
)
def actualizar_grafos(n_clicks, matriz, estado_actual, factor):
    if n_clicks is None:
        prob_ep = ProbabilidadEP()
        return [
            [{"label": opcion, "value": opcion} for opcion in prob_ep.listaMatrices()],
            "",
            False,
            [],
            [],
        ]

    if not matriz or not estado_actual or not factor:
        raise PreventUpdate

    prob_ep = ProbabilidadEP()
    estrategia3 = Estrategia3()

    matrices = prob_ep.datosMatrices(matriz)
    c1 = prob_ep.retornarEstados(matrices)
    c2 = prob_ep.retornarEstadosFuturos(matrices)

    estado_actual = tuple(map(int, estado_actual.split(",")))
    particion, diferencia, tiempo, _ = estrategia3.retornarMejorParticion(
        c1, c2, estado_actual, matriz, factor
    )

    grafo1, grafo2 = generar_grafos_bipartitos_correctos(particion)
    nodes1, edges1 = grafo1
    nodes2, edges2 = grafo2

    return (
        no_update,
        f"Mejor partición: {particion} | Diferencia: {diferencia} | Tiempo de ejecución: {tiempo:.2f} segundos",
        True,
        nodes1 + edges1,
        nodes2 + edges2,
    )


if __name__ == "__main__":
    app.run_server(debug=True)
