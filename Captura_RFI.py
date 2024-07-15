#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Captura RFI
# Author: Daniel Gomez
# GNU Radio version: 3.10.8.0

from PyQt5 import Qt
from gnuradio import qtgui
from gnuradio import blocks
from gnuradio import blocks, gr
from gnuradio import fft
from gnuradio.fft import window
from gnuradio import gr
from gnuradio.filter import firdes
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import uhd
import time
import Captura_RFI_CSV as CSV  # embedded python block
import Captura_RFI_Control_Frecuencia as Control_Frecuencia  # embedded python block
import sip



class Captura_RFI(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Captura RFI", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Captura RFI")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except BaseException as exc:
            print(f"Qt GUI: Could not set Icon: {str(exc)}", file=sys.stderr)
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "Captura_RFI")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 1000000
        self.frec_inicial = frec_inicial = 80000000
        self.frec_final = frec_final = 300000000
        self.Intervalo_Tiempo = Intervalo_Tiempo = 0.5

        ##################################################
        # Blocks
        ##################################################

        self.uhd_usrp_source_1 = uhd.usrp_source(
            ",".join(("", "")),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0,1)),
            ),
        )
        self.uhd_usrp_source_1.set_samp_rate(samp_rate)
        self.uhd_usrp_source_1.set_time_now(uhd.time_spec(time.time()), uhd.ALL_MBOARDS)

        self.uhd_usrp_source_1.set_center_freq(0, 0)
        self.uhd_usrp_source_1.set_antenna('RX2', 0)
        self.uhd_usrp_source_1.set_normalized_gain(1, 0)
        self.qtgui_vector_sink_f_0 = qtgui.vector_sink_f(
            1024,
            0,
            1.0,
            "Frecuencia MHz",
            "dB",
            "",
            1, # Number of inputs
            None # parent
        )
        self.qtgui_vector_sink_f_0.set_update_time(0.10)
        self.qtgui_vector_sink_f_0.set_y_axis((-140), 2)
        self.qtgui_vector_sink_f_0.enable_autoscale(False)
        self.qtgui_vector_sink_f_0.enable_grid(True)
        self.qtgui_vector_sink_f_0.set_x_axis_units("")
        self.qtgui_vector_sink_f_0.set_y_axis_units("")
        self.qtgui_vector_sink_f_0.set_ref_level(0)


        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_vector_sink_f_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_vector_sink_f_0.set_line_label(i, labels[i])
            self.qtgui_vector_sink_f_0.set_line_width(i, widths[i])
            self.qtgui_vector_sink_f_0.set_line_color(i, colors[i])
            self.qtgui_vector_sink_f_0.set_line_alpha(i, alphas[i])

        self._qtgui_vector_sink_f_0_win = sip.wrapinstance(self.qtgui_vector_sink_f_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_vector_sink_f_0_win)
        self.fft_vxx_0 = fft.fft_vcc(1024, True, window.blackmanharris(1024), True, 1)
        self.blocks_throttle2_0 = blocks.throttle( gr.sizeof_float*1024, 50000, True, 0 if "auto" == "auto" else max( int(float(0.1) * 50000) if "auto" == "time" else int(0.1), 1) )
        self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, 1024)
        self.blocks_nlog10_ff_0 = blocks.nlog10_ff(10, 1024, 0)
        self.blocks_multiply_const_xx_0 = blocks.multiply_const_cc(0.000976562, 1024)
        self.blocks_message_debug_0 = blocks.message_debug(True, gr.log_levels.info)
        self.blocks_complex_to_mag_squared_0 = blocks.complex_to_mag_squared(1024)
        self.Control_Frecuencia = Control_Frecuencia.blk(frec_inicial=frec_inicial, frec_final=frec_final, intervalo_tiempo=Intervalo_Tiempo, ancho_banda=samp_rate)
        self.CSV = CSV.CSVWriterBlock(Filename_csv="CSV_Salida")


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.Control_Frecuencia, 'Frec_out'), (self.CSV, 'Frec_in'))
        self.msg_connect((self.Control_Frecuencia, 'Frec_out'), (self.blocks_message_debug_0, 'print'))
        self.msg_connect((self.Control_Frecuencia, 'Frec_out'), (self.uhd_usrp_source_1, 'command'))
        self.connect((self.blocks_complex_to_mag_squared_0, 0), (self.blocks_nlog10_ff_0, 0))
        self.connect((self.blocks_multiply_const_xx_0, 0), (self.blocks_complex_to_mag_squared_0, 0))
        self.connect((self.blocks_nlog10_ff_0, 0), (self.blocks_throttle2_0, 0))
        self.connect((self.blocks_stream_to_vector_0, 0), (self.fft_vxx_0, 0))
        self.connect((self.blocks_throttle2_0, 0), (self.CSV, 0))
        self.connect((self.blocks_throttle2_0, 0), (self.qtgui_vector_sink_f_0, 0))
        self.connect((self.fft_vxx_0, 0), (self.blocks_multiply_const_xx_0, 0))
        self.connect((self.uhd_usrp_source_1, 0), (self.blocks_stream_to_vector_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "Captura_RFI")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.uhd_usrp_source_1.set_samp_rate(self.samp_rate)

    def get_frec_inicial(self):
        return self.frec_inicial

    def set_frec_inicial(self, frec_inicial):
        self.frec_inicial = frec_inicial
        self.Control_Frecuencia.frec_inicial = self.frec_inicial

    def get_frec_final(self):
        return self.frec_final

    def set_frec_final(self, frec_final):
        self.frec_final = frec_final
        self.Control_Frecuencia.frec_final = self.frec_final

    def get_Intervalo_Tiempo(self):
        return self.Intervalo_Tiempo

    def set_Intervalo_Tiempo(self, Intervalo_Tiempo):
        self.Intervalo_Tiempo = Intervalo_Tiempo
        self.Control_Frecuencia.intervalo_tiempo = self.Intervalo_Tiempo




def main(top_block_cls=Captura_RFI, options=None):

    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
