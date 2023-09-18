
# import numpy as np
# from gnuradio import gr

# class blk(gr.sync_block):
#     """Embedded Python Block example - guarda datos en archivo CSV"""

#     def __init__(self, filename="output.csv"):
#         """arguments to this function show up as parameters in GRC"""
#         gr.sync_block.__init__(
#             self,
#             name='Embedded Python Block',  # will show up in GRC
#             in_sig=[(np.float32, 1024)],
#             out_sig=None  # no output
#         )
#         self.filename = filename
#         self.data = []  # Lista para almacenar los datos recibidos

#     def work(self, input_items, output_items):
#         """Guarda los datos recibidos en la lista data"""
#         self.data.extend(input_items[0])
#         return len(input_items[0])

#     def stop(self):
#         """Al detener el flujo, guarda los datos en el archivo CSV"""
#         np.savetxt(self.filename, self.data, delimiter=',')
#         return True

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

import csv
import numpy as np
from gnuradio import gr

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
