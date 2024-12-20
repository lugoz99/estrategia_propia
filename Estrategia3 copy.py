import time
import numpy as np
import random
import math
import os
import sys

from ProbabilidadEp import ProbabilidadEP

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
)


class Estrategia3:
    def datosMatriz(self, opcion):

        p = ProbabilidadEP()
        datos = p.datosMatrices(opcion)
        return datos

    def generarDistribucionProbabilidades(
        self, tabla, estadoActual, estadoFuturo, num, estados
    ):
        indice = [estados.index(i) for i in estadoActual]
        probabilidadesDistribuidas = []
        for i in estadoFuturo:
            if "'" in i:
                i = i[:-1]
            nuevaTabla = self.generarTablaComparativa(tabla[i])
            filtro2 = self.porcentajeDistribucion(nuevaTabla, indice, num)
            probabilidadesDistribuidas.append(filtro2)
        tabla = self.generarTabla(probabilidadesDistribuidas, num)
        tabla[0] = [[estadoFuturo, estadoActual]] + tabla[0]
        tabla[1] = [num] + tabla[1]
        return tabla

    def generarTabla(self, distribucion, num, i=0, numBinario="", nuevoValor=1):
        if i == len(distribucion):
            numBinario = "0" * (len(distribucion) - len(numBinario)) + numBinario
            nuevoDato = tuple(int(bit) for bit in numBinario)
            return [[nuevoDato], [nuevoValor]]
        else:
            tabla = self.generarTabla(
                distribucion,
                num,
                i + 1,
                numBinario + "0",
                nuevoValor * distribucion[i][1][2],
            )
            tabla2 = self.generarTabla(
                distribucion,
                num,
                i + 1,
                numBinario + "1",
                nuevoValor * distribucion[i][1][1],
            )
            return [tabla[0] + tabla2[0], tabla[1] + tabla2[1]]

    def porcentajeDistribucion(self, tabla, indice, num):
        tablaNueva = [tabla[0]]
        try:
            tabla1 = [
                fila
                for fila in tabla[1:]
                if all(
                    i < len(num) and pos < len(fila[0]) and fila[0][pos] == num[i]
                    for i, pos in enumerate(indice)
                )
            ]
        except IndexError as e:
            print(f"IndexError: {e}")
            raise

        nuevosValores = [0, 0]
        for i in tabla1:
            nuevosValores[0] += i[1]
            nuevosValores[1] += i[2]

        total = sum(nuevosValores)
        nuevosValores = [v / total if total != 0 else v for v in nuevosValores]
        nuevaFila = [num, *nuevosValores]
        tablaNueva.append(nuevaFila)
        return tablaNueva

    def generarTablaComparativa(self, diccionario):
        lista = [["key", (1,), (0,)]]
        for k, v in diccionario.items():
            lista.append([k, v, 1 - v])
        return lista

    def generarEstadoTransicion(self, subconjuntos):
        estados = list(subconjuntos.keys())
        transiciones = {}
        estado_actual = [0] * len(estados)

        def aux(i):
            if i == len(estados):
                estado_actual_tuple = tuple(estado_actual)
                estado_futuro = tuple(
                    subconjuntos[estado][estado_actual_tuple] for estado in estados
                )
                transiciones[estado_actual_tuple] = estado_futuro
            else:
                estado_actual[i] = 0
                aux(i + 1)
                estado_actual[i] = 1
                aux(i + 1)

        aux(0)
        return transiciones, estados

    def retornarMejorParticion(self, c1, c2, estadoActual, opcion, factor):
        matrices = self.datosMatriz(opcion)
        resultado, estados = self.generarEstadoTransicion(matrices)
        distribucionProbabilidadOriginal = self.generarDistribucionProbabilidades(
            matrices, c1, c2, estadoActual, estados
        )
        inicio = time.time()
        particion, diferencia, lista = self.recocidoSimulado(
            matrices,
            estados,
            distribucionProbabilidadOriginal,
            c1,
            c2,
            estadoActual,
            factor,
        )
        tiempo = time.time() - inicio
        return particion, diferencia, tiempo, lista

    def recocidoSimulado(
        self, matrices, estados, disProbdOriginal, c1, c2, estadoActual, factor
    ):
        mejor_particion = None
        menor_diferencia = float("inf")
        listaParticionesEvaluadas = []
        temperatura = 1000
        iteraciones_por_temperatura = 10

        while temperatura > 1:
            for _ in range(iteraciones_por_temperatura):
                c1_izq, c2_izq, c1_der, c2_der = self.generar_vecino(c1, c2)
                diferencia = self.obtener_diferencia(
                    c1_izq,
                    c2_izq,
                    c1_der,
                    c2_der,
                    matrices,
                    estadoActual,
                    disProbdOriginal,
                    estados,
                )
                if diferencia < menor_diferencia:
                    menor_diferencia = diferencia
                    mejor_particion = [
                        (tuple(c2_izq), tuple(c1_izq)),
                        (tuple(c2_der), tuple(c1_der)),
                    ]
                else:
                    probabilidad_aceptacion = math.exp(
                        (menor_diferencia - diferencia) / temperatura
                    )
                    if random.random() < probabilidad_aceptacion:
                        menor_diferencia = diferencia
                        mejor_particion = [
                            (tuple(c2_izq), tuple(c1_izq)),
                            (tuple(c2_der), tuple(c1_der)),
                        ]
            temperatura *= factor
        return mejor_particion, menor_diferencia, listaParticionesEvaluadas

    def obtener_diferencia(
        self,
        c1_izq,
        c2_izq,
        c1_der,
        c2_der,
        matrices,
        estadoActual,
        disOriginal,
        estados,
    ):
        distribucion_izq = self.generarDistribucionProbabilidades(
            matrices, c1_izq, c2_izq, estadoActual, estados
        )
        distribucion_der = self.generarDistribucionProbabilidades(
            matrices, c1_der, c2_der, estadoActual, estados
        )
        p1 = distribucion_izq[1][1:]
        p2 = distribucion_der[1][1:]
        prodTensor = self.producto_tensor(p1, p2)
        return self.calcularEMD(disOriginal[1][1:], prodTensor)

    def generar_vecino(self, c1, c2):
        mitad_c1 = len(c1) // 2
        mitad_c2 = len(c2) // 2
        c1_izq = random.sample(c1, mitad_c1)
        c1_der = list(set(c1) - set(c1_izq))
        c2_izq = random.sample(c2, mitad_c2)
        c2_der = list(set(c2) - set(c2_izq))
        return c1_izq, c2_izq, c1_der, c2_der

    def calcularEMD(self, p1, p2):
        p1, p2 = np.array(p1), np.array(p2)
        cost_matrix = np.abs(np.subtract.outer(p1, p2))
        return np.sum(np.min(cost_matrix, axis=1) * p1)

    def producto_tensor(self, p1, p2):
        return np.outer(p1, p2).flatten()
