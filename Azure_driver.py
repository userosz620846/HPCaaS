import re
from azure.mgmt.compute import ComputeManagementClient
from azure.identity import AzureCliCredential
from azure.mgmt.network import NetworkManagementClient



# Define your Azure credentials
subscription_id = '0284bf80-1bc7-47c0-96b2-b7487bd695dd'
client_id = '795acf3e-6991-4ed2-be38-e4ee80bdfa82'
secret = 'wUF8Q~yk1HNSwrrRyrEWzXo096FHE67RlEpj_btK'
tenant = '5edb4f8a-bff3-477d-b5b9-a11a85d85d64'
resourceGroupName = "COE619"
location = 'north central us'

# Authenticate the clients
credential = AzureCliCredential()
compute_client = ComputeManagementClient(credential, subscription_id)
network_client = NetworkManagementClient(credential, subscription_id)



def create_ip(resource_id):
    publicIPName = 'my-pub-ip-'+resource_id
    public_ip_params = {
    'location': location,
    'public_ip_allocation_method': 'Dynamic'
    }
    public_ip_result = network_client.public_ip_addresses.begin_create_or_update(
        resourceGroupName,
        publicIPName,
        public_ip_params
    )
    
    print("public ip created.....")
    return public_ip_result

def create_nic(resource_id):
    networkInterfaceName = 'my-nic-'+resource_id
    publicIPName = 'my-pub-ip-'+resource_id
    nic_params = {
    'location': location,
    'ip_configurations': [{
        'name': "ipconfig1",
        'subnet': {
            'id':"/subscriptions/0284bf80-1bc7-47c0-96b2-b7487bd695dd/resourceGroups/COE619/providers/Microsoft.Network/virtualNetworks/dask-node-test-vnet/subnets/default"
        },
         "publicIPAddress": {
                        "id": f"/subscriptions/0284bf80-1bc7-47c0-96b2-b7487bd695dd/resourceGroups/COE619/providers/Microsoft.Network/publicIPAddresses/{publicIPName}",
                        "properties": {
                            "deleteOption": "Detach"
                        }
        }
    }],
    "networkSecurityGroup": {
           'id': '/subscriptions/0284bf80-1bc7-47c0-96b2-b7487bd695dd/resourceGroups/COE619/providers/Microsoft.Network/networkSecurityGroups/dask-node-test-nsg'
        }
}

    nic_result = network_client.network_interfaces.begin_create_or_update(
        resourceGroupName,
        networkInterfaceName,
        nic_params
    )
    
    print("nic created.....")
    return nic_result

def create_vm(resource_id):
        
        public_ip = create_ip(resource_id= resource_id)
        create_nic(resource_id= resource_id)
        
        vm_name = 'dask-node-'+resource_id
        networkInterfaceName = 'my-nic-'+resource_id
        param = {
        'location': location,
        'hardware_profile': {
             "vmSize": "Standard_B1ls"
        },
        "storageProfile": {
                "imageReference": {
                    "id": "/subscriptions/0284bf80-1bc7-47c0-96b2-b7487bd695dd/resourceGroups/COE619/providers/Microsoft.Compute/galleries/my_images/images/dask-node-def",
                    "exactVersion": "latest"
                },
                # "osDisk": {
                #     "osType": "Linux",
                #     "name": "dask-node-1_OsDisk_1_2252ecb6162747c5beef74c62996e495",
                #     "createOption": "FromImage",
                #     "caching": "ReadWrite",
                #     "managedDisk": {
                #         "storageAccountType": "Standard_LRS",
                #         "id": "/subscriptions/0284bf80-1bc7-47c0-96b2-b7487bd695dd/resourceGroups/COE619/providers/Microsoft.Compute/disks/dask-node-1_OsDisk_1_2252ecb6162747c5beef74c62996e495"
                #     },
                #     "deleteOption": "Detach",
                #     "diskSizeGB": 30
                # },
                # "dataDisks": []
            },
            "osProfile": {
                "computerName": vm_name,
                "adminUsername": "goss4",
                "linuxConfiguration": {
                    "disablePasswordAuthentication": True,
                    "ssh": {
                        "publicKeys": [
                            {
                                "path": "/home/goss4/.ssh/authorized_keys",
                                "keyData": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQChZ1MvRympl9akikGHEvpUJ7YdZ/UG0LoyKa257vab+Y2E+F6kTrmoDkdvfggyfDdaKYZcdRlZ4NSom09oQ0JiXgTz1IHRMsoJRoFVPJN906AXQxUzi3iq1Oh3z+RyiNBqXJCx/Yio94Cno4gaieY0Jsb6IXekdktSgjD4aoGBfcLfth9A72Pvn8JpRkcFv5qVeV8KVjdrH+XLysDTZdnMf0t87q3xejv98sdynaKCDp1UBtYLF+2Kldill7StzDpTZ3fJHhIrHcJ8/HpvIhFMwoVIpIXZbvVNfHWuZ/uDjD9Xy8NW+gIUiT+ECUgFKXNJggSOb/jodWF267jF5+9RGNzIXSLuQkL4QQY1m7LQdhGNbvm/o95bMF0QDP+OLHePt3Jwqwv8H8mB90LsMxbZwOst6zOdAn+o62wcOmte5gHz6jb0ZXSFoOfPkefQOm/gsea0u5497kLzH930WW/7wQy1Ku/fxhLjxANrawRBBGecrQFIOSX9eDGBEwhLZos= goss4@Laptop"
                            }
                        ]
                    },
                    "provisionVMAgent": True,
                    "patchSettings": {
                        "patchMode": "ImageDefault",
                        "assessmentMode": "ImageDefault"
                    }
                },
                "secrets": [],
                "allowExtensionOperations": True,
                # "requireGuestProvisionSignal": False
            },
            "securityProfile": {
                "uefiSettings": {
                    "secureBootEnabled": True,
                    "vTpmEnabled": True
                },
                "securityType": "TrustedLaunch"
            },
            "networkProfile": {
                "networkInterfaces": [
                    {
                        "id": f"/subscriptions/0284bf80-1bc7-47c0-96b2-b7487bd695dd/resourceGroups/COE619/providers/Microsoft.Network/networkInterfaces/{networkInterfaceName}",
                        "properties": {
                            "deleteOption": "Detach"
                        }
                    }
                ]
            }
        
        
    }
        poller = compute_client.virtual_machines.begin_create_or_update('COE619', vm_name, param, polling=True)
        result = poller.result()
        print(f"VM: {vm_name} created......")
        return result
    

def get_ip(resource_id):
    
    ip_name = 'my-pub-ip-'+resource_id
        
        # name = 'dask-node-'+resource_id
        # vm = compute_client.virtual_machines.get(resourceGroupName, name)
        # # print(vm.network_profile.network_interfaces)
        # for interface in vm.network_profile.network_interfaces:
        #         ni_name = interface.id.split('/')[-1]
        #         print(ni_name)
        #         sub = interface.id.split('/')[4]
        #         print(sub)

        # ip_configs = network_client.network_interfaces.get(sub, ni_name).ip_configurations
        # for config in ip_configs:
        #     print(config.public_ip_address)
        #     # if config.public_ip_address:
        #     #     public_ip = config.public_ip_address
        #     # return public_ip.ip_address
        
    public_ip = network_client.public_ip_addresses.get(resourceGroupName, ip_name)
    return public_ip.ip_address

def delete_vm(resource_id):
    vm_name = 'dask-node-'+resource_id
    compute_client.virtual_machines.begin_delete('COE619', vm_name).wait()
    print(f"VM '{vm_name}' has been deleted successfully.")


# vm, ip = create_vm("23")


vm_size = "Standard_B1ls"

# Define the parameters for your virtual machine



# create new  public IP and NIC

# public_ip_params = {
#     'location': location,
#     'public_ip_allocation_method': 'Dynamic'
# }
# public_ip_result = network_client.public_ip_addresses.begin_create_or_update(
#     resourceGroupName,
#     publicIPName,
#     public_ip_params
# )

# print("Public IP Address created.....\n")

# nic_params = {
#     'location': location,
#     'ip_configurations': [{
#         'name': "ipconfig1",
#         'subnet': {
#             'id':"/subscriptions/0284bf80-1bc7-47c0-96b2-b7487bd695dd/resourceGroups/COE619/providers/Microsoft.Network/virtualNetworks/dask-node-test-vnet/subnets/default"
#         },
#          "publicIPAddress": {
#                         "id": f"/subscriptions/0284bf80-1bc7-47c0-96b2-b7487bd695dd/resourceGroups/COE619/providers/Microsoft.Network/publicIPAddresses/{publicIPName}",
#                         "properties": {
#                             "deleteOption": "Detach"
#                         }
#         }
#     }],
#     "networkSecurityGroup": {
#            'id': '/subscriptions/0284bf80-1bc7-47c0-96b2-b7487bd695dd/resourceGroups/COE619/providers/Microsoft.Network/networkSecurityGroups/dask-node-test-nsg'
#         }
# }

# nic_result = network_client.network_interfaces.begin_create_or_update(
#     resourceGroupName,
#     networkInterfaceName,
#     nic_params
# )

# print("NIC created.....\n")


# Create the virtual machine

# param = {
#     'location': location,
#     'hardware_profile': {
#         'vm_size': vm_size
#     },
#     "storageProfile": {
#             "imageReference": {
#                 "id": "/subscriptions/0284bf80-1bc7-47c0-96b2-b7487bd695dd/resourceGroups/COE619/providers/Microsoft.Compute/galleries/my_images/images/dask-node-def",
#                 "exactVersion": "0.0.1"
#             },
#             # "osDisk": {
#             #     "osType": "Linux",
#             #     "name": "dask-node-1_OsDisk_1_2252ecb6162747c5beef74c62996e495",
#             #     "createOption": "FromImage",
#             #     "caching": "ReadWrite",
#             #     "managedDisk": {
#             #         "storageAccountType": "Standard_LRS",
#             #         "id": "/subscriptions/0284bf80-1bc7-47c0-96b2-b7487bd695dd/resourceGroups/COE619/providers/Microsoft.Compute/disks/dask-node-1_OsDisk_1_2252ecb6162747c5beef74c62996e495"
#             #     },
#             #     "deleteOption": "Detach",
#             #     "diskSizeGB": 30
#             # },
#             # "dataDisks": []
#         },
#         "osProfile": {
#             "computerName": vm_name,
#             "adminUsername": "goss4",
#             "linuxConfiguration": {
#                 "disablePasswordAuthentication": True,
#                 "ssh": {
#                     "publicKeys": [
#                         {
#                             "path": "/home/goss4/.ssh/authorized_keys",
#                             "keyData": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQChZ1MvRympl9akikGHEvpUJ7YdZ/UG0LoyKa257vab+Y2E+F6kTrmoDkdvfggyfDdaKYZcdRlZ4NSom09oQ0JiXgTz1IHRMsoJRoFVPJN906AXQxUzi3iq1Oh3z+RyiNBqXJCx/Yio94Cno4gaieY0Jsb6IXekdktSgjD4aoGBfcLfth9A72Pvn8JpRkcFv5qVeV8KVjdrH+XLysDTZdnMf0t87q3xejv98sdynaKCDp1UBtYLF+2Kldill7StzDpTZ3fJHhIrHcJ8/HpvIhFMwoVIpIXZbvVNfHWuZ/uDjD9Xy8NW+gIUiT+ECUgFKXNJggSOb/jodWF267jF5+9RGNzIXSLuQkL4QQY1m7LQdhGNbvm/o95bMF0QDP+OLHePt3Jwqwv8H8mB90LsMxbZwOst6zOdAn+o62wcOmte5gHz6jb0ZXSFoOfPkefQOm/gsea0u5497kLzH930WW/7wQy1Ku/fxhLjxANrawRBBGecrQFIOSX9eDGBEwhLZos= goss4@Laptop"
#                         }
#                     ]
#                 },
#                 "provisionVMAgent": True,
#                 "patchSettings": {
#                     "patchMode": "ImageDefault",
#                     "assessmentMode": "ImageDefault"
#                 }
#             },
#             "secrets": [],
#             "allowExtensionOperations": True,
#             # "requireGuestProvisionSignal": False
#         },
#         "securityProfile": {
#             "uefiSettings": {
#                 "secureBootEnabled": True,
#                 "vTpmEnabled": True
#             },
#             "securityType": "TrustedLaunch"
#         },
#         "networkProfile": {
#             "networkInterfaces": [
#                 {
#                     "id": f"/subscriptions/0284bf80-1bc7-47c0-96b2-b7487bd695dd/resourceGroups/COE619/providers/Microsoft.Network/networkInterfaces/{networkInterfaceName}",
#                     "properties": {
#                         "deleteOption": "Detach"
#                     }
#                 }
#             ]
#         }
    
    
# }

# poller = compute_client.virtual_machines.begin_create_or_update('COE619', vm_name, param, polling=True)
# result = poller.result()



