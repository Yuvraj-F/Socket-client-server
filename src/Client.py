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
    s = None
    
    try:
        s = socket(AF_INET, SOCK_DGRAM)
    except OSError:
        
        if s != None:
            s.close()
            
        print("ERROR: Socket creation failed")
        exit()
    
    return s    

def create_request_packet(request_type):
    """ creates and returns a dt-request packet. """
    
    #initialize packet with 6 bytes
    packet = bytearray(6)
    
    #Set MagicNo field
    packet[0] = MAGIC_NO >> 8
    packet[1] = MAGIC_NO & 0xff
    
    #Set PacketType field
    packet[3] = PACKET_TYPE
    
    #Set RequestType field
    packet[5] = REQUEST_TYPE[request_type]
    
    return packet
    
    
def exit_client(socket):
    socket.close()
    exit()
    
def main():
    """ Client activities """
    
    #Get command line arguments
    arguments = argv[1:]
    arguments = ["time", "youtube.com", 4958]
    
    #Check for errors
    
    #there must be NUM_ARGS arguments
    if len(arguments) != NUM_ARGS:
        print("ERROR: Incorrect number of command line arguments")
        exit()
        
    #First argument must be "date" or "time"
    if arguments[0] not in REQUEST_TYPE.keys():
        print(f"ERROR: Request type '{arguments[0]}' is not valid")
        exit()
        
    #Third argument must be positive and in the range [1024, 64000]
    if int(arguments[2]) <= 0:
        print(f"ERROR: Given port '{arguments[2]}' is not a positive integer")
        exit()    
    if int(arguments[2]) < MIN_PORT or int(arguments[2]) > MAX_PORT:
        print(f"ERROR: Given port '{arguments[2]}' is not in the range [1024, 64000]")
        exit()  
    
    #Second argument must be dotted ip address or hostname. If it can be resolved,
    #extracts the address to use for sending requests to hosts
    try:    
        services = getaddrinfo(arguments[1], arguments[2], AF_INET, SOCK_DGRAM)
    except gaierror:
        print("ERROR: Hostname resolution failed")
        exit()
    
    #extract address from services
    family, sock_type, proto, canonname, address = services[0] 
    
    #Create socket
    s = create_client_socket()
        
    #Create dt_request packet    
    packet = create_request_packet(arguments[0])
    
    #Send dt_request packet to server
    try:
        amount = s.sendto(packet, address)
    except (OSError, TimeoutError):
        print("ERROR: Sending failed")
        exit_client(s)
        

    s.close()
    

main()

