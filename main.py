import json
import time
import numpy as np
from pymongo import MongoClient
from Estrategia3 import Estrategia3
from EstrategiaFuerzBruta import EstrategiaFuerzaBruta

from ProbabilidadEp import ProbabilidadEP


class InMemoryDB:
    def __init__(self):
        self.data = []

    def insert_one(self, data):
        self.data.append(data)
        print("Datos guardados en memoria:", data)

    def find(self):
        return self.data


# Intentar conexión a MongoDB con timeout
try:
    client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
    client.server_info()  # Esto lanza una excepción si la conexión falla
    db = client["proyecto_algoritmos"]
    collection = db["resultados_pruebas"]
    print("Conexión exitosa a MongoDB")
except Exception as e:
    print(f"Error al conectar a MongoDB: {e}")
    print("Usando almacenamiento en memoria...")
    collection = InMemoryDB()

# Inicializar ProbabilidadEP
prob_ep = ProbabilidadEP()


def registrar_resultados(data):
    try:
        # Convertir valores numpy a Python nativo
        def convertir_nativo(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            return obj

        data_converted = json.loads(json.dumps(data, default=convertir_nativo))
        print(f"Registrando en MongoDB: {json.dumps(data_converted, indent=4)}")
        collection.insert_one(data_converted)
        print("Resultados guardados exitosamente en MongoDB")
        return True
    except Exception as e:
        print(f"Error al registrar resultados: {e}")
        return False


def ejecutar_fuerza_bruta(matriz, estado_actual):
    try:
        matrices = prob_ep.datosMatrices(matriz)
        if matrices is None:
            raise ValueError(f"No se encontraron datos para la matriz '{matriz}'.")

        c1 = prob_ep.retornarEstados(matrices)
        c2 = prob_ep.retornarEstadosFuturos(matrices)

        estrategia_fb = EstrategiaFuerzaBruta()
        inicio = time.time()
        particion, diferencia = estrategia_fb.retornarMejorParticion(
            c1, c2, estado_actual, matriz
        )
        tiempo = time.time() - inicio

        registrar_resultados(
            {
                "metodo": "fuerza_bruta",
                "matriz": matriz,
                "estado_actual": estado_actual,
                "resultado": {
                    "particion": particion,
                    "diferencia": float(diferencia),
                    "tiempo": float(tiempo),
                },
            }
        )

        print(
            f"Fuerza Bruta ejecutada: Diferencia: {diferencia:.4f} | Tiempo: {tiempo:.2f}s"
        )
    except Exception as e:
        print(f"Error al ejecutar Fuerza Bruta: {str(e)}")


def ejecutar_recocido_simulado(matriz, estado_actual, factor_enfriamiento):
    try:
        if not 0 < factor_enfriamiento < 1:
            raise ValueError("El factor de enfriamiento debe estar entre 0 y 1.")

        matrices = prob_ep.datosMatrices(matriz)
        if matrices is None:
            raise ValueError(f"No se encontraron datos para la matriz '{matriz}'.")

        c1 = prob_ep.retornarEstados(matrices)
        c2 = prob_ep.retornarEstadosFuturos(matrices)

        estrategia3 = Estrategia3()
        particion, diferencia, tiempo, _ = estrategia3.retornarMejorParticion(
            c1, c2, estado_actual, matriz, factor_enfriamiento
        )

        registrar_resultados(
            {
                "metodo": "recocido_simulado",
                "matriz": matriz,
                "estado_actual": estado_actual,
                "factor": float(factor_enfriamiento),
                "resultado": {
                    "particion": particion,
                    "diferencia": float(diferencia),
                    "tiempo": float(tiempo),
                },
            }
        )

        print(
            f"Recocido Simulado ejecutado: Diferencia: {diferencia:.4f} | Tiempo: {tiempo:.2f}s"
        )
    except Exception as e:
        print(f"Error al ejecutar Recocido Simulado: {str(e)}")


if __name__ == "__main__":
    # Listar opciones disponibles
    opciones = prob_ep.listaMatrices()
    print(f"Matrices disponibles: {', '.join(opciones)}")

    # Menú interactivo
    print("Seleccione el algoritmo a ejecutar:")
    print("1. Fuerza Bruta")
    print("2. Recocido Simulado")

    seleccion = input("Ingrese el número de su elección: ")

    if seleccion == "1":
        matriz = input("Ingrese el nombre de la matriz: ")
        estado_actual = input("Ingrese el estado actual: ")
        ejecutar_fuerza_bruta(matriz, estado_actual)
    elif seleccion == "2":
        matriz = input("Ingrese el nombre de la matriz: ")
        estado_actual = input("Ingrese el estado actual: ")
        factor_enfriamiento = float(
            input("Ingrese el factor de enfriamiento (0.1 - 0.9): ")
        )
        ejecutar_recocido_simulado(matriz, estado_actual, factor_enfriamiento)
    else:
        print("Selección inválida.")
