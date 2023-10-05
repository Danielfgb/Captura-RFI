import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import os

Carga_Datos = pd.read_csv(r"C:\Users\dfgom\OneDrive\Escritorio\USRP\RFI_Captura\Salida\outputprueba2.csv")

Carga_Datos= Carga_Datos.dropna(subset=['Frecuencia (Hz)'])
# print(Carga_Datos['Frecuencia (Hz)'].mean())

conteo_frecuencia = Carga_Datos['Frecuencia (Hz)'].value_counts()
print(conteo_frecuencia)

recuentos_por_muestra = {}

# Convertir la columna 'Frecuencia (Hz)' en un arreglo NumPy
frecuencias = Carga_Datos['Frecuencia (Hz)'].values

# Inicializar variables para llevar el seguimiento de la muestra actual y el conteo actual
muestra_actual = None
conteo_actual = 0

for frecuencia in frecuencias:
    if muestra_actual is None:
        muestra_actual = frecuencia
        conteo_actual = 1
    elif muestra_actual == frecuencia:
        conteo_actual += 1
    else:
        if muestra_actual not in recuentos_por_muestra:
            recuentos_por_muestra[muestra_actual] = []
        recuentos_por_muestra[muestra_actual].append(conteo_actual)
        
        muestra_actual = frecuencia
        conteo_actual = 1

# Agregar el último conjunto de conteos a la salida
if muestra_actual is not None:
    if muestra_actual not in recuentos_por_muestra:
        recuentos_por_muestra[muestra_actual] = []
    recuentos_por_muestra[muestra_actual].append(conteo_actual)

for muestra, conteos in recuentos_por_muestra.items():
    print(f'Frecuencia: {muestra} - Conteos: {", ".join(map(str, conteos))}')