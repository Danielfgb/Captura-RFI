import numpy as np
from gnuradio import gr
import time
import pmt

class blk(gr.sync_block):
    """sending asynchronous messages"""

    def __init__(self, frec_inicial=100000000, frec_final=200000000, intervalo_tiempo=5, ancho_banda=20000000):
        
        gr.sync_block.__init__(
            self,
            name='Control frecuencia USRP',
            in_sig=None,  # No input signal
            out_sig=None  # No output signal
        )

        # DECLARA LAS VARIABLES INICIALES ||||| Frec_I1 = frec_ini + BW/2 ,  Frec_I2 = Frec_I1 + BW ..... Frec_Fn = Frec_In-1 + BW/2 || if (Frec_Fn == frec_final) = Frec_Fn = Frec_I1

        self.Val_frec = True

        self.frec_inicial = (frec_inicial) + (ancho_banda/2)
        self.frec_final = frec_final
        self.intervalo_tiempo = intervalo_tiempo
        self.intervalo_cambio = ancho_banda

        self.frec_cambio = (frec_inicial) + (ancho_banda/2)

        # Configurar el puerto de mensajes
        self.message_port_register_out(pmt.intern("Frec_out"))

        # Iniciar el hilo del remitente del mensaje
        self.msg_thread = MsgSenderThread(self)
        self.msg_thread.start()

    def send_message(self):

        if self.Val_frec:                      
            self.frec_cambio = self.frec_inicial
            self.Val_frec = False

        # Calcula el nuevo valor de frecuencia
        self.frec_inicial += self.intervalo_cambio       

        # Si la frecuencia supera el valor final, vuelve a iniciar desde el valor inicial
        if (self.frec_inicial) >= (self.frec_final):
            self.frec_inicial = self.frec_cambio
            self.Val_frec = True

        # Crear el diccionario freq_msg
        freq_msg = {'freq': self.frec_inicial}

        # Enviar freq_msg como un mensaje asincrónico
        msg = pmt.to_pmt(freq_msg)
        self.message_port_pub(pmt.intern("Frec_out"), msg)

        return (self.frec_inicial)

    def stop(self):
        self.msg_thread.stop()
        self.msg_thread = None

    def msg_handler(self, msg):
        if pmt.is_eq(msg, pmt.intern("msg_send")):
            self.send_message()

class MsgSenderThread(gr.threading.Thread):
    def __init__(self, block):
        gr.threading.Thread.__init__(self)
        self.block = block
        self.running = True

    def stop(self):
        self.running = False

    def run(self):
        while self.running:
            time.sleep(self.block.intervalo_tiempo)
            self.block.send_message()