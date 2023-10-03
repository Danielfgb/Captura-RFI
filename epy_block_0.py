###################################################################################################

# import numpy as np
# import csv
# from gnuradio import gr

# class CSVWriterBlock(gr.sync_block):
#     def __init__(self, filename="output.csv"):
#         gr.sync_block.__init__(
#             self,
#             name="CSV Writer Block",
#             in_sig=[(np.float32, 1024)],  # Tipo de datos de entrada (float) y tamaño de bloque (1024)
#             out_sig=None,
#         )
#         self.filename = filename
#         self.file = open(self.filename, "w", newline="")
#         self.writer = csv.writer(self.file)
#         self.writer.writerow(["Sample"])

#     def work(self, input_items, output_items):
#         data_array = input_items[0]
        
#         # Escribir los datos en el archivo CSV
#         self.writer.writerows(data_array)
        
#         # Devolver el número de elementos procesados
#         return len(input_items[0])

#     def stop(self):
#         # Cerrar el archivo CSV cuando se detenga el flujo
#         self.file.close()

###################################################################################################

# class CSVWriterBlock(gr.sync_block):
#     def __init__(self, filename="output.csv"):
#         gr.sync_block.__init__(
#             self,
#             name="CSV Writer Block",
#             in_sig=[(np.float32, 1024)],  # Tipo de datos de entrada (float) y tamaño de bloque (1024)
#             out_sig=None,
#         )
#         self.filename = filename
#         self.file = open(self.filename, "w", newline="")
#         self.writer = csv.writer(self.file)

#     def work(self, input_items, output_items):
#         data_array = input_items[0]

#         # Utilizar NumPy para organizar los datos en filas
#         data_array = data_array.reshape(-1, 1)
        
#         # Escribir los datos en el archivo CSV
#         self.writer.writerows(data_array.tolist())
        
#         # Devolver el número de elementos procesados
#         return len(input_items[0])

#     def stop(self):
#         # Cerrar el archivo CSV cuando se detenga el flujo
#         self.file.close()

###################################################################################################

# import csv
# import numpy as np
# from gnuradio import gr
# import time
# import pmt

# class CSVWriterBlock(gr.sync_block):
    
#     def __init__(self, filename="output.csv"):
#         gr.sync_block.__init__(
#             self,
#             name="CSV Writer Block",
#             in_sig=[(np.float32, 1024)],  # Tipo de datos de entrada (float) y tamaño de bloque (1024)
#             out_sig=None,
#         )
#         self.filename = filename
#         self.file = open(self.filename, "w", newline="")
#         self.writer = csv.writer(self.file)
        
#         # Registrar la entrada de mensajes
#         self.message_port_register_in(pmt.intern("Frec_in"))
#         self.set_msg_handler(pmt.intern("Frec_in"), self.handle_message)

#     def handle_message(self, msg):
#         # Procesar el mensaje asíncrono y almacenar los datos en la variable 
#         self.message_data = pmt.to_python(msg)
#         print("Mensaje recibido:", self.message_data)


#     def work(self, input_items, output_items):
#         data_array = input_items[0]

#         # Verificar si hay un mensaje y procesarlo si existe
#         if hasattr(self, 'message_data'):
#             #print("Mensaje almacenado en handle_message:", self.message_data)
   
#             freq_value = self.message_data.get('freq', None)
#             if freq_value is not None:
#                 print("Valor numérico de frecuencia:", freq_value)

#             self.Frec_central = self.message_data

#         # Utilizar NumPy para organizar los datos en filas
#         data_array = data_array.reshape(-1, 1)

#         # Escribir los datos en el archivo CSV
#         self.writer.writerows(data_array.tolist())

#         # Devolver el número de elementos procesados
#         return len(input_items[0])

#     def stop(self):
#         # Cerrar el archivo CSV cuando se detenga el flujo
#         self.file.close()

####################################### prueba con cambio a valor flotante y que solo imprima si cambia ################# falta añadir lo de las frecuencias que estan en el otro codigo y cambiarlo a la otra columna 
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

        # Utilizar NumPy para organizar los datos en filas
        data_array = data_array.reshape(-1, 1)

        # Escribir los datos en el archivo CSV
        self.writer.writerows(data_array.tolist())

        # Devolver el número de elementos procesados
        return len(input_items[0])

    def stop(self):
        # Cerrar el archivo CSV cuando se detenga el flujo
        self.file.close()
