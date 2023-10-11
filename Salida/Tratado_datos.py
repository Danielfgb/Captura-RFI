import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import os


# Carga el archivo csv para tratarlo con pandas 
Carga_Datos = pd.read_csv(r"C:\Users\dfgom\OneDrive\Escritorio\USRP\RFI_Captura\Salida\outputprueba2.csv")

# borra caracteres nulos
Carga_Datos= Carga_Datos.dropna(subset=['Frecuencia (Hz)'])
# print(Carga_Datos['Frecuencia (Hz)'].mean())

# cuenta cuentos datos hay por frecuencia y los valores de frecuencia que tiene 
conteo_frecuencia = Carga_Datos['Frecuencia (Hz)'].value_counts()
print(conteo_frecuencia)


################ Separa el archivo en el numero de muestras que se realizaron ################
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

################## Tratado de datos ###################
#Para poder tratar los datos se dividen por grupos esos hacen referencia a las muestras que se toman, 
#para posteriormente sacar el promedio de estos y el los máximos

def dividir_y_guardar_grupos(Carga_Datos, carpeta_salida):
    grupos = []
    grupo_actual = None
    cambios = np.where(Carga_Datos['Frecuencia (Hz)'].values[:-1] > Carga_Datos['Frecuencia (Hz)'].values[1:])[0]

    inicio = 0
    for cambio in cambios:
        grupo_actual = Carga_Datos.iloc[inicio:cambio + 1]
        grupos.append(grupo_actual)
        inicio = cambio + 1

    grupo_actual = Carga_Datos.iloc[inicio:]
    grupos.append(grupo_actual)

    # Crear la carpeta de salida si no existe
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)

    # Guardar los grupos en archivos CSV
    for i, grupo in enumerate(grupos):
        nombre_archivo = os.path.join(carpeta_salida, f'Muestra_{i + 1}.csv')
        grupo.to_csv(nombre_archivo, index=False)
        print(f"Grupo {i + 1} guardado en '{nombre_archivo}'")

carpeta_muestras = 'Muestras'
dividir_y_guardar_grupos(Carga_Datos, carpeta_muestras)

# Tratado de las muestras 

#Asignación de las frecuencias para cada muestra, teniendo en cuenta el ancho de banda 

#Frec_max-Frec_min/cont_frec-1

carpeta = r'C:\Users\dfgom\OneDrive\Escritorio\USRP\RFI_Captura\Salida\Muestras'  
archivos_csv = [archivo for archivo in os.listdir(carpeta) if archivo.endswith('.csv')]

BW_TEMP = 0
MST_ANT = False

# Procesar cada archivo CSV en la carpeta
for archivo_csv in archivos_csv:
    archivo_path = os.path.join(carpeta, archivo_csv)
    data = pd.read_csv(archivo_path)

    # Identificar las secuencias de frecuencias iguales
    secuencias = data['Frecuencia (Hz)'].unique()

    # Calcular el valor de BW
    if len(secuencias) >= 2: # REVISA SI HAY OTRA FRECUENCIA 
        BW = (secuencias[1] - secuencias[0])
        BW_TEMP = BW
        MST_ANT = True
        
    elif (MST_ANT == True):
        BW = BW_TEMP

    else:               # si no no hubo una muestra anterior y no tiene un valor de BW lo tomara por defecto como 20M.
        BW = 20000000

    # Crear un nuevo DataFrame para los resultados
    nuevo_df = pd.DataFrame(columns=['Frecuencia (Hz)', 'dB'])

    # Calcular y agregar los nuevos valores de frecuencia 
    for secuencia in secuencias:
        num_samples = (data['Frecuencia (Hz)'] == secuencia).sum()
        
        min_value = secuencia - (BW / 2)
        max_value = secuencia + (BW / 2)

        # Asegurar que num_samples sea al menos 2
        if num_samples == 1:
            num_samples = 2

        incremento_frec = BW / (num_samples - 1)
        nuevos_valores_frecuencia = min_value + np.arange(num_samples) * incremento_frec
        nuevos_valores_frecuencia = pd.Series(nuevos_valores_frecuencia)
        nuevos_valores_frecuencia.name = 'Frecuencia (Hz)'
        nuevo_df = pd.concat([nuevo_df, pd.concat([nuevos_valores_frecuencia, data[data['Frecuencia (Hz)'] == secuencia]['dB'].reset_index(drop=True)], axis=1)], ignore_index=True)

    # Ordenar el nuevo DataFrame por frecuencia
    nuevo_df.sort_values(by=['Frecuencia (Hz)'], inplace=True)

    # Reiniciar los índices del nuevo DataFrame
    nuevo_df.reset_index(drop=True, inplace=True)

    # Sobreescribir el archivo CSV original con los nuevos datos
    nuevo_df.to_csv(archivo_path, index=False)

    print(f'Archivo procesado y sobrescrito: {archivo_path}')
