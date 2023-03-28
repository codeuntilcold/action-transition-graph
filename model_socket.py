import socket
from time import sleep

SIMULATE_FILE_NAME = 'sim_8_4_1_20221105.txt'

def read_sim_file():
    for line in open(SIMULATE_FILE_NAME, 'r'):
        yield line

# Create a socket object
clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Get local machine name
host = socket.gethostname()

# Reserve a port for your service
port = 24000

# Connect to the server on local machine
clientsocket.connect((host, port))

for message in read_sim_file():
    clientsocket.send(message.encode('ascii'))
    sleep(1 / 30.0)

# Close the client socket
clientsocket.close()
