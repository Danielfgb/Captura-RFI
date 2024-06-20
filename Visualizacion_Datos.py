import tkinter as tk
import os
import pandas as pd
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.widgets import SpanSelector

#carpeta = r'C:\Users\dfgom\OneDrive\Escritorio\USRP\RFI_Captura\Salida\Resultados'
carpeta = r'C:\Users\dfgom\OneDrive\Escritorio\USRP\RFI_Captura\Salida\Muestras_19-06-2024_16-46-34'


# Función para cargar y mostrar los datos desde un archivo CSV seleccionado
def cargar_archivo():
    archivo_seleccionado = archivo_var.get()
    
    if archivo_seleccionado:
        df = pd.read_csv(os.path.join(carpeta, archivo_seleccionado))
        
        x = df.columns[0]  
        y = df.columns[1]  
        
        x = df[x].values
        y = df[y].values
        
        ax1.clear()
        ax1.plot(x, y)
        
        # Ajustar los límites del eje y según tus necesidades
        y_min = min(y) - 10
        y_max = max(y) + 10
        
        ax1.set_ylim(y_min, y_max)
        ax1.set_title(f'Archivo seleccionado: {archivo_seleccionado}')
        
        # Actualizar las variables globales x e y
        global x_global, y_global
        x_global = x
        y_global = y
        
        # Calcular estadísticas
        maximos = sorted(y, reverse=True)[:90]
        media = np.mean(y)
        estadisticas_texto = f"10 valores máximos: {maximos}\nMedia: {media}"
        estadisticas_label.config(text=estadisticas_texto)
        
        # Dibujar línea roja de la media
        ax1.axhline(y=media, color='red', linestyle='--', label=f'Media: {media}')
        
        # Marcar los 10 valores máximos con puntos rojos
        for valor_maximo in maximos:
            indice = np.where(y == valor_maximo)[0][0]
            ax1.plot(x[indice], valor_maximo, 'ro')  # Punto rojo en el máximo
        
        ax1.legend()  # Mostrar la leyenda en la gráfica
        canvas.draw()

# Función para manejar la selección de una región
def onselect(xmin, xmax):
    indmin, indmax = np.searchsorted(x_global, (xmin, xmax))
    indmax = min(len(x_global) - 1, indmax)

    region_x = x_global[indmin:indmax]
    region_y = y_global[indmin:indmax]

    if len(region_x) >= 2:
        ax2.clear()
        ax2.plot(region_x, region_y)
        ax2.set_xlim(region_x[0], region_x[-1])
        ax2.set_ylim((region_y.min()-5), (region_y.max()+5))
        canvas.draw()

# Crear la ventana principal
root = tk.Tk()
root.title("Generador de Gráficas")

# Obtener la lista de archivos CSV en la carpeta
archivos_csv = [archivo for archivo in os.listdir(carpeta) if archivo.endswith('.csv')]

# Variable para almacenar el archivo seleccionado
archivo_var = tk.StringVar(root)
archivo_var.set(archivos_csv[0] if archivos_csv else "")

# Crear una lista desplegable con los nombres de los archivos
archivo_dropdown = tk.OptionMenu(root, archivo_var, *archivos_csv)
archivo_dropdown.pack()

# Crear un botón para cargar y mostrar los datos del archivo seleccionado
cargar_button = tk.Button(root, text="Generar Gráfica", command=cargar_archivo)
cargar_button.pack()

# Etiqueta para mostrar estadísticas
estadisticas_label = tk.Label(root, text="")
estadisticas_label.pack()  # Empaquetamos la etiqueta en la ventana principal

# Crear un lienzo para mostrar la gráfica generada
fig = Figure(figsize=(18, 12))
ax1 = fig.add_subplot(211)
ax2 = fig.add_subplot(212)

# Crear el lienzo de matplotlib
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().pack()

# Crear el selector de región
span = SpanSelector(
    ax1,
    onselect,
    "horizontal",
    useblit=True,
    props=dict(alpha=0.5, facecolor="tab:blue"),
    interactive=True,
    drag_from_anywhere=True
)

# Variables globales para x e y
x_global = []
y_global = []

# Mostrar la ventana principal
root.mainloop()
