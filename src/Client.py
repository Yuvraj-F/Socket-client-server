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

NUM_ARGS = 3
MIN_PORT = 1024
MAX_PORT = 64000
MAGIC_NO = 0x36FB                
REQUEST_PACKET_TYPE = 0x0001             
REQUEST_TYPE = {"date": 0x1,
                "time": 0x2}        
LANG_REP = {1: "English",          
            2: "Māori",            
            3: "German"}           

RESPONSE_HEADER_SIZE = 13       
RESPONSE_PACKET_CODE = 2
MAX_YEAR = 2100

def create_client_socket():
    """ Creates socket """
    
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
    
    packet = bytearray(6)
    
    packet[0] = MAGIC_NO >> 8
    packet[1] = MAGIC_NO & 0xff
    packet[3] = REQUEST_PACKET_TYPE
    packet[5] = REQUEST_TYPE[request_type]
    
    return packet


def validate_arguments(args):
    """ makes sure the command line arguments are valid. returns services if 
        given host name or ip address can be resolved """
    
    if len(args) != NUM_ARGS:
        raise ValueError("ERROR: Incorrect number of command line arguments")

    if args[0] not in REQUEST_TYPE.keys():
        raise ValueError(f"ERROR: Request type '{args[0]}' is not valid")
        
    if not args[2].isdigit() or int(args[2]) <= 0:
        raise ValueError(f"ERROR: Given port '{args[2]}' is not a positive integer")
 
    if int(args[2]) < MIN_PORT or int(args[2]) > MAX_PORT:
        raise ValueError(f"ERROR: Given port '{args[2]}' is not in the range [1024, 64000]")

    try:    
        services = getaddrinfo(args[1], args[2], AF_INET, SOCK_DGRAM)
    except gaierror:
        raise ValueError("ERROR: Hostname resolution failed")
        
    return services

def validate_response(data):
    """ Performs checks to validate dt-response packet. 
        Raises ValueError if invalid. """
    
    if len(data) < RESPONSE_HEADER_SIZE:
        raise ValueError("ERROR: Packet is too small to be a DT_Response")
    
    if data[0] != MAGIC_NO >> 8 or data[1] != MAGIC_NO & 0xff:
        raise ValueError("ERROR: Packet magic number is incorrect")
    
    if data[3] != RESPONSE_PACKET_CODE:
        raise ValueError("ERROR: Packet is not a DT_Response")
    
    if data[5] not in [1,2,3]:
        raise ValueError("ERROR: Packet has invalid language")
    
    if data[6] << 8 | data[7] > MAX_YEAR:
        raise ValueError("ERROR: Packet has invalid year")
    
    if data[8] < 1 or data[8] > 12:
        raise ValueError("ERROR: Packet has invalid month")
    
    if data[9] < 1 or data[9] > 31:
        raise ValueError("ERROR: Packet has invalid day")
    
    if data[10] < 0 or data[10] > 23:
        raise ValueError("ERROR: Packet has invalid hour")
    
    if data[11] < 0 or data[11] > 59:
        raise ValueError("ERROR: Packet has invalid minute")
    
    if len(data) != (13 + data[12]):
        raise ValueError("ERROR: Packet text length is incorrect")
    
    try:
        decoded_text = data[13:].decode("utf-8")
    except UnicodeDecodeError:
        raise ValueError("ERROR: Packet has invalid text")
    
    
def exit_client(socket):
    socket.close()
    exit()
    
def main():
    """ Client activities """
    
    arguments = argv[1:]
    
    try:    
        services = validate_arguments(arguments)
    except ValueError as err:
        print(err)
        exit()
    
    family, sock_type, proto, canonname, server_address = services[0] 
    sock = create_client_socket()
 
    request_packet = create_request_packet(arguments[0])
    
    try:
        amount = sock.sendto(request_packet, server_address)
    except (OSError, TimeoutError):
        print("ERROR: Sending failed")
        exit_client(sock)
        
    print(f"{arguments[0].capitalize()} request sent to {server_address[0]}:{server_address[1]}")

    try:
        recv_data = sock.recv(64)  
    except TimeoutError:
        print("ERROR: Receiving timed out")
        exit_client(sock)
    except OSError:
        print("ERROR: Receiving failed")
        exit_client(sock)

    try:
        validate_response(recv_data)
    except ValueError as err:
        print(err)
        exit_client(sock)  

    decoded_text = recv_data[13:].decode("utf-8")
    month, day, year = recv_data[8], recv_data[9], recv_data[6] << 8 | recv_data[7]
    hour, minute = recv_data[10], recv_data[11]
    
    print(f"{LANG_REP[recv_data[5]]} response received:")
    print(f"Text: {decoded_text}")
    print(f"Date: {day}/{month}/{year}")
    print(f"Time: {hour:02d}:{minute:02d}")
    
    exit_client(sock)
    
""" TEST COMMANDS """
#python3 src/Client.py time localhost 15442
#py src/Client.py time localhost 15442

main()

