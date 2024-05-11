import string
from urllib import response
import subprocess
from click import command
from google.cloud import compute_v1
from fabric import Connection
import paramiko


# project = 'coe-619'
# zone = 'us-central1-a'
# name = 'dask-node-test3'
# machine_type = f"zones/{zone}/machineTypes/n1-standard-1"
# source_image = f"projects/{project}/global/images/dask-image"

client = compute_v1.InstancesClient()

user = 'goss4'
key_file = 'id_rsa'

def create_vm(resource_id):
    
    project = 'coe-619'
    zone = 'us-central1-c'
    name = 'dask-node-'+resource_id
    machine_type = f"zones/{zone}/machineTypes/n1-standard-1"
    source_image = f"projects/{project}/global/images/dask-image2"
    
    config = {
    "name": name,
    "machine_type": machine_type,
    "disks": [
        {
            "boot": True,
            "auto_delete": True,
            "initialize_params": {
                "source_image": source_image,
            },
        }
    ],
    "network_interfaces": [
        {
            "network": "global/networks/default",
            "access_configs": [
                {
                    "name": "External NAT"
                }
            ]
        }
    ]
    }

    response = client.insert(project=project, zone=zone, instance_resource=config)

    
    print("VM "+name+" has been created.")
    return response

def delete_vm(resource_id):
    project = 'coe-619'
    zone = 'us-central1-c'
    name = 'dask-node-'+resource_id
    client.delete(project=project, zone=zone,instance=name)
    print("VM has been deleted.")

def get_ip(resource_id):
    project = 'coe-619'
    zone = 'us-central1-c'
    name = 'dask-node-'+resource_id
    request = client.get(project=project, zone=zone, instance=name)
    return request.network_interfaces[0].access_configs[0].nat_i_p
    
def run_command( ip, command): 



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
    print(stdout.read().decode())

    # Close the connection
    client.close()

    
    


## create VM:

# create_vm(project,zone,name,machine_type, source_image)
#
#

## get public IP:
# print("public IP of your VM is:"+get_ip(project,zone,name))


## delete VM:
# delete_vm(project,zone,name)

# ip = get_ip(project,zone,name)
# command= "ls -l /"
# ip= "34.69.34.243"

# run_command(ip,command)