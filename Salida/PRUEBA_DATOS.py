import os
import tkinter as tk
from tkinter import ttk, filedialog
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import subprocess

# Función para cargar y graficar los datos
def plot_data(filename, start_idx, end_idx):
    data = pd.read_csv(filename)
    subset = data.iloc[start_idx:end_idx]

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(subset['Frecuencia (Hz)'], subset['dB'])
    ax.set_xlabel('Frecuencia (Hz)')
    ax.set_ylabel('dB')
    ax.set_title('Gráfico de datos')

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.grid(row=1, column=0, padx=10, pady=10)

# Función para actualizar el gráfico cuando se selecciona un archivo diferente
def update_plot(event):
    selected_file = os.path.join(folder_path, file_listbox.get(file_listbox.curselection()))
    update_slider_range(selected_file)
    plot_data(selected_file, 0, 1000)

# Función para actualizar el rango del slider en función de los datos del archivo CSV
def update_slider_range(file_path):
    data = pd.read_csv(file_path)
    max_value = len(data) - 1000 if len(data) > 1000 else 0
    slider.config(from_=0, to=max_value)
    slider.set(0)

# Función para ejecutar el archivo .py "realizar_muestra.py"
def execute_realizar_muestra():
    subprocess.run(["python", r"C:\Users\dfgom\OneDrive\Escritorio\USRP\RFI_Captura\Captura_RFI.py"])

# Carpeta que contiene los archivos CSV
folder_path = r'C:\Users\dfgom\OneDrive\Escritorio\USRP\RFI_Captura\Salida\Muestras'

# Crear la ventana principal
root = tk.Tk()
root.title("Visualizador de Datos CSV")

# Crear un marco para organizar widgets
frame = ttk.Frame(root)
frame.pack(padx=20, pady=20)

# Crear lista de archivos CSV en la carpeta
file_list = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
file_listbox = tk.Listbox(frame, height=len(file_list))
file_listbox.grid(row=0, column=0, padx=10, pady=10)
for filename in file_list:
    file_listbox.insert(tk.END, filename)

# Vincular el evento <<ListboxSelect>> para actualizar el gráfico al seleccionar un archivo
file_listbox.bind("<<ListboxSelect>>", update_plot)

# Crear un slider para navegar por los datos (inicialmente deshabilitado)
slider = tk.Scale(frame, from_=0, to=0, orient=tk.HORIZONTAL, length=400, state='disabled')
slider.grid(row=2, column=0, padx=10, pady=10)

# Crear botón "Realizar Muestra" para ejecutar el archivo .py
realizar_muestra_button = ttk.Button(frame, text="Realizar Muestra", command=execute_realizar_muestra)
realizar_muestra_button.grid(row=3, column=0, padx=10, pady=10)

# Iniciar la interfaz gráfica con el primer archivo
if file_list:
    initial_file = os.path.join(folder_path, file_list[0])
    update_slider_range(initial_file)
    plot_data(initial_file, 0, 1000)

# Iniciar la interfaz gráfica
root.mainloop()
