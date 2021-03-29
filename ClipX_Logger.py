import socket
import datetime
import msvcrt
import time
from tkinter.filedialog import asksaveasfilename
import plotly.graph_objects as go

print("##########################")
print("ClipX acquisition terminal")
print("##########################\n")

print("Access \"http://clipx/#/\" in your web browser to configure ClipX" )
IP = input("Enter ClipX IP Address : ")

PORT = 55000 

time_hist = []
torque_hist = []
start_time = time.time()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((IP, PORT))
print("Reading data from ClipX... Press space to stop")
s.sendall(b'SDO?x44f2,4 \r\n')
unit = s.recv(512).decode()[:-2]
while 1:    
    if msvcrt.kbhit():
        k = ord(msvcrt.getch())
        if  k == 32:
            print("Stopping")
            break        
        else:
            print("Press Space to stop")
            
    s.sendall(b'SDO?x44f0,4 \r\n')
    data = s.recv(1024)
    time_hist.append(time.time()-start_time)
    torque_hist.append(float(data))
    
s.close()
print(len(time_hist), "Values acquired")
print("Saving csv file")
formats = [('Comma Separated values', '*.csv'), ]
file_name = asksaveasfilename(filetypes=formats, title="Save logged data as...", defaultextension = formats, initialfile = ("Log at "+ datetime.datetime.now().strftime("%m-%d-%Y_%Hh%M")))
if file_name != '':
    f = open(file_name, "w")
    f.write("Timestamp (s) , Measurement (" + unit + ") \n")
    for i in range(len(time_hist)):
        f.write(str(time_hist[i]))
        f.write(",")
        f.write(str(torque_hist[i]))
        f.write(",\n")
    f.close()

print("Showing graph")
# Create traces
fig = go.Figure()
fig.add_trace(go.Scatter(x=time_hist, y=torque_hist,
    mode='lines',
    name='ClipX Measurement (' + unit + ')',
    ))

fig.update_layout(title="Log at "+ datetime.datetime.now().strftime("%m-%d-%Y_%Hh%M"),
                   xaxis_title='Time (s)',
                   yaxis_title='Measurement (' + unit + ')')

fig.show()


