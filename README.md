# Captura-RFI

## Descripción:  

Este repositorio contiene el desarrollo de un Medidor Autónomo de Interferencia de Radiofrecuencia (RFI) con el propósito facilitar la selección de sitios idóneos y la caracterización del RFI para el establecimiento exitoso de un radiotelescopio de baja frecuencia en Colombia.

Un medidor de RFI es un dispositivo diseñado para evaluar la presencia y la intensidad de las interferencias electromagnéticas en el espectro de radiofrecuencia. Estas interferencias, generadas por fuentes artificiales como dispositivos electrónicos, comunicaciones inalámbricas y otras emisiones no deseadas, pueden afectar significativamente las observaciones radio astronómicas. El medidor de RFI identifica y cuantifica estas interferencias, permitiendo la caracterización del entorno electromagnético.

## Contenido del repositorio:

[1. Salida:](/Salida/) Carpeta que contiene los datos generados en formato .csv con el nombre de "CSV_Salida.csv" por el programa [Captura_RFI.grc](/Captura_RFI.grc) en esta carpeta también se encuentra el código encargado del pos-procesamiento con el nombre de [Tratado_datos.py](/Salida/Tratado_datos.py) de la cual se encuentran dos versiones una desarrollada en python y otra con el mismo nombre en Jupyter.

[2. GNU-RADIO: ](/Captura_RFI.grc) Programa desarrollado en GNU-Radio para la adquisición, registro y procesamiento de las señales de RF.

[3. Control frecuencia: ](/Control_Frecuencia.py) Código desarrollado para el cambio de frecuencia en la tarjeta USRP B200 mediante "Polymorphic Types" (PMT).

[4. CSV: ](/CSV.py) Código desarrollado para el guardado de los datos en un archivo CSV.

## Instrucciones de Uso:

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