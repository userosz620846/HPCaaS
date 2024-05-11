import csv
import socket
import struct
import numpy as np
import GCP_driver, Azure_driver
import paramiko
import distributed as dsd
import time
import threading as thd

global w_ips
global s_ip
global cloud
global s_id
w_ids = []
w_ips = []
global NWs
NWs = 0
server_ip = 'localhost'
server_port = 9999

##
# parces data recieved when first creating a cluster
##
def parce_data(data, ID):

    # Assuming the data format: 5 integers followed by the file content
    
    RG, CR, NW, ALG, ERG, file_content = struct.unpack("iiiii{}s".format(len(data) - 20), data)

    print(f"Received RG: {RG}")
    print(f"Received CR: {CR}")
    print(f"Received NW: {NW}")
    print(f"Received ALG: {ALG}")
    print(f"Received ERG: {ERG}")

    file_content = file_content.decode()
    # Convert the string back to a matrix
    matrix = [list(map(float, row.split())) for row in file_content.split('\n')]
    print(matrix[0])
    # Convert the matrix to a NumPy array
    matrix = np.array(matrix)

    
    # Write the matrix to a CSV file
    with open('received_data_'+str(ID)+'.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(matrix)


    return  RG, CR, NW, ALG, ERG

 

##
# parces data recieved when adding new workers
##
def parce_data2(data):

    try:
        
        RG,CR,NW = struct.unpack("iii", data)

        print(f"Received RG: {RG}")
        print(f"Received NW: {NW}")
        print(f"Received CR: {CR}")

        return  RG, CR, NW

    except Exception as e:
        print(f"Error handling client connection: {e}")


##
# parces data recieved when submitting a new job
##
def parce_data3(data, ID):



    # Assuming the data format: 2 integers followed by the file content
    
    ALG, ERG, file_content = struct.unpack("ii{}s".format(len(data) - 8), data)


    print(f"Received ALG: {ALG}")
    print(f"Received ERG: {ERG}")

    file_content = file_content.decode()
    
    matrix = [list(map(float, row.split())) for row in file_content.split('\n')]

    # Convert the matrix to a NumPy array
    matrix = np.array(matrix)

    
    # Write the matrix to a CSV file
    with open('received_data_'+str(ID)+'.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(matrix)
    
    
    print("data parcing is done!!!!!")
    return  ALG, ERG

##
# creates a cluster
##
def create_cluster(cloud, ID, sct, RG, NWs):
    
    w_ids = []
    w_ips = []

    ID = str(ID)
    if RG == 0:
        num_workers = NWs
    else:
        num_workers = NWs*RG
        Ws=NWs
        NWs = NWs*RG
    
    s_id = ID + "-s"
    
    print("Number of workers is .............."+str(num_workers))
    for i in range(num_workers):
        w_ids.append(ID + "-w" + str(i)) 

    #create scheduler and workers
    if cloud == "GCP":
        GCP_driver.create_vm(s_id)
        sct.send("LOG:Scheduler VM created.".encode("utf-8"))
        for w in w_ids:
            GCP_driver.create_vm(w)
            sct.send("LOG:Worker VM created".encode("utf-8"))
        s_ip = GCP_driver.get_ip(s_id)
        while s_ip=="":
                print("failed to get scheduler IP... trying again...")
                s_ip = GCP_driver.get_ip(s_id)
        print("Scheduler IP is: "+s_ip)
        sct.send(("LOG:Scheduler IP is: "+s_ip).encode("utf-8"))
        sct.send(("IP:"+s_ip).encode("utf-8"))
        for i, w in enumerate(w_ids):
            ip = GCP_driver.get_ip(w)
            while ip=="":
                print("failed to get worker IP... trying again...")
                ip = GCP_driver.get_ip(w)
            print("worker IP is:"+ip)
            sct.send(("LOG:Worker IP is: "+ip).encode("utf-8"))
            w_ips.append(ip)
    
    if cloud == "azure":
        Azure_driver.create_vm(s_id)
        sct.send("LOG:Scheduler VM created.".encode("utf-8"))
        for w in w_ids:
            Azure_driver.create_vm(w)
            sct.send("LOG:Worker VM created".encode("utf-8"))
        s_ip = Azure_driver.get_ip(s_id)
        print("Scheduler IP is: "+s_ip)
        sct.send(("IP:"+s_ip).encode("utf-8"))
        sct.send(("LOG:Scheduler IP is: "+s_ip).encode("utf-8"))
        for i, w in enumerate(w_ids):
            ip = Azure_driver.get_ip(w)
            w_ips.append(ip)
            print("worker IP is:"+ip)
            sct.send(("LOG:Worker IP is: "+ip).encode("utf-8"))
            time.sleep(2)
            
    
    #establish dask environment
    time.sleep(60)
    run_command(s_ip, "python3 -m dask scheduler")
    sct.send("LOG:initializing dask environment in scheduler".encode("utf-8"))
    time.sleep(60)

    if RG == 0:
            for w in w_ips:
                run_command(w, f"python3 -m dask worker {s_ip}:8786")

                time.sleep(10)
    else:
            worker_counter = 0
            for _ in range(1, RG+1):
                for __ in range(Ws):
                    w = w_ips[worker_counter]
                    run_command(w, f"python3 -m dask worker {s_ip}:8786 --resources \"RG={_}\"")
                    # thd.Thread(target=run_command, args=(w,f"python3 -m dask worker {s_ip}:8786 --resources \"RG={_}\"")).start()
                    worker_counter+=1
                    # run_command(w, f"python3 -m dask worker {s_ip}:8786 --resources {RG}")
                    time.sleep(10)
        
    
        
    sct.send("LOG:Cluster is online".encode("utf-8"))
    sct.send("ON".encode("utf-8"))
    
            
            
        
    return  s_ip, s_id, w_ips, w_ids

##
# This function adds a number of workers to the client cluster in the chosen RG
##
def add_workers(n, cloud, RG, ID, NWs, s_ip, w_ids):

    ID = str(ID)
    print("Scheduler IP to add worker to is: "+s_ip)
    print("Current NWs is: "+str(NWs))
    new_w_ids = []
    new_w_ips = []
    for i in range(n):
        new_w_ids.append(ID + "-w" + str(NWs))
        w_ids.append(ID + "-w" + str(NWs))
        NWs+=1
        
        

    #create additional workers
    if cloud == "GCP":
        for w in new_w_ids:
            GCP_driver.create_vm(w)
            time.sleep(5)
        for i, w in enumerate(new_w_ids):
            ip = GCP_driver.get_ip(w)
            while ip=="":
                print("failed to get worker IP... trying again...")
                ip = GCP_driver.get_ip(w)
            print("worker IP is:"+ip)
            new_w_ips.append(ip)
            w_ips.append(ip)
            time.sleep(2)

    if cloud == "azure":
        for w in new_w_ids:
            Azure_driver.create_vm(w)
        for i, w in enumerate(new_w_ids):
            ip = Azure_driver.get_ip(w)
            new_w_ips.append(ip)
            w_ips.append(ip)
            

    #establish dask environment
    time.sleep(60)
    for w in new_w_ips:
        print("sending command to: "+ w)
        if RG == 0:
            run_command(w, f"python3 -m dask worker {s_ip}:8786")
            run_command(w, f"python3 -m dask worker {s_ip}:8786")
            time.sleep(10)
        else:
            run_command(w, f"python3 -m dask worker {s_ip}:8786 --resources \"RG={RG}\"")
            run_command(w, f"python3 -m dask worker {s_ip}:8786 --resources \"RG={RG}\"")
            time.sleep(10)
    return NWs, w_ids
    
##
# this function reads the CPU utalization of a remote host.
##       
def get_cpu_util(ip): 

    user = 'goss4'
    key_file = 'id_rsa'

    # Create an SSH client
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Load your RSA private key
    private_key = paramiko.RSAKey(filename=key_file)

    # Connect using the private key
    client.connect(ip, username=user, pkey=private_key, allow_agent=False, look_for_keys=False)

    # Execute a command remotely (e.g., list files)
    stdin, stdout, stderr = client.exec_command("python3 -c \"import psutil; print(psutil.cpu_percent(interval=1))\"")

    # Print the output
    time.sleep(5)
    # Close the connection
    # print("command sent....")
    client.close()
    return stdout.read().decode()      
    
##
# this function sends a command to a remote host using SSH
##
def run_command( ip, command): 

    user = 'goss4'
    key_file = 'id_rsa'

    # Create an SSH client
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Load your RSA private key
    private_key = paramiko.RSAKey(filename=key_file)

    # Connect using the private key
    client.connect(ip, username=user, pkey=private_key, allow_agent=False, look_for_keys=False)

    # Execute a command remotely (e.g., list files)
    stdin, stdout, stderr = client.exec_command(command)

    # Print the output
    # print(stdout.read().decode())
    time.sleep(5)
    # Close the connection
    print("command sent....")
    print(command)
    # client.close()
    # print(stdout.read().decode())
    print("done......")

##
# Alternative function to run command. used for debugging only.
##
def run_command2(ip, command):
    time.sleep(5)
    
    user = 'goss4'
    key_file = 'id_rsa'

    # Create an SSH client
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Load your RSA private key
    private_key = paramiko.RSAKey(filename=key_file)

    # Connect using the private key
    client.connect(ip, username=user, pkey=private_key, allow_agent=False, look_for_keys=False)
    try:
        print("sending this command: "+command)
        stdin, stdout, stderr = client.exec_command(command)

    except Exception as e:
        print(f"Error: {e}")


##
# This function will submit a new job to the cluster and return the result
##
def submit_jobs(ALG, ERG, s_ip, ID):
    client = dsd.Client(s_ip+":8786")
   
    csv_file_path = 'received_data_'+str(ID)+'.csv'

    # Initialize an empty list to store the rows
    futures = []
    line = np.empty((0,))
    
    with open(csv_file_path, 'r') as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            line = np.empty((0,))
            for _ in row:
                line = np.append(line, float(_))
            # line = da.from_array(line, row)
            print("job sent")
            if ERG == 0:
                if ALG==1:
                    futures.append(client.submit(np.sum, line))
                elif ALG==2:
                    futures.append(client.submit(np.mean, line))
                elif ALG==3:
                    futures.append(client.submit(np.max, line))
            else:
                if ALG==1:
                    futures.append(client.submit(np.sum, line,resources={"RG": ERG}))
                elif ALG==2:
                    futures.append(client.submit(np.mean, line,resources={"RG": ERG}))
                elif ALG==3:
                    futures.append(client.submit(np.max, line,resources={"RG": ERG}))
    
    result = np.empty((0,))
    for future in futures:
        result = np.append(result, future.result())
        
    return result
            
            
            



    
##
# This function will delete the cluster
##
def delete_cluster(cloud, s_id, w_ids):
 
    print("inside delet_Cluster !!!!!")
    print("Scheduler ID is"+s_id)
    
    if cloud == "GCP":
        GCP_driver.delete_vm(s_id)
        for w in w_ids:
            GCP_driver.delete_vm(w)
            time.sleep(5)

    if cloud == "azure":
        Azure_driver.delete_vm(s_id)
        for w in w_ids:
            Azure_driver.delete_vm(w)

    
##
# This function creates the cluster and handles the submisison of the first job
##
def handle_cluster_job(cloud, ID, client_socket, RG, ALG, ERG, NWs):

    s_ip, s_id, w_ips, w_ids = create_cluster(cloud, ID, client_socket, RG, NWs)
    result = submit_jobs(ALG,ERG,s_ip, ID)
    result.tofile("output"+str(ID)+".csv", sep=",")

    with open("output"+str(ID)+".csv", "rb") as file:
        file_content = file.read()

    data = b"FILE:" + file_content
    client_socket.sendall(data)
    print("Dataset sent successfully!")  
    
    return s_ip, s_id, w_ips, w_ids

##
# this function will call submit_jobs function and send the output file to the client
##
def handle_job(socket, ALG, ERG, s_ip, ID):

    result = submit_jobs(ALG,ERG,s_ip, ID)
    result.tofile("output"+str(ID)+".csv", sep=",")

    with open("output"+str(ID)+".csv", "rb") as file:
        file_content = file.read()

    data = b"FILE:" + file_content
    socket.sendall(data)
    print("Dataset sent successfully!")  
    
##
# Main
##
def main():

    while True:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((server_ip, server_port))
        server_socket.listen(1)
        print(f"Server listening for new clients on {server_ip}:{server_port}")

        # Accept a client connection
        client_socket, client_address = server_socket.accept()
        print(f"Client connected from {client_address}")
        
        thd.Thread(target=handle_client, args=(client_socket, client_address)).start()

        

##
# This function will be the target of a thread. It handles a client and listens for requests and data. This enables the ability of multi-clients handling.
##
def handle_client(client_socket, client_address):
    ID = client_address[1]
    
    s_ip=""
    s_id=""
    w_ips= []
    w_ids= []
    client_socket.send(str(ID).encode())
    time.sleep(0.5)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((server_ip, ID))
    server_socket.listen(1)
    client_socket, client_address = server_socket.accept()
    print("established didicated connection with client ID:"+ str(ID))
    while True:
        data = b""
        while True:
            chunk = client_socket.recv(1024)
            print(chunk.decode())
            if not chunk or chunk.decode() == 'END':
                break
            data += chunk
            
        data = data.decode()
        if data.startswith("NEW:"):
            RG, CR, NWs, ALG, ERG = parce_data(data[4:].encode(),ID)
            if CR == 1 or CR == 2:
                cloud = "GCP"
            else:
                cloud = "azure"
            
            s_ip, s_id, w_ips, w_ids =handle_cluster_job(cloud, ID, client_socket, RG, ALG, ERG, NWs)
            
        elif data.startswith("ADD:"):
            RG,CR,n = parce_data2(data[4:].encode())
            if CR == 1 or CR == 2:
                cloud = "GCP"
            else:
                cloud = "azure"
            print("Inside MAIN / DLT... s_IP is:" + s_ip)
            NWs, w_ids = add_workers(n, cloud, RG, ID, NWs, s_id, w_ids)
            
        elif data.startswith("DLT"):
                delete_cluster(cloud, s_id, w_ids)
                
        elif data.startswith("JOB:"):
            ALG, ERG = parce_data3(data[4:].encode(),ID)
            handle_job(client_socket, ALG, ERG, s_ip, ID)
    

    


if __name__=="__main__":   
    main()
