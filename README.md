# Captura-RFI

## Descripción:  

Este repositorio contiene el desarrollo de un Medidor Autónomo de Interferencia de Radiofrecuencia (RFI) con el propósito facilitar la selección de sitios idóneos y la caracterización del RFI.

Un medidor de RFI es un dispositivo diseñado para evaluar la presencia y la intensidad de las interferencias electromagnéticas en el espectro de radiofrecuencia. Estas interferencias, generadas por fuentes artificiales como dispositivos electrónicos, comunicaciones inalámbricas y otras emisiones no deseadas, pueden afectar significativamente las observaciones radio astronómicas. El medidor de RFI identifica y cuantifica estas interferencias, permitiendo la caracterización del entorno electromagnético.

## Contenido del repositorio:


[1. Salida:](/Salida/) Carpeta que contiene los datos generados en formato .csv con el nombre de "CSV_Salida_d-m-Y_H-M-S.csv" por el programa [Captura_RFI.grc](/Captura_RFI.grc). Este nombre incluye la fecha y hora (día, mes, año, hora, minuto y segundo) para facilitar el seguimiento de las muestras tomadas. Dentro de esta carpeta, se crea una sub-carpeta llamada **"Muestras"** seguida del mismo nombre del archivo csv, y en ella se guardan las muestras ya tratadas de dicho archivo. También se crea otra sub-carpeta llamada **"Resultados"** seguida del nombre del mismo csv, donde se almacena el posprocesamiento junto con un archivo csv que contiene dos datos resultantes y relevantes. En esta carpeta también se encuentra el código encargado del pos-procesamiento con el nombre de [Tratado_datos.py](/Salida/Tratado_Datos.py), del cual existen dos versiones: una desarrollada en Python y otra con el mismo nombre en Jupyter.

[2. GNU-RADIO: ](/Captura_RFI.grc) Programa desarrollado en GNU-Radio para la adquisición, registro y procesamiento de las señales de RF. Al iniciar el programa por primera vez, se generarán tres códigos:

- [**Captura_RFI.py**](/Captura_RFI.py): Este es el archivo general que contiene todo lo del programa.
- [**Captura_RFI_Control_Frecuencia.py**](/Captura_RFI_Control_Frecuencia.py): Código encargado de hacer el salto de frecuencia y desarrollado para el cambio de frecuencia en la tarjeta USRP B200 mediante "Polymorphic Types" (PMT).
- [**Captura_RFI_CSV.py**](/Captura_RFI_CSV.py): Este es el encargado de guardar en un archivo csv los datos de potencia tomados por la USRP y lo guardará con el nombre de Captura_RFI_CSV.py.

## Instrucciones de Uso:

Para usar el programa, lo único que se requiere es tener GNU Radio, preferiblemente versiones superiores a la 3.8. Abra el programa llamado [**Captura_RFI.grc**](/tree/main/Captura_RFI.grc). Al iniciar el programa correctamente, los demás códigos se generarán automáticamente: [**Captura_RFI.py**](/tree/main/Captura_RFI.py), [**Captura_RFI_Control_Frecuencia.py**](/tree/main/Captura_RFI_Control_Frecuencia.py) y [**Captura_RFI_CSV.py**](/tree/main/Captura_RFI_CSV.py). Además, se requiere el archivo [**Tratado_Datos.py**](/tree/main/Tratado_Datos.py), que se encarga del posprocesamiento, y el archivo [**Visualizacion_Datos.py**](/tree/main/Visualizacion_Datos.py), que se encarga de visualizar y generar los reportes finales.


La adquisición de datos se divide en muestras como se observa en siguiente la imagen:

![Medidor](./img/Diagrama%20medidor%20.png)

Esto es debido a que la tarjeta USRP cuenta con un ancho de banda limitado de 200 KHz a 56 MHz y en la adquisición se requieren analizar un ancho de banda mas amplio por lo cual se desarrollo el programa [Control frecuencia](/Control_Frecuencia.py) que esta encargado de recibir una frecuencia inicial y final y dividirla en muestra iguales con un mismo ancho de banda. 

1. Dentro del programa [Captura_RFI.grc](/Captura_RFI.grc) en la parte superior encontrara el apartado de variables en esté se encuentran cuatro variables que son las encargadas de configurar la adquisición de las señales RF, la variable samp_rate hace referencia al ancho de banda que tomara por cambio de frecuencia, como fue explicado, la variable frec_inicial y frec_final establecen en rango de frecuencia que sera analizado y la variable Intervalo_Tiempo se refiere al tiempo que analizara cada segmento antes de pasar a la siguiente frecuencia central.

    ![Variable](./img/Variables.png)

2. Dentro del mismo flujograma de GNU-Radio encontrara un bloque con el nombre de CSV writer Block, dentro de este es necesario cambiar la ruta donde guardara el archivo csv con los datos analizados y el nombre que llevara. 

    ![Variable](./img/bloc_csv.png)

3. Adquisición: A la hora de realizar la adquisicion de las señales RF se vera en pantalla 

4. archivo generado 

5. 