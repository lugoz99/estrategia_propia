# Desimport os
import sys


import os



sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
)

from Data import Data
import numpy as np
import pandas as pd

class ProbabilidadEP:
    def datosMatrices(self, opcion):
        tres = Data().retornarDatosTresNodos()
        cuatro = Data().retornarDatosCuatroNodos()
        cinco = Data().retornarDatosCincoNodos()
        seis = Data().retornarDatosSeisNodos()
        ocho = Data().retornarDatosMatrizOchoNodos()
        diez = Data().retornarDatosMatrizDiezNodos()
        salida = None
        if opcion == "Tres Nodos":
            salida = tres
        if opcion == "Cuatro Nodos":
            salida = cuatro
        if opcion == "Cinco Nodos":
            salida = cinco
        if opcion == "Seis Nodos":
            salida = seis
        if opcion == "Ocho Nodos":
            salida = ocho
        if opcion == "Diez Nodos":
            salida = diez
        return salida

    def listaMatrices(self):
        opcion = [
            "Tres Nodos",
            "Cuatro Nodos",
            "Cinco Nodos",
            "Seis Nodos",
            "Ocho Nodos",
            "Diez Nodos",
        ]
        return opcion

    def generarDistribucionProbabilidades(
        self, tabla, estadoActual, estadoFuturo, num, estados
    ):
        try:
            indice = [estados.index(i) for i in estadoActual]
        except ValueError as e:
            print(f"Error: {e}")
            print("estadoActual:", estadoActual)
            print("estados:", estados)
            raise

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

    def retornarEstados(self, datos):

        resultado, estados = self.generarEstadoTransicion(datos)
        return estados

    def retornarDistribucion(self, c1, c2, valorActual, opcion):
        matrices = self.datosMatrices(opcion)
        resultado, estados = self.generarEstadoTransicion(matrices)
        datos = self.generarDistribucionProbabilidades(
            matrices, c1, c2, valorActual, estados
        )
        lista = []
        lista.append(str(datos[0][0]))

        for i in range(len(datos[0][1:])):
            lista.append(str(datos[0][1:][i]))

        df = pd.DataFrame(datos[1:], columns=lista)
        return df

    def retornarEstadosFuturos(self, datos):

        resultado, estados = self.generarEstadoTransicion(datos)
        for i in range(len(estados)):
            estados[i] = estados[i] + "'"

        return estados

    def generarProbParticiones(self, distribuciones, combinaciones):
        tablaDeparticiones = {}
        cadena = distribuciones[0][0]
        lista1, lista2 = [eval(subcadena) for subcadena in cadena.split("|")]

        for i in combinaciones[1:]:
            lista = self.particiones(distribuciones, i[0][0], i[1][0], i[0][1], i[1][1])
            nombre = "("
            for j in i[0][0]:
                if j < len(lista1):
                    nombre += f" {lista1[j]}"
            nombre += " ) ("
            for j in i[0][1]:
                if j < len(lista2):
                    nombre += f" {lista2[j]}"
            nombre += " ) - ("

            for j in i[1][0]:
                if j < len(lista1):
                    nombre += f" {lista1[j]}"
            nombre += " ) ("
            for j in i[1][1]:
                if j < len(lista2):
                    nombre += f" {lista2[j]}"
                    pass
            nombre += " )"
            tablaDeparticiones[nombre] = lista
        return tablaDeparticiones

    def retornarMejorParticion(self, c1, c2, estadoActual, candidato, opcion):
        matrices = self.datosMatrices(opcion)
        matricesP = self.retornarMatrizCondicionada(
            matrices, c1, estadoActual, candidato
        )
        c1 = self.retornarEstados(matricesP)
        c2 = self.retornarEstadosFuturos(matricesP)
        resultado, estados = self.generarEstadoTransicion(matricesP)
        distribucionProbabilidadOriginal = self.generarDistribucionProbabilidades(
            matricesP, c1, c2, estadoActual, estados
        )
        lista = []
        particion, diferencia, tiempo, lista = self.busqueda_voraz(
            matricesP, estados, distribucionProbabilidadOriginal, c1, c2, estadoActual
        )
        return particion, diferencia, tiempo, lista


    def calcularEMD(self, p1, p2):
        p1 = np.array(p1)
        p2 = np.array(p2)

        if p1.ndim != 1 or p2.ndim != 1:
            raise ValueError("p1 y p2 deben ser arrays unidimensionales")

        if len(p1) != len(p2):
            p2 = np.interp(np.linspace(0, 1, len(p1)), np.linspace(0, 1, len(p2)), p2)

        cost_matrix = np.abs(np.subtract.outer(p1, p2))
        salida = np.sum(np.min(cost_matrix, axis=1) * p1)
        return salida

    def producto_tensor(self, p1, p2):
        p1 = np.array(p1)
        p2 = np.array(p2)
        return np.outer(p1, p2).flatten()
