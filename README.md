# HPCaaS

This project is to create a multi-cloud, custom-scheduling enabled HPC as a Service (HPCaaS) platform.

How to setup:
- cloud environment setup:
in azure, you needa subsctition ID, a client ID, and a resource group name. Also, you need a method of authentication, which in my case is using local authentication by installing azure CLI on the local machine and entering the azure creds once. As for GCP, you need a project, and a zone. Authenticaion is the same as Aure (local authentication which is done once and stored on the local machine). The cloud integration and API intergation logic is in Azure_driver.py and GCP_driver.py
- RSA key managment: the private key is id_rsa (uploaded in the repo), it will be used automatically. It should be placed in the same folder as controller_final.py
- as for the public key, in Azure, every VM is pre-configured with it (see Azure_driver.py), and in GCP the SSH public key is defined for the whole project scope (no need to configure indivisual VMs with it)
- Run controller_final.py and once it starts up and listens for client connections, start client_final.py
- mulitple clients can connect at the same time.
- Datasets can be generated using data_creator.py for convinient testing.
