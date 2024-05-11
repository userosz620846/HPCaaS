from ast import arg
import csv
import os
import socket
import struct
import time
import webbrowser
import PySimpleGUI as sg
from itertools import cycle
import sys
import threading as thd





global s_ip

##
# This function will send a request to create the cluster along with the first job and dataset to the server
##
def send_cluster_dataset(sct, RG, CR, NW, ALG, ERG, file_path):

        # Read the file content
            
        with open(file_path, 'r') as csvfile:
            reader = csv.reader(csvfile)
            matrix = []
            for row in reader:
                matrix.append([float(x) for x in row])

        # Convert the matrix to a string
        file_content = '\n'.join([' '.join([str(x) for x in row]) for row in matrix]) 

        # Pack the data: 5 integers followed by the file content
        data = struct.pack("iiiii{}s".format(len(file_content.encode())), RG, CR, NW, ALG, ERG, file_content.encode())

        data = b"NEW:"+data
        # Send the data to the server
        sct.sendall(data)
        time.sleep(0.2)
        sct.send("END".encode())
        print("Dataset sent successfully!")

##
# This function sends a new job (along with the dataset) to the server
##
def send_job(sct, ALG, ERG, file_path):
    try:

        # Read the file content
        with open(file_path, 'r') as csvfile:
            reader = csv.reader(csvfile)
            matrix = []
            for row in reader:
                matrix.append([float(x) for x in row])
        
        file_content = '\n'.join([' '.join([str(x) for x in row]) for row in matrix]) 
        
        # Pack the data: 2 integers followed by the file content
        data = struct.pack("ii{}s".format(len(file_content)), ALG, ERG, file_content.encode())

        data = b"JOB:"+data
        # Send the data to the server
        sct.sendall(data)
        time.sleep(0.2)
        sct.send("END".encode())
        print("Dataset sent successfully!")

    except Exception as e:
        print(f"Error sending dataset: {e}")

##
# this function sends request to add a number of workers to the cluster in the spicified resource group
##
def add_worker(sct, RG, CR, NW):
    try:

        # Pack the data: 3 integers followed by the file content
        data = struct.pack("iii", RG, CR, NW)
        data = b"ADD:"+data
        # Send the data to the server
        sct.sendall(data)
        print("Request to add worker was sent...")


    except Exception as e:
        print(f"Error sending dataset: {e}")

def delete_cluster(sct):
    sct.send("DLT".encode())
    

##
# This function is the target of a thread, which will listen to logs and files and update the window accodingly
##
def handler(sct, window):
    global s_ip
    on = False
    print("listening for logs and files.......")
    while True:
                data = sct.recv(1024).decode("utf-8")
                if not data or data == 'q':
                    break
                else:
                    print(f"Received log entry from client: {data}")
                    window.refresh()
                    if data.startswith("LOG:"):
                        log_entry = data[4:]  # Extract the log message
                        print(f"Received log entry from client: {log_entry}")
                        window["-LOG_CONSOLE-"].print(log_entry, end="\n", text_color="black")
                        window.refresh()
                    # And refresh the window: window.refresh()
                    elif data.startswith("FILE:"):
                        file_content = data[5:]  # Extract the file content
                        # Process the file content (e.g., save it to a file)
                        with open("YAY!.csv", "w", newline="") as csvfile:
                            writer = csv.writer(csvfile)
                            print("reading file.......")
                            for row in file_content.splitlines():
                                writer.writerow(row.split(",")) 
                        print("Received output file content")
                    elif data.startswith("IP:"):
                        s_ip = data[3:]
                        window["-DASHBOARD_LINK-"].update(s_ip+":8787")
                    elif data.startswith("ON"):
                        on=True
                        window["-ADD_WORKER_NUM-"].update(visible=True)
                        window["-ADD_WORKER_TEXT-"].update(visible=True)
                        window["-ADD_WORKER-"].update(visible=True)
                        window["-ADD_WORKER_TEXT2-"].update(visible=True)
                        window["-ADD_WORKER_RG-"].update(visible=True)
                        window["-ADD_WORKER_LINE-"].update(visible=True)
                        window["-ADD_WORKER_LINE2-"].update(visible=True)
                        window["-KILL-"].update(visible=True)
                        window["Submit New Job"].update(visible= True)
                        window["Create Cluster & Submit Job"].update(visible= False)
                        window["Open Dashboard"].update(visible= True)
                    
##
# this small function will create the items in the resource group selection list
##
def create_resource_group_options(num_resource_groups):
    # Generate resource group options based on user input
    if num_resource_groups == 0:
        return "ALL"
    else:
        return [f"RG{i}" for i in range(1, num_resource_groups + 1)]

##
# this function will open and handle the interations in the second window
##
def open_second_window(RG,CR,NW, sct):
    
    global s_ip
    layout = [
        [sg.Text("Choose Resource Group:")],
        [sg.InputCombo(create_resource_group_options(RG), key="-RESOURCE_GROUP-")],
        [sg.Text("Upload Dataset:")],
        [sg.InputText(key="-DATASET_PATH-", disabled=True), sg.FileBrowse("Browse", key="-DATASET_BROWSE-")],
        [sg.Text("Dashboard Link:")],
        [sg.Text(key="-DASHBOARD_LINK-",text="pending cluster creation.."), sg.Button("Open Dashboard",visible=False)],
        [sg.Text("Choose Algorithm:")],
        [sg.Combo(["1) Row-Wise Sum", "2) Row-Wise Average", "3) Row_wise Max"], key="-ALGORITHM-")],
        [sg.Button("Create Cluster & Submit Job"),[sg.Button("Submit New Job" , visible=False)]],
        [[sg.Text("-----------------------------------------------------",key="-ADD_WORKER_LINE-",visible=False)]],
        [[sg.Text("Number of workers to add:", visible=False,key="-ADD_WORKER_TEXT-")],[sg.Slider(key="-ADD_WORKER_NUM-", orientation='h', visible=False)],
         [sg.Text("to which resource group?:", visible=False,key="-ADD_WORKER_TEXT2-")],
         [sg.InputCombo(create_resource_group_options(RG), key="-ADD_WORKER_RG-",visible=False)],[sg.Button("Add Workers", key="-ADD_WORKER-", visible=False)],
        [[sg.Text("-----------------------------------------------------",key="-ADD_WORKER_LINE2-",visible=False)]],
        [[sg.Button("DELETE Cluster", key="-KILL-", visible=False)]],
        [sg.Multiline(size=(40, 10), key="-LOG_CONSOLE-")]
    ]]

    window = sg.Window("Manage Cluster", layout, finalize=True)
    
    
    thd.Thread(target=handler,args=(sct, window)).start()
    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED:
            break
        elif event == "-ADD_WORKER-":
            
            if RG == 0:
                A_RG = 0
            else:
                A_RG = int(values["-ADD_WORKER_RG-"][2])
            A_NW = int(values["-ADD_WORKER_NUM-"])

            thd.Thread(target=add_worker,args=(sct, A_RG, CR, A_NW)).start()
            
                
        elif event == "Open Dashboard":

            webbrowser.open("http://"+s_ip+":8787/status")
        elif event == "-KILL-":
            sg.popup_auto_close("your cluster is deleted ... thank you.", auto_close_duration=3)
            window.close()
            delete_cluster(client_socket)
        elif event == "Create Cluster & Submit Job":
           
            ALG = int(values["-ALGORITHM-"][0])
            # ALG = 1
            if (RG==0):
                ERG=0
            else:
                ERG = int(values["-RESOURCE_GROUP-"][2])
            # ERG = 1
            
            file_path = values["-DATASET_PATH-"]
            send_cluster_dataset(sct, RG, CR, NW, ALG, ERG,file_path)
 
            thd.Thread(target=handler,args=(sct, window)).start()

           
           
            sg.popup_auto_close("Job submitted. Waiting for results...", auto_close_duration=2)
    
        elif event == "Submit New Job":

            ALG = int(values["-ALGORITHM-"][0])
            if (RG==0):
                ERG=0
            else:
                ERG = int(values["-RESOURCE_GROUP-"][2])
            
            file_path = values["-DATASET_PATH-"]
            send_job(sct, ALG, ERG,file_path)
            

##
# This funciton will open and handle the interacitons in the first window
##
def main_window(sct):
    sg.theme("LightGrey1")

    # Layout
    layout = [
        [[sg.Text("Configure Cluster", font=("Helvetica", 16))],
        [sg.Checkbox("Custom Scheduling", key="-CUSTOM_SCHEDULING-", enable_events=True)],
        [sg.Text("Resource Groups:", visible=False,key="-RG_TEXT-"), sg.Slider(key="-RESOURCE_GROUPS-", orientation='h', visible=False)],
        [sg.Text("Cloud Region:"), sg.InputCombo(["Region A", "Region B", "Region C"], key="-CLOUD_REGION-")],
        [sg.Text("Number of Workers:",  visible=True,key="-SL_TEXT-"), sg.Slider(key="-SCALING_LIMIT-", orientation='h', visible=True)],
        [sg.Button("Next")]]
    ]

    # Create the window
    window = sg.Window("HPC as a Service Platform", layout, finalize=True)
        
    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED:
            break
        elif event == "-CUSTOM_SCHEDULING-":
            window["-RG_TEXT-"].update(visible= values["-CUSTOM_SCHEDULING-"])
            window["-RESOURCE_GROUPS-"].update(visible= values["-CUSTOM_SCHEDULING-"])
        elif event == "Next":
            if(values["-CUSTOM_SCHEDULING-"]):

                RG = int(values["-RESOURCE_GROUPS-"])
            else:

                RG = 0
                

            NW = int(values["-SCALING_LIMIT-"])

            CR = values["-CLOUD_REGION-"]
            if(CR =="Region A"):
                CR = 1
            elif (CR == "Region B"):
                CR = 2
            elif ((CR == "Region C")):
                CR = 3 

            
            
            open_second_window(RG,CR,NW,sct)
            break
            

    window.close()

if __name__ == "__main__":

    print("trying to connect with server...")
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("localhost", 9999))
    data = client_socket.recv(1024).decode("utf-8")
    client_socket.close()
    ID = int(data)
    port = ID
    sct = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    time.sleep(0.5)
    sct.connect(("localhost", port))
    print("\nestablished didicated connection with server!")
    main_window(sct)

