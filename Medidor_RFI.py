import os
import sys
import subprocess
import threading
import shutil
from tkinter import Tk, Button, Label, filedialog, messagebox

def run_gnu_radio():
    carpeta_destino = filedialog.askdirectory(title="Seleccionar carpeta de destino")
    if carpeta_destino:
        # Ruta del archivo de GNU Radio en el mismo directorio que este script
        archivo_gnu_radio = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Captura_RFI_1.0.grc')
        
        if os.path.exists(archivo_gnu_radio):
            # Copiar el archivo a la carpeta seleccionada
            destino = os.path.join(carpeta_destino, 'Captura_RFI_1.0.grc')
            shutil.copy(archivo_gnu_radio, destino)
            messagebox.showinfo("Éxito", f"Archivo {archivo_gnu_radio} copiado a {destino}")
        else:
            messagebox.showerror("Error", f"No se encontró el archivo {archivo_gnu_radio}")

def run_tratado_datos(ruta_archivo_csv):
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Tratado_Datos.py')
    
    if not os.path.exists(script_path):
        messagebox.showerror("Error", f"No se encontró el script Tratado_Datos.py en {script_path}")
        return

    def run_script():
        try:
            if sys.platform.startswith('win'):
                # Windows
                cmd = f'start /wait cmd /c "{sys.executable} {script_path} {ruta_archivo_csv}"'
            else:
                # macOS / Linux
                cmd = f'xterm -hold -e "{sys.executable} {script_path} {ruta_archivo_csv}"'
            subprocess.run(cmd, shell=True)
            messagebox.showinfo("Éxito", "Tratamiento de datos completado.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al ejecutar Tratado_Datos.py: {e}")

    threading.Thread(target=run_script).start()
    messagebox.showinfo("Información", "Tratamiento de datos en progreso. Por favor espera...")

def select_csv_and_run_tratado():
    ruta_archivo_csv = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if ruta_archivo_csv:
        run_tratado_datos(ruta_archivo_csv)

def run_visualizacion():
    script_visualizacion = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Visualizacion_Datos.py")
    subprocess.Popen([sys.executable, script_visualizacion])

def install_gnu_radio():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ruta_instalador_gnu_radio = os.path.join(script_dir, "GNU_Radio_installer.exe")
    
    if os.path.exists(ruta_instalador_gnu_radio):
        subprocess.Popen(ruta_instalador_gnu_radio, cwd=script_dir)
    else:
        messagebox.showerror("Error", "No se encontró el instalador de GNU Radio.")

root = Tk()
root.title("Interfaz de Control")

texto_explicativo = """Esta interfaz permite controlar diferentes funciones:
- 'Instalar GNU' inicia el instalador de GNU Radio si no está instalado.
- Utiliza el botón 'GNU' para copiar el archivo Captura_RFI_1.0.grc a una carpeta seleccionada.
- El botón 'Pos-procesamiento' ejecuta Tratado_Datos.py en un archivo CSV seleccionado.
- 'Visualización' abre Visualizacion_Datos.py.
"""
lbl_explicativo = Label(root, text=texto_explicativo, justify="left", padx=10, pady=10)
lbl_explicativo.pack()

root.geometry("600x300")  # Ancho x Alto

btn_install_gnu = Button(root, text="Instalar GNU", command=install_gnu_radio)
btn_install_gnu.pack(pady=10)

btn_gnu = Button(root, text="GNU", command=run_gnu_radio)
btn_gnu.pack(pady=10)

btn_tratado = Button(root, text="Pos-procesamiento", command=select_csv_and_run_tratado)
btn_tratado.pack(pady=10)

btn_visualizacion = Button(root, text="Visualización", command=run_visualizacion)
btn_visualizacion.pack(pady=10)

root.mainloop()
