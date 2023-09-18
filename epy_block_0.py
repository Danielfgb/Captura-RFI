
import numpy as np
from gnuradio import gr

class blk(gr.sync_block):
    """Embedded Python Block example - guarda datos en archivo CSV"""

    def __init__(self, filename="output.csv"):
        """arguments to this function show up as parameters in GRC"""
        gr.sync_block.__init__(
            self,
            name='Embedded Python Block',  # will show up in GRC
            in_sig=[(np.float32, 1024)],
            out_sig=None  # no output
        )
        self.filename = filename
        self.data = []  # Lista para almacenar los datos recibidos

    def work(self, input_items, output_items):
        """Guarda los datos recibidos en la lista data"""
        self.data.extend(input_items[0])
        return len(input_items[0])

    def stop(self):
        """Al detener el flujo, guarda los datos en el archivo CSV"""
        np.savetxt(self.filename, self.data, delimiter=',')
        return True



