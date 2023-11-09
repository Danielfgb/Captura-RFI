import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# Carga el archivo csv para tratarlo con pandas 
Carga_Datos = pd.read_csv(r"C:\Users\dfgom\OneDrive\Escritorio\USRP\RFI_Captura\Salida\CSV_Salida.csv")

# borra caracteres nulos
Carga_Datos= Carga_Datos.dropna(subset=['Frecuencia (Hz)'])
Carga_Datos = Carga_Datos.replace(-379.29779052734375, np.nan) # error al tomar las muestras

# cuenta cuentos datos hay por frecuencia y los valores de frecuencia que tiene 
conteo_frecuencia = Carga_Datos['Frecuencia (Hz)'].value_counts()
print(conteo_frecuencia)

################ Separa el archivo en el numero de muestras que se realizaron (Visualizacion) ###############

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

######################################## Tratado de datos ##################################
# divide por grupos de frecuencias y de muestras 

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

    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)

    def agrupar_por_frecuencia(df):
        grupos_frecuencia = {}
        for _, row in df.iterrows():
            frecuencia = row['Frecuencia (Hz)']
            if frecuencia not in grupos_frecuencia:
                grupos_frecuencia[frecuencia] = []
            grupos_frecuencia[frecuencia].append(row)
        return list(grupos_frecuencia.values())

    for i, grupo in enumerate(grupos):
        
        grupos_frecuencia = agrupar_por_frecuencia(grupo)

        for j, subgrupo in enumerate(grupos_frecuencia):
            nombre_archivo = os.path.join(carpeta_salida, f'Muestra_{i + 1}_Grupo_{j + 1}.csv')
            df = pd.DataFrame(subgrupo)
            df.to_csv(nombre_archivo, index=False)
            print(f"Grupo {i + 1}, Subgrupo {j + 1} guardado en '{nombre_archivo}'")

carpeta_muestras = 'Muestras'
dividir_y_guardar_grupos(Carga_Datos, carpeta_muestras)

###################################################################################################

carpeta_entrada = r'C:\Users\dfgom\OneDrive\Escritorio\USRP\RFI_Captura\Salida\Muestras' # Remplazar por variable (carpeta_muestras)

archivos = os.listdir(carpeta_entrada)

archivos_csv = [archivo for archivo in os.listdir(carpeta_entrada) if archivo.endswith('.csv')]

filas_por_grupo = 1024

##################################### Tratado de las muestras ##################################### 

# transpone los datos cada 1024 datos y saca el promedio de este en la ultima columna 

for archivo in archivos:
    if archivo.endswith('.csv'):  
        
        data = pd.read_csv(os.path.join(carpeta_entrada, archivo))

        cantidad_grupos = len(data['Frecuencia (Hz)']) // filas_por_grupo
        columna_frecuencia = pd.Series(data['Frecuencia (Hz)'][:cantidad_grupos]).repeat(filas_por_grupo).reset_index(drop=True)
        data['Grupo'] = (data.index // filas_por_grupo) + 1
        data['Nuevo_Indice'] = data.groupby('Grupo').cumcount()
        df_pivot = data.pivot(index='Nuevo_Indice', columns='Grupo', values='dB')
        df_pivot.columns = [f'dB{col}' for col in df_pivot.columns]
        df_pivot.reset_index(drop=True, inplace=True)
        df_pivot.index.name = 'Indice'
        df_pivot['Frecuencia (Hz)'] = columna_frecuencia
        df_pivot = df_pivot[['Frecuencia (Hz)'] + [col for col in df_pivot.columns if col != 'Frecuencia (Hz)']]
        df_promedio = df_pivot.copy()
        df_promedio['Promedio_dB'] = df_pivot.iloc[:, 1:].mean(axis=1)

        df_promedio.to_csv(os.path.join(carpeta_entrada, archivo), index=False)

        print(f"Archivo '{archivo}' procesado y sobrescrito.")

print("Proceso de procesamiento y sobrescritura de grupos completado.")

#################Conserva primera columna (Frecuencia Hz) segunda columna (Promedio dB de grupo de frecuencia)####################
# elimina los datos restantes, concerva primera columna (Frecuencia) y ultima columna, promedio de frecuencias por muestra 

for archivo in archivos_csv:
    ruta_completa = os.path.join(carpeta_entrada, archivo)

    df = pd.read_csv(ruta_completa)

    df = df.iloc[:, [0, -1]]

    df = df.rename(columns={df.columns[-1]: 'dB'})
    df.to_csv(ruta_completa, index=False)

########################### Concatena las muestras, une las frecuencias que pertenecen a la misma muestra ####################################

dataframes_por_muestra = {}

for archivo in os.listdir(carpeta_entrada):
    if archivo.endswith(".csv"):
        nombre_muestra = archivo.split("_")[1]
        df = pd.read_csv(os.path.join(carpeta_entrada, archivo))

        if nombre_muestra in dataframes_por_muestra:
            dataframes_por_muestra[nombre_muestra] = pd.concat([dataframes_por_muestra[nombre_muestra], df], ignore_index=True)
        else:
            dataframes_por_muestra[nombre_muestra] = df

# Elimina los archivos originales
for archivo in os.listdir(carpeta_entrada):
    if archivo.endswith(".csv"):
        os.remove(os.path.join(carpeta_entrada, archivo))

for nombre_muestra, df in dataframes_por_muestra.items():
    archivo_salida = os.path.join(carpeta_entrada, f"Muestra_{nombre_muestra}.csv")
    df.to_csv(archivo_salida, index=False, mode='w')  

############################ Asignacion de las frecuencias para las muestras ####################################

#Asignación de las frecuencias para cada muestra, teniendo en cuenta el ancho de banda 

#Frec_max-Frec_min/cont_frec-1

carpeta = r'C:\Users\dfgom\OneDrive\Escritorio\USRP\RFI_Captura\Salida\Muestras'  
archivos_csv = [archivo for archivo in os.listdir(carpeta) if archivo.endswith('.csv')]

BW_TEMP = 0
MST_ANT = False

# Procesar cada archivo CSV en la carpetax
for archivo_csv in archivos_csv:
    archivo_path = os.path.join(carpeta, archivo_csv)
    data = pd.read_csv(archivo_path)

    # Identificar las secuencias de frecuencias iguales
    secuencias = data['Frecuencia (Hz)'].unique()
    secuencias.sort() # organiza variable secuencias de menor a mayor

    # Calcular el valor de BW
    if len(secuencias) >= 2: # REVISA SI HAY OTRA FRECUENCIA 
        BW = (secuencias[1] - secuencias[0])
        BW_TEMP = BW
        MST_ANT = True
        
    elif (MST_ANT == True):
        BW = BW_TEMP

    else:               # si no no hubo una muestra anterior y no tiene un valor de BW lo tomara por defecto como 20M.
        BW = 10000000

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
    print (f"BW: {BW} ")

################################################################################################

for archivo in archivos:
    if archivo.endswith('.csv'):
        # Ruta completa al archivo
        archivo_completo = os.path.join(carpeta_entrada, archivo)
        
        # Lee el archivo CSV en un DataFrame
        df = pd.read_csv(archivo_completo)
        
        # Inicializa una lista para almacenar los resultados
        result_data = []
        
        # Itera a través de los valores únicos en la columna 'Frecuencia (Hz)'
        for freq in df['Frecuencia (Hz)'].unique():
            # Filtra las filas que tienen el mismo valor en 'Frecuencia (Hz)'
            filtered_rows = df[df['Frecuencia (Hz)'] == freq]
            
            # Calcula el promedio de la columna 'dB'
            avg_db = filtered_rows['dB'].mean()
            
            # Agrega una tupla con el valor de 'Frecuencia (Hz)' y el promedio 'dB' a la lista de resultados
            result_data.append((freq, avg_db))
        
        # Crea un DataFrame a partir de la lista de resultados
        result_df = pd.DataFrame(result_data, columns=['Frecuencia (Hz)', 'dB'])
        
        # Guarda el resultado en el mismo archivo CSV
        result_df.to_csv(archivo_completo, index=False)


#########################################################################################

################################3 Promedio ###############################################
ruta_resultados = 'Resultados'

# Obtener la lista de archivos CSV en el directorio
archivos_csv = [archivo for archivo in os.listdir(carpeta_entrada) if archivo.endswith('.csv')]

# Ordenar los archivos alfabéticamente
archivos_csv.sort()

# Verificar si hay al menos dos archivos CSV
if len(archivos_csv) < 2:
    print("Deben existir al menos dos archivos CSV en la carpeta para calcular promedios y máximos.")
else:
    # Leer el primer archivo CSV para obtener el encabezado y comprobar si los archivos tienen el mismo tamaño
    primer_archivo = pd.read_csv(os.path.join(carpeta_entrada, archivos_csv[0]))
    num_filas = len(primer_archivo)

    # Crear DataFrames para los promedios y máximos
    promedios = primer_archivo.copy()
    maximos = primer_archivo.copy()

    for archivo_csv in archivos_csv[1:-1]:
        ruta_archivo = os.path.join(carpeta_entrada, archivo_csv)
        df = pd.read_csv(ruta_archivo)

        # Comprobar si el DataFrame tiene el mismo tamaño que el primero
        if len(df) != num_filas:
            print(f"El archivo {archivo_csv} no tiene el mismo tamaño que los archivos anteriores. Se omitirá.")
        else:
            # Calcular el promedio y el máximo y agregarlos a los DataFrames de promedios y máximos
            promedios['dB'] = promedios['dB'] + df['dB']
            maximos['dB'] = maximos['dB'].combine_first(df['dB'])

    # Calcular el promedio dividiendo la suma de dB por el número de archivos válidos
    promedios['dB'] = promedios['dB'] / (len(archivos_csv) - 1)

    # Comprobar si la carpeta de resultados existe, si no, crearla
    if not os.path.exists(ruta_resultados):
        os.makedirs(ruta_resultados)

    # Guardar los DataFrames de promedios y máximos como archivos CSV
    promedios.to_csv(os.path.join(ruta_resultados, 'promedios.csv'), index=False)
    maximos.to_csv(os.path.join(ruta_resultados, 'maximos.csv'), index=False)

    print("Los resultados se han guardado en la carpeta 'Resultados'.")