""" 
------Client------
Sends dt-request packets to Server. Recieves dt-response packets from Server. 

Upon receiving: 
Check size (>=13 bytes), MagicNo == 0x36FB, PacketType == 0x0002 

Author: Yuvraj Singh Fagotra 
"""

""" dt-request format """

from sys import exit, argv
from socket import socket, AF_INET, SOCK_DGRAM, getaddrinfo, gaierror

#Globals
NUM_ARGS = 3
MIN_PORT = 1024
MAX_PORT = 64000
MAGIC_NO = 0x36FB                #Identifies packet as a DateTime packet (16-bits)
PACKET_TYPE = 0x0001             #Identifies packet as a dt-request packet (16-bits)
REQUEST_TYPE = {"date": 0x1,
                "time": 0x2}        #Type of request. 1 = date, 2 = time (16-bits)


def create_client_socket():
    """ """
    sock = None
    
    try:
        sock = socket(AF_INET, SOCK_DGRAM)
    except OSError:
        
        if sock != None:
            sock.close()
            
        print("ERROR: Socket creation failed")
        exit()
        
    sock.settimeout(1)
    
    return sock    

def create_request_packet(request_type):
    """ Creates and returns a dt-request packet. """
    
    #initialize packet of size 6 bytes
    packet = bytearray(6)
    
    #Set MagicNo field
    packet[0] = MAGIC_NO >> 8
    packet[1] = MAGIC_NO & 0xff
    
    #Set PacketType field
    packet[3] = PACKET_TYPE
    
    #Set RequestType field
    packet[5] = REQUEST_TYPE[request_type]
    
    return packet


def validate_arguments(args):
    """ makes sure the command line arguments are valid. returns services if 
        given host name or ip address can be resolved """
    
    #there must be NUM_ARGS arguments
    if len(args) != NUM_ARGS:
        raise ValueError("ERROR: Incorrect number of command line arguments")
        
    #First argument must be "date" or "time"
    if args[0] not in REQUEST_TYPE.keys():
        raise ValueError(f"ERROR: Request type '{args[0]}' is not valid")
        
    #Third argument must be positive and in the range [1024, 64000]
    if int(args[2]) <= 0:
        raise ValueError(f"ERROR: Given port '{args[2]}' is not a positive integer")
 
    if int(args[2]) < MIN_PORT or int(args[2]) > MAX_PORT:
        raise ValueError(f"ERROR: Given port '{args[2]}' is not in the range [1024, 64000]")
 
        
    #Second argument must be dotted ip address or hostname. If it can be resolved,
    #extracts the address to use for sending requests to hosts
    try:    
        services = getaddrinfo(args[1], args[2], AF_INET, SOCK_DGRAM)
    except gaierror:
        raise ValueError("ERROR: Hostname resolution failed")
   
        
    return services
    
def exit_client(socket):
    socket.close()
    exit()
    
def main():
    """ Client activities """
    
    #Get command line arguments
    arguments = argv[1:]

    #Check for error. If valid, get services based on given arguments
    try:    
        services = validate_arguments(arguments)
    except ValueError as err:
        print(err)
        exit()
    
    #extract Server address from services
    family, sock_type, proto, canonname, server_address = services[0] 
    
    #Create socket
    sock = create_client_socket()
        
    #Create dt_request packet    
    packet = create_request_packet(arguments[0])
    
    #Send dt_request packet to server
    try:
        amount = sock.sendto(packet, server_address)
    except (OSError, TimeoutError):
        print("ERROR: Sending failed")
        exit_client(sock)
        
    #Status message if packet is sent to Server successfuly 
    print(f"{arguments[0]} request sent to {server_address[0]}:{server_address[1]}")
        

    sock.close()
    
""" TEST COMMANDS """
#python3 src/Client.py time localhost 15442
#py src/Client.py time localhost 15442

main()

