from time import sleep
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import socket
import queue 
import msvcrt

class monitor:
    def __init__(self, timestep, samples = 50, y_label = 'Value'):
        self.x_vec = np.linspace(-samples*timestep ,-timestep, samples)
        self.timestep = timestep
        self.samples = samples
        self.curve_legends = []
        self.curve_getters = []
        self.curves = []
        plt.ion()
        self.fig = plt.figure(figsize=(13,6))
        self.ax = self.fig.add_subplot(111)
        self.hists = []        
        self.curve_colors = ['b','g','r','c','m','y']
        self.y_label = y_label
        

    def addCurve(self, c_name, c_getter):
        self.curve_getters.append(c_getter)
        self.curve_legends.append(c_name)

        y_hist = queue.Queue()
        for i in range(self.samples):
            y_hist.put(0)
        self.hists.append(y_hist)

        y_vec = np.zeros(self.samples)
        curve_, = self.ax.plot(self.x_vec, y_vec, self.curve_colors[len(self.curves)])
        self.curves.append(curve_)

    def start(self):
        plt.xlabel('Time [s]')
        plt.ylabel(self.y_label)
        plt.title('Monitor')
        plt.show()
        plt.grid()
        plt.legend(self.curve_legends)

    def update(self):
        for curve_n in range(len(self.curves)):            
            self.hists[curve_n].get()
            n_value = self.curve_getters[curve_n]()
            self.hists[curve_n].put(n_value)
            y_vec = list(self.hists[curve_n].queue)
            self.curves[curve_n].set_ydata(y_vec)
            
        min_y = min([min(i.queue) for i in self.hists])
        max_y = max([max(i.queue) for i in self.hists])
        min_y = min(min_y , -1)
        max_y = max(max_y , 1)
        marg = 0.1*(max_y - min_y)
        
        plt.ylim([min_y-marg, max_y+marg])
        plt.pause(self.timestep)

    def stop(self):
        plt.ioff()
    
    def resume(self):
        plt.ion()


print("##########################")
print("ClipX Monitor")
print("##########################\n")

print("Access \"http://clipx/#/\" in your web browser to configure ClipX" )
IP = input("Enter ClipX IP Address : ")

PORT = 55000        # The port used by the server

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((IP, PORT))
s.sendall(b'SDO?x44f2,4 \r\n')
unit = s.recv(512).decode()[:-2]
def ClipxValue():        
        s.sendall(b'SDO?x44f0,4 \r\n')
        data = s.recv(512)
        return float(data)

g = monitor(0.1,70, y_label=unit)
g.addCurve('ClipX Value', ClipxValue)
g.start()
print("Reading data from ClipX... Press space to stop")
while 1:
    #Keeps updating the graph
    g.update()
    if msvcrt.kbhit():
        k = ord(msvcrt.getch())
        if  k == 32:
            print("Stopping")
            break        
        else:
            print("Press Space to stop")