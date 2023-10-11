import tkinter as tk
import os
import pandas as pd
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.widgets import SpanSelector

carpeta = r'C:\Users\dfgom\OneDrive\Escritorio\USRP\RFI_Captura\Salida\Muestras'

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
        ax2.set_ylim(region_y.min(), region_y.max())
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

# Crear un lienzo para mostrar la gráfica generada
fig = Figure(figsize=(10, 8))
ax1 = fig.add_subplot(211)
ax2 = fig.add_subplot(212)

canvas = FigureCanvasTkAgg(fig, master=root)
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