import csv
import numpy as np
from gnuradio import gr
import pmt

class CSVWriterBlock(gr.sync_block):
    
    def __init__(self, filename="output.csv"):
        gr.sync_block.__init__(
            self,
            name="CSV Writer Block",
            in_sig=[(np.float32, 1024)],  # Tipo de datos de entrada (float) y tamaño de bloque (1024)
            out_sig=None,
        )
        self.filename = filename
        self.file = open(self.filename, "w", newline="")
        self.writer = csv.writer(self.file)
        self.prev_freq_value = None  # Valor de frecuencia anterior
        self.header_written = False  # Variable para rastrear si se ha escrito el encabezado

        # Registrar la entrada de mensajes
        self.message_port_register_in(pmt.intern("Frec_in"))
        self.set_msg_handler(pmt.intern("Frec_in"), self.handle_message)

    def handle_message(self, msg):
        # Procesar el mensaje asíncrono y almacenar los datos numéricos
        message_data = pmt.to_python(msg)
        freq_value = message_data.get('freq', None)

        if freq_value is not None:
            freq_value = float(freq_value)  # Convertir a float
            if self.prev_freq_value is None or freq_value != self.prev_freq_value:
                self.prev_freq_value = freq_value
                print("Valor numérico de frecuencia:", freq_value)

    def work(self, input_items, output_items):
        data_array = input_items[0]

        # Verificar si se ha escrito el encabezado y escribirlo si no
        if not self.header_written:
            self.writer.writerow(["Frecuencia (Hz)", "dB"])
            self.header_written = True

        # Verificar si hay un mensaje y obtener el valor de frecuencia si existe
        freq_value = None
        if hasattr(self, 'prev_freq_value'):
            freq_value = self.prev_freq_value

        # Utilizar NumPy para organizar los datos en filas
        data_array = data_array.reshape(-1, 1)

        # Crear una columna de valores de frecuencia
        if freq_value is not None:
            freq_column = np.full((len(data_array), 1), freq_value, dtype=np.float32)
        else:
            freq_column = np.full((len(data_array), 1), np.nan, dtype=np.float32)  # Si no hay frecuencia, llenar con NaN

        # Combinar los valores de frecuencia y los datos en una sola matriz
        combined_data = np.hstack((freq_column, data_array))

        # Escribir los datos combinados en el archivo CSV
        self.writer.writerows(combined_data.tolist())

        # Devolver el número de elementos procesados
        return len(input_items[0])

    def stop(self):
        # Cerrar el archivo CSV cuando se detenga el flujo
        self.file.close()
