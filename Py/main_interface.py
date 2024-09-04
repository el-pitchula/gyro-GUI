import serial
import threading
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from vpython import canvas, box, vector, rate

# Configurações da porta serial
ser = serial.Serial('COM3', 115200, timeout=1)

# Interface gráfica principal
class MPU6050Interface(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("MPU6050 Interface")
        self.geometry("1000x600")

        # Elementos da interface
        self.create_widgets()

        # Thread para atualização da interface
        self.update_thread = threading.Thread(target=self.update_data)
        self.update_thread.daemon = True
        self.update_thread.start()

    def create_widgets(self):
        # Frame para o Serial Plotter
        self.plot_frame = ttk.LabelFrame(self, text="Serial Plotter")
        self.plot_frame.place(relx=0.05, rely=0.05, relwidth=0.4, relheight=0.4)

        # Matplotlib figure
        self.fig, self.ax = plt.subplots()
        self.ax.set_ylim([-32768, 32768])
        self.ax.set_title("MPU6050 Serial Plotter")
        self.line_accel, = self.ax.plot([], [], 'r-', label="Accel")
        self.line_gyro, = self.ax.plot([], [], 'b-', label="Gyro")
        self.ax.legend()

        self.canvas_plot = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas_plot.get_tk_widget().pack(fill=tk.BOTH, expand=1)

        # Frame para dados brutos da Serial
        self.serial_frame = ttk.LabelFrame(self, text="Dados da Serial")
        self.serial_frame.place(relx=0.5, rely=0.05, relwidth=0.4, relheight=0.4)

        self.serial_text = tk.Text(self.serial_frame, height=15, width=50)
        self.serial_text.pack(fill=tk.BOTH, expand=1)

        # Frame para a visualização 3D
        self.vpython_frame = ttk.LabelFrame(self, text="Visualização 3D")
        self.vpython_frame.place(relx=0.05, rely=0.5, relwidth=0.9, relheight=0.4)

        self.canvas_vpython = canvas(width=600, height=400)
        self.model = box(length=1, height=0.1, width=2)

    def update_data(self):
        accel_data = []
        gyro_data = []

        while True:
            line = ser.readline().decode('utf-8').strip()
            if line:
                # Exibir dados na interface
                self.serial_text.insert(tk.END, line + "\n")
                self.serial_text.see(tk.END)

                if "Accel:" in line:
                    data = line.split()
                    ax = int(data[1])
                    ay = int(data[2])
                    az = int(data[3])
                    gx = int(data[5])
                    gy = int(data[6])
                    gz = int(data[7])

                    # Atualizar Serial Plotter
                    accel_data.append(ax)
                    gyro_data.append(gx)
                    if len(accel_data) > 100:
                        accel_data.pop(0)
                        gyro_data.pop(0)

                    self.line_accel.set_data(range(len(accel_data)), accel_data)
                    self.line_gyro.set_data(range(len(gyro_data)), gyro_data)
                    self.ax.relim()
                    self.ax.autoscale_view()
                    self.canvas_plot.draw()

                    # Atualizar modelo 3D
                    self.model.axis = vector(ax/32768, ay/32768, az/32768)
                    rate(50)

if __name__ == "__main__":
    app = MPU6050Interface()
    app.mainloop()
