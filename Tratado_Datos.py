import pandas as pd
import numpy as np
import os
import gc  # Liberar memoria ram
import sys

def cargar_datos(ruta_archivo):
    Carga_Datos = pd.read_csv(ruta_archivo)
    nombre_archivo = os.path.basename(ruta_archivo)
    parte_fecha = "_".join(nombre_archivo.split("_")[-2:]).split(".")[0]
    print(parte_fecha)
    return Carga_Datos, parte_fecha

def tratar_datos(Carga_Datos):
    Carga_Datos = Carga_Datos.dropna(subset=['Frecuencia (Hz)'])
    Carga_Datos = Carga_Datos.replace(-379.29779052734375, np.nan)
    conteo_frecuencia = Carga_Datos['Frecuencia (Hz)'].value_counts()
    print(conteo_frecuencia)
    return Carga_Datos

def dividir_y_guardar_grupos(Carga_Datos, carpeta_salida):
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)
    cambios = np.where(Carga_Datos['Frecuencia (Hz)'].values[:-1] > Carga_Datos['Frecuencia (Hz)'].values[1:])[0]
    cambios = np.concatenate(([0], cambios, [len(Carga_Datos)]))
    for i in range(len(cambios) - 1):
        inicio, fin = cambios[i], cambios[i + 1]
        grupo = Carga_Datos.iloc[inicio:fin]
        grupos_frecuencia = grupo.groupby('Frecuencia (Hz)').apply(lambda x: x.to_dict(orient='records')).tolist()
        for j, subgrupo in enumerate(grupos_frecuencia):
            if subgrupo:
                if isinstance(subgrupo[0], dict):
                    nombre_archivo = os.path.join(carpeta_salida, f'Muestra_{i + 1}_Grupo_{j + 1}.csv')
                    pd.DataFrame(subgrupo).to_csv(nombre_archivo, index=False)
                    print(f"Grupo {i + 1}, Subgrupo {j + 1} guardado en '{nombre_archivo}'")

def limpiar_ram(variables_locales):
    variables_a_eliminar = ['inicio', 'fin', 'grupo', 'grupos_frecuencia', 'subgrupo', 'nombre_archivo', 'Carga_Datos', 'nombre_muestra', 'archivo']
    gc.collect()
    for variable in variables_a_eliminar:
        if variable in variables_locales:
            del variables_locales[variable]

def transponer_datos(carpeta_entrada, filas_por_grupo):
    archivos = os.listdir(carpeta_entrada)
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
    print("Proceso de procesamiento y sobrescrita de grupos completado.")

def filtrar_datos(carpeta_entrada):
    archivos_csv = [archivo for archivo in os.listdir(carpeta_entrada) if archivo.endswith('.csv')]
    for archivo in archivos_csv:
        ruta_completa = os.path.join(carpeta_entrada, archivo)
        df = pd.read_csv(ruta_completa)
        df = df.iloc[:, [0, -1]]
        df = df.rename(columns={df.columns[-1]: 'dB'})
        df.to_csv(ruta_completa, index=False)

def concatenar_datos(carpeta_entrada):
    dataframes_por_muestra = {}
    for archivo in os.listdir(carpeta_entrada):
        if archivo.endswith(".csv"):
            nombre_muestra = archivo.split("_")[1]
            df = pd.read_csv(os.path.join(carpeta_entrada, archivo))
            if nombre_muestra in dataframes_por_muestra:
                dataframes_por_muestra[nombre_muestra] = pd.concat([dataframes_por_muestra[nombre_muestra], df], ignore_index=True)
            else:
                dataframes_por_muestra[nombre_muestra] = df
    for archivo in os.listdir(carpeta_entrada):
        if archivo.endswith(".csv"):
            os.remove(os.path.join(carpeta_entrada, archivo))
    for nombre_muestra, df in dataframes_por_muestra.items():
        archivo_salida = os.path.join(carpeta_entrada, f"Muestra_{nombre_muestra}.csv")
        df.to_csv(archivo_salida, index=False, mode='w')

def asignar_frecuencias(carpeta_entrada):
    archivos_csv = [archivo for archivo in os.listdir(carpeta_entrada) if archivo.endswith('.csv')]
    BW_TEMP = 0
    MST_ANT = False
    for archivo_csv in archivos_csv:
        archivo_path = os.path.join(carpeta_entrada, archivo_csv)
        data = pd.read_csv(archivo_path)
        secuencias = data['Frecuencia (Hz)'].unique()
        secuencias.sort()
        if len(secuencias) >= 2:
            BW = (secuencias[1] - secuencias[0])
            BW_TEMP = BW
            MST_ANT = True
        elif MST_ANT:
            BW = BW_TEMP
        else:
            BW = 10000000
        nuevo_df = pd.DataFrame(columns=['Frecuencia (Hz)', 'dB'])
        for secuencia in secuencias:
            num_samples = (data['Frecuencia (Hz)'] == secuencia).sum()
            min_value = secuencia - (BW / 2)
            max_value = secuencia + (BW / 2)
            if num_samples == 1:
                num_samples = 2
            incremento_frec = BW / (num_samples - 1)
            nuevos_valores_frecuencia = min_value + np.arange(num_samples) * incremento_frec
            nuevos_valores_frecuencia = pd.Series(nuevos_valores_frecuencia)
            nuevos_valores_frecuencia.name = 'Frecuencia (Hz)'
            nuevo_df = pd.concat([nuevo_df, pd.concat([nuevos_valores_frecuencia, data[data['Frecuencia (Hz)'] == secuencia]['dB'].reset_index(drop=True)], axis=1)], ignore_index=True)
        nuevo_df.sort_values(by=['Frecuencia (Hz)'], inplace=True)
        nuevo_df.reset_index(drop=True, inplace=True)
        nuevo_df.to_csv(archivo_path, index=False)
        print(f'Archivo procesado y sobrescrito: {archivo_path}')
        print(f"BW: {BW}")

def filtrar_muestras_frecuencias(carpeta_entrada):
    archivos = os.listdir(carpeta_entrada)
    for archivo in archivos:
        if archivo.endswith('.csv'):
            archivo_completo = os.path.join(carpeta_entrada, archivo)
            df = pd.read_csv(archivo_completo)
            result_data = []
            for freq in df['Frecuencia (Hz)'].unique():
                filtered_rows = df[df['Frecuencia (Hz)'] == freq]
                avg_db = filtered_rows['dB'].mean()
                result_data.append((freq, avg_db))
            result_df = pd.DataFrame(result_data, columns=['Frecuencia (Hz)', 'dB'])
            result_df.to_csv(archivo_completo, index=False)

def calcular_resultados(carpeta_entrada, parte_fecha):
    ruta_resultado_final = os.path.join(carpeta_entrada, 'Resultados_' + parte_fecha)
    if not os.path.exists(ruta_resultado_final):
        os.makedirs(ruta_resultado_final)
        
    ruta_resultado_final = os.path.join(ruta_resultado_final, 'Resultado_' + parte_fecha + '.csv')
    
    archivos_csv = [archivo for archivo in os.listdir(carpeta_entrada) if archivo.endswith('.csv')]
    archivos_csv.sort()
    if len(archivos_csv) < 2:
        print("Deben existir al menos dos archivos CSV en la carpeta para calcular los resultados.")
    else:
        primer_archivo = pd.read_csv(os.path.join(carpeta_entrada, archivos_csv[0]))
        num_filas = len(primer_archivo)
        maximos = primer_archivo.copy()
        for archivo_csv in archivos_csv[1:-1]:
            ruta_archivo = os.path.join(carpeta_entrada, archivo_csv)
            df = pd.read_csv(ruta_archivo)
            if len(df) != num_filas:
                print(f"El archivo {archivo_csv} no tiene el mismo tamaño que los archivos anteriores. Se omitirá.")
                continue
            maximos['dB'] = np.maximum(maximos['dB'], df['dB'])
        maximos.to_csv(ruta_resultado_final, index=False)
        print(f"Resultados guardados en: {ruta_resultado_final}")

def main(ruta_archivo, carpeta_salida, filas_por_grupo):
    Carga_Datos, parte_fecha = cargar_datos(ruta_archivo)
    Carga_Datos = tratar_datos(Carga_Datos)
    
    # Obtener el directorio actual del programa
    directorio_actual = os.path.dirname(os.path.realpath(__file__))
    
    # Crear carpeta "Salida" si no existe en el directorio actual
    carpeta_principal = os.path.join(directorio_actual, 'Salida')
    if not os.path.exists(carpeta_principal):
        os.makedirs(carpeta_principal)

    # Definir la carpeta de salida completa
    carpeta_salida_completa = os.path.join(carpeta_principal, carpeta_salida + "_" + parte_fecha)

    dividir_y_guardar_grupos(Carga_Datos, carpeta_salida_completa)
    limpiar_ram(locals())
    transponer_datos(carpeta_salida_completa, filas_por_grupo)
    filtrar_datos(carpeta_salida_completa)
    concatenar_datos(carpeta_salida_completa)
    asignar_frecuencias(carpeta_salida_completa)
    filtrar_muestras_frecuencias(carpeta_salida_completa)
    calcular_resultados(carpeta_salida_completa, parte_fecha)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python Tratado_Datos.py <ruta_del_archivo_csv>")
        sys.exit(1)

    ruta_archivo = sys.argv[1]  # Ruta del archivo CSV pasada como argumento
    carpeta_salida = 'Muestra'  # Reemplaza con el nombre base de la carpeta de salida
    filas_por_grupo = 1024  # Reemplaza con el número de filas por grupo
    main(ruta_archivo, carpeta_salida, filas_por_grupo)
