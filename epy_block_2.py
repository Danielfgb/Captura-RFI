import numpy as np
from gnuradio import gr
import csv
import matplotlib.pyplot as plt

class CSVWriterAndPlotBlock(gr.sync_block):

    def __init__(self, filename="output.csv", central_frequency=115000000, bandwidth=170000000, image_filename="data_plot.png"):

        gr.sync_block.__init__(
            self,
            name="CSV Writer and Plot Block",
            in_sig=[(np.float32, 1024)],
            out_sig=None,
        )
        self.filename = filename
        self.central_frequency = central_frequency
        self.bandwidth = bandwidth
        self.save_image = True
        self.image_filename = image_filename
        self.file = open(self.filename, "w", newline="")
        self.first_work_call = True
        self.writer = None
        self.fig, self.ax = plt.subplots()

    def work(self, input_items, output_items):
        """Write data to the CSV file and plot the data"""
        if self.first_work_call:
            self.writer = csv.writer(self.file)
            self.writer.writerow(["Frequency (Hz)", "dBs"])  # Write the header to the CSV file
            self.first_work_call = False

        data_array = input_items[0]

        data_array_transposed = np.transpose(data_array)

        num_samples = data_array_transposed.shape[0]
        frequencies = np.linspace(
            self.central_frequency - self.bandwidth / 2,
            self.central_frequency + self.bandwidth / 2,
            num_samples
        )

        data_with_freq = np.column_stack((frequencies, data_array_transposed))

        # Write CSV file
        self.writer.writerows(data_with_freq)

        frequencies_plot = data_with_freq[:, 0]
        data_plot = data_with_freq[:, 1]

        # Plot the data
        self.ax.clear()
        self.ax.plot(frequencies_plot, data_plot)
        self.ax.set_xlabel("Frequency (Hz)")
        self.ax.set_ylabel("dBs")
        self.ax.set_title("RFI")
        self.ax.grid(False)

        if self.save_image:
            plt.savefig(self.image_filename)

        return len(input_items[0])

    def stop(self):
        """Stop the block and close the CSV file"""
        self.file.close()
        #plt.show()  # Display the plot after processing is done