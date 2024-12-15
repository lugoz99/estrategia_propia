import threading
import time
from dash import html
import dash_cytoscape as cyto
from dash import Dash
from Estrategia3 import Estrategia3
from ProbabilidadEp import ProbabilidadEP


# Función para ejecutar la aplicación Dash
def ejecutar_dash_app(app):
    app.run_server(
        debug=True, use_reloader=False
    )  # use_reloader=False evita reinicios múltiples


# Función para manejar la entrada de datos en un hilo separado
def manejar_datos():
    prob_ep = ProbabilidadEP()
    estrategia3 = Estrategia3()

    print("Matrices disponibles:")
    opciones = prob_ep.listaMatrices()
    for idx, opcion in enumerate(opciones):
        print(f"{idx + 1}. {opcion}")

    seleccion = int(input("Seleccione la matriz: "))
    opcion_matriz = opciones[seleccion - 1]

    matrices = prob_ep.datosMatrices(opcion_matriz)
    c1 = prob_ep.retornarEstados(matrices)
    c2 = prob_ep.retornarEstadosFuturos(matrices)

    estado_actual = input("Ingrese el estado actual (ejemplo: '0,1'): ")
    estado_actual = tuple(map(int, estado_actual.split(",")))

    factor = float(input("Ingrese el factor de enfriamiento (ejemplo: 0.85): "))

    particion, diferencia, tiempo, _ = estrategia3.retornarMejorParticion(
        c1, c2, estado_actual, opcion_matriz, factor
    )

    # Generar los grafos bipartitos correctamente
    grafo1, grafo2 = generar_grafos_bipartitos_correctos(particion)

    # Crear y actualizar la app Dash
    app = crear_dash_app_bipartita_correcta(
        grafo1, grafo2, particion, diferencia, tiempo
    )
    threading.Thread(target=ejecutar_dash_app, args=(app,)).start()


def generar_grafos_bipartitos_correctos(particion):
    """
    Genera dos grafos bipartitos basados en la partición correcta.
    """
    grafo1, grafo2 = particion

    # Primer grafo: conexiones entre grafo1 presente y futuro
    nodes_grafo1 = [
        {"data": {"id": nodo, "label": nodo, "group": "futuro"}, "classes": "futuro"}
        for nodo in grafo1[0]
    ]
    nodes_grafo1 += [
        {
            "data": {"id": nodo, "label": nodo, "group": "presente"},
            "classes": "presente",
        }
        for nodo in grafo1[1]
    ]
    edges_grafo1 = [
        {"data": {"source": presente, "target": futuro}, "classes": "highlight"}
        for presente in grafo1[1]
        for futuro in grafo1[0]
    ]

    # Segundo grafo: conexiones entre grafo2 presente y futuro
    nodes_grafo2 = [
        {"data": {"id": nodo, "label": nodo, "group": "futuro"}, "classes": "futuro"}
        for nodo in grafo2[0]
    ]
    nodes_grafo2 += [
        {
            "data": {"id": nodo, "label": nodo, "group": "presente"},
            "classes": "presente",
        }
        for nodo in grafo2[1]
    ]
    edges_grafo2 = [
        {"data": {"source": presente, "target": futuro}, "classes": "highlight-alt"}
        for presente in grafo2[1]
        for futuro in grafo2[0]
    ]

    return (nodes_grafo1, edges_grafo1), (nodes_grafo2, edges_grafo2)


def crear_dash_app_bipartita_correcta(grafo1, grafo2, particion, diferencia, tiempo):
    """
    Configura la app Dash para mostrar los dos grafos bipartitos correctamente.
    """
    nodes1, edges1 = grafo1
    nodes2, edges2 = grafo2

    app = Dash(__name__)

    app.layout = html.Div(
        [
            html.H1("Grafos Bipartitos Basados en la Partición Correcta"),
            html.Div(f"Mejor partición: {particion}"),
            html.Div(f"Diferencia: {diferencia}"),
            html.Div(f"Tiempo de ejecución: {tiempo} segundos"),
            # Primer grafo bipartito
            html.Div("Primer Grafo Bipartito (Conexión entre presente y futuro):"),
            cyto.Cytoscape(
                id="grafo1",
                elements=nodes1 + edges1,
                layout={"name": "grid"},
                style={"width": "45%", "height": "500px", "display": "inline-block"},
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
            ),
            # Segundo grafo bipartito
            html.Div("Segundo Grafo Bipartito (Conexión entre presente y futuro):"),
            cyto.Cytoscape(
                id="grafo2",
                elements=nodes2 + edges2,
                layout={"name": "grid"},
                style={"width": "45%", "height": "500px", "display": "inline-block"},
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
            ),
        ]
    )

    return app


if __name__ == "__main__":
    # Crear un hilo para manejar la entrada de datos
    hilo_datos = threading.Thread(target=manejar_datos)
    hilo_datos.start()

    # Mantener el programa principal corriendo
    while hilo_datos.is_alive():
        time.sleep(1)
