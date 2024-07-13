import tkinter as tk
from tkinter import filedialog, messagebox
import os
import pandas as pd
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.widgets import SpanSelector
import csv
import re

# Función para seleccionar la carpeta de salida
def seleccionar_carpeta():
    carpeta_seleccionada = filedialog.askdirectory()
    if carpeta_seleccionada:
        carpeta_var.set(carpeta_seleccionada)
        cargar_archivos_csv(carpeta_seleccionada)

# Función para cargar los archivos CSV de las subcarpetas "Muestra" y "Resultados"
def cargar_archivos_csv(carpeta):
    archivos_csv = []
    regex_muestra = re.compile(r'^Muestra_.+')
    regex_resultados = re.compile(r'^Resultado_.+')
    
    for root, dirs, files in os.walk(carpeta):
        for dir_name in dirs:
            if regex_muestra.match(dir_name) or regex_resultados.match(dir_name):
                subdir_path = os.path.join(root, dir_name)
                for file in os.listdir(subdir_path):
                    if file.endswith('.csv'):
                        relative_path = os.path.relpath(os.path.join(subdir_path, file), carpeta)
                        archivos_csv.append(relative_path)
    
    archivo_var.set("")  # Limpiar la selección anterior
    archivo_dropdown['menu'].delete(0, 'end')
    for archivo in archivos_csv:
        archivo_dropdown['menu'].add_command(label=archivo, command=tk._setit(archivo_var, archivo))

# Función para cargar y mostrar los datos desde un archivo CSV seleccionado
def cargar_archivo():
    archivo_seleccionado = archivo_var.get()
    carpeta = carpeta_var.get()
    
    if archivo_seleccionado:
        df = pd.read_csv(os.path.join(carpeta, archivo_seleccionado))
        
        x = df.columns[0]  
        y = df.columns[1]  
        
        x = df[x].values
        y = df[y].values
        
        ax1.clear()
        ax1.plot(x, y)
        
        y_min = min(y) - 5
        y_max = max(y) + 5
        
        ax1.set_ylim(y_min, y_max)
        ax1.set_title(f'Archivo seleccionado: {archivo_seleccionado}')
        
        global x_global, y_global
        x_global = x
        y_global = y
        
        # Calcular y mostrar el piso de ruido con formato específico
        media = np.mean(y)
        media_str = f"{media:.3f} dB"
        
        # Dibujar línea roja con el piso de ruido
        ax1.axhline(y=media, color='red', linestyle='--', label=f'Piso ruido: {media_str}')
        
        ax1.legend()  
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
        
        # Mostrar los máximos sobre el setpoint 
        setpoint = float(setpoint_entry.get())
        encontrar_maximos(setpoint, ax2)
        
        canvas.draw()

# Función para encontrar y mostrar máximos por encima de un setpoint
def encontrar_maximos(setpoint, axis):
    global x_global, y_global
    
    if len(x_global) == 0 or len(y_global) == 0:
        return
    
    maximos = []
    for i, valor in enumerate(y_global):
        if valor > setpoint:
            maximos.append((x_global[i], valor))
    
    if maximos:
        x_maximos, y_maximos = zip(*maximos)
        axis.plot(x_maximos, y_maximos, 'go', label=f'Máximos > {setpoint} dB')
        axis.legend()
        canvas.draw()

# Función para guardar los máximos encontrados en un archivo CSV cuando se presiona "Generar Reporte"
def guardar_reporte():
    setpoint = float(setpoint_entry.get())
    global x_global, y_global
    
    if len(x_global) == 0 or len(y_global) == 0:
        messagebox.showerror("Error", "No hay datos para generar el reporte.")
        return
    
    maximos = []
    for i, valor in enumerate(y_global):
        if valor > setpoint:
            maximos.append((x_global[i], valor))
    
    if not maximos:
        messagebox.showinfo("Información", f"No se encontraron máximos sobre el setpoint {setpoint} dB.")
        return
    
    # Obtener información adicional para el reporte
    nombre_archivo = archivo_var.get()
    media = np.mean(y_global)
    
    # Construir los datos del reporte
    reporte = []
    reporte.append(f"Reporte del archivo: {nombre_archivo}")
    reporte.append(f"Piso de ruido: {media:.3f} dB")
    reporte.append(f"Setpoint: {setpoint} dB")
    reporte.append("Valores maximos por encima del setpoint:")
    reporte.append("Frecuencia (MHz), dB")  # Encabezado de los valores máximos
    
    for freq, db in maximos:
        reporte.append(f"{freq:.2f}, {db:.2f}")
    
    guardar_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                filetypes=[("Archivos CSV", "*.csv")],
                                                title="Guardar Reporte")
    if guardar_path:
        try:
            with open(guardar_path, 'w', newline='') as file:
                writer = csv.writer(file)
                for line in reporte:
                    writer.writerow([line])
            messagebox.showinfo("Guardado", f"Reporte guardado exitosamente en:\n{guardar_path}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el reporte.\nError: {str(e)}")

# Función para actualizar el setpoint desde la interfaz gráfica
def actualizar_setpoint():
    try:
        nuevo_setpoint = float(setpoint_entry.get())
        encontrar_maximos(nuevo_setpoint, ax1)  # Actualizar también en la gráfica principal (ax1)
        onselect(ax2.get_xlim()[0], ax2.get_xlim()[1])  # Actualizar en la gráfica ampliada (ax2)
    except ValueError:
        messagebox.showerror("Error", "Ingrese un valor numérico válido para el setpoint.")

# Crear la ventana principal
root = tk.Tk()
root.title("Generador de Gráficas")

# Crear un botón para seleccionar la carpeta de salida
seleccionar_carpeta_button = tk.Button(root, text="Seleccionar Carpeta", command=seleccionar_carpeta)
seleccionar_carpeta_button.pack()

# Variable para almacenar la ruta de la carpeta seleccionada
carpeta_var = tk.StringVar(root)

# Variable para almacenar el archivo seleccionado
archivo_var = tk.StringVar(root)

# Crear una lista desplegable con los nombres de los archivos
archivo_dropdown = tk.OptionMenu(root, archivo_var, "")
archivo_dropdown.pack()

# Crear un botón para cargar y mostrar los datos del archivo seleccionado
cargar_button = tk.Button(root, text="Generar Gráfica", command=cargar_archivo)
cargar_button.pack()

# Crear un campo de entrada para el setpoint
setpoint_label = tk.Label(root, text="Setpoint:")
setpoint_label.pack()

setpoint_entry = tk.Entry(root)
setpoint_entry.pack()

# Crear un botón para actualizar el setpoint
actualizar_setpoint_button = tk.Button(root, text="Actualizar Setpoint", command=actualizar_setpoint)
actualizar_setpoint_button.pack()

# Crear un botón para generar el reporte
generar_reporte_button = tk.Button(root, text="Generar Reporte", command=guardar_reporte)
generar_reporte_button.pack()

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

x_global = []
y_global = []

root.mainloop()
