import os
import shutil
import threading
from tkinter import Tk, Button, Label, filedialog, messagebox, ttk
import Tratado_Datos
import subprocess
from queue import Queue

class Application:
    def __init__(self, root):
        self.root = root
        self.root.title("Interfaz Medidor RFI")

        self.create_widgets()

    def create_widgets(self):

        texto_explicativo = """Esta interfaz permite controlar diferentes funciones:
        - 'Instalar GNU Radio' inicia el instalador de GNU Radio 3.10.8.0 si no está instalado.
        - Utiliza el botón 'Cargar Medidor de RF' para copiar el archivo Captura_RFI_1.0.grc a una carpeta seleccionada.
        - El botón 'Post-procesamiento' organiza y procesa los datos del archivo CSV generado por el medidor de RFI.
        - 'Visualización y Reporte' permite visualizar los datos procesados y generar un reporte con los datos relevantes.
        """

        self.lbl_explicativo = Label(self.root, text=texto_explicativo, justify="left", padx=10, pady=10)
        self.lbl_explicativo.pack()

        self.btn_install_gnu = Button(self.root, text="Instalar GNU Radio", command=self.install_gnu_radio)
        self.btn_install_gnu.pack(pady=10)

        self.btn_gnu = Button(self.root, text="Cargar Medidor de RF", command=self.run_gnu_radio)
        self.btn_gnu.pack(pady=10)

        self.btn_tratado = Button(self.root, text="Post-procesamiento", command=self.select_csv_and_run_tratado)
        self.btn_tratado.pack(pady=10)

        self.btn_visualizacion = Button(self.root, text="Visualización y Reporte", command=self.run_visualizacion)
        self.btn_visualizacion.pack(pady=10)

    def run_gnu_radio(self):
        carpeta_destino = filedialog.askdirectory(title="Seleccionar carpeta de destino")
        if carpeta_destino:
            archivo_gnu_radio = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Captura_RFI_1.0.grc')
            
            if os.path.exists(archivo_gnu_radio):
                destino = os.path.join(carpeta_destino, 'Captura_RFI_1.0.grc')
                shutil.copy(archivo_gnu_radio, destino)
                messagebox.showinfo("Éxito", f"Archivo {archivo_gnu_radio} copiado a {destino}")
            else:
                messagebox.showerror("Error", f"No se encontró el archivo {archivo_gnu_radio}")

    def run_tratado_datos(self, ruta_archivo_csv, carpeta_salida):
        try:
            
            carpeta_entrada = os.path.dirname(ruta_archivo_csv)       
            nombre_archivo_base = os.path.splitext(os.path.basename(ruta_archivo_csv))[0]
            carpeta_salida_completa = os.path.join(carpeta_entrada, f'{carpeta_salida}_{nombre_archivo_base}')

            Tratado_Datos.main(ruta_archivo_csv, carpeta_salida_completa, 1024)
            self.progress_queue.put("Éxito")
        except Exception as e:
            self.progress_queue.put(f"Error: {e}")

    def handle_progress(self):
        message = self.progress_queue.get()
        if message == "Éxito":
            if hasattr(self, 'progress_window') and self.progress_window:
                self.progress_window.destroy()
            messagebox.showinfo("Éxito", "Tratamiento de datos completado.")
        else:
            if hasattr(self, 'progress_window') and self.progress_window:
                self.progress_window.destroy()
            messagebox.showerror("Error", f"Error al ejecutar Tratado_Datos.py: {message}")

    def update_progress(self):
        if hasattr(self, 'progress_bar') and self.progress_bar:
            self.progress_bar.stop()
            self.progress_bar.destroy()
            self.progress_bar = None
        if hasattr(self, 'progress_label') and self.progress_label:
            self.progress_label.destroy()
            self.progress_label = None

    def select_csv_and_run_tratado(self):
        ruta_archivo_csv = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if ruta_archivo_csv:
            self.progress_queue = Queue()

            self.progress_window = Tk()
            self.progress_window.title("Progreso")
            self.progress_window.geometry("300x100")

            self.progress_label = Label(self.progress_window, text="Procesando datos...")
            self.progress_label.pack(pady=10)

            self.progress_bar = ttk.Progressbar(self.progress_window, length=200, mode='indeterminate')
            self.progress_bar.pack(pady=10)
            self.progress_bar.start()

            # Nombre base de la carpeta de salida
            carpeta_salida = 'Muestra'

            threading.Thread(target=self.run_tratado_datos, args=(ruta_archivo_csv, carpeta_salida)).start()
            self.check_progress()

    def check_progress(self):
        self.root.after(100, self.check_progress)
        while not self.progress_queue.empty():
            self.update_progress()
            self.handle_progress()

    def run_visualizacion(self):

        import Visualizacion_Datos
        Visualizacion_Datos.main()

    def install_gnu_radio(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        ruta_instalador_gnu_radio = os.path.join(script_dir, "GNU_Radio_installer.exe")
        
        if os.path.exists(ruta_instalador_gnu_radio):
            subprocess.Popen(ruta_instalador_gnu_radio, cwd=script_dir)
        else:
            messagebox.showerror("Error", "No se encontró el instalador de GNU Radio.")

if __name__ == "__main__":
    root = Tk()
    app = Application(root)
    root.mainloop()