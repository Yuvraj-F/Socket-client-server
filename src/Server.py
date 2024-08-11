""" 
------Server------
Recieves dt-request packets from Client. Sends dt-response packets to Client.

Upon receiving: 
Check size (6 bytes), MagicNo == 0x36FB, PacketType = 0x0001, RequestType = 0x0001 | 0x0002.

Author: Yuvraj Singh Fagotra 
"""

from sys import exit, argv
from socket import socket, AF_INET, SOCK_DGRAM
from select import select
from datetime import datetime


#Globals
NUM_ARGS = 3
MIN_PORT = 1024
MAX_PORT = 64000
REQUEST_PACKET_SIZE = 6 #Bytes
REQUEST_PACKET_CODE = 1
REQUEST_TYPE = {0x1: "date",
                0x2: "time"}        #Type of request. 1 = date, 2 = time (16-bits)
MAGIC_NO = 0x36FB               #Identifies packet as a DateTime packet (16-bits)
RESPONSE_PACKET_TYPE = 0x0002            #Identifies packet as a dt-request packet (16-bits)
LANG_REP = ["English",          #String representaion for each language 
            "Māori",            #English, Maori, and German (16-bits)
            "German"]

MONTHS = {1: ("January", "Kohi-tātea", "Januar"),
          2: ("February", "Hui-tanguru", "Februar"),
          3: ("March", "Poutū-te-rangi", "März"),
          4: ("April", "Paenga-whāwhā", "April"),
          5: ("May", "Haratua", "Mai"),
          6: ("June", "Pipiri", "Juni"),
          7: ("July", "Hōngingoi", "Juli"),
          8: ("August", "Here-turi-kōkā", "August"),
          9: ("September", "Mahuru", "September"),
          10: ("October", "Whiringa-ā-nuku", "Oktober"),
          11: ("November", "Whiringa-ā-rangi", "November"),
          12: ("December", "Hakihea", "Dezember"),}

def create_server_socket(lang, port):
    """ Before creating the socket, prints a status message which specifies the 
        language the socket is being used for and the associated port number.
        Creates and returns a new socket and binds it to the given port number.
        
        Also set a timeout after socket is created."""
    
    print(f"Binding {lang} to port {port}")
    
    sock = None

    try:
        sock = socket(AF_INET, SOCK_DGRAM)
    except OSError:
        raise OSError("ERROR: Socket creation failed")
        
    try:
        sock.bind(("localhost", port))
        sock.settimeout(1)
    except OSError:
        sock.close()
        raise OSError("ERROR: Socket binding failed")
        
    
    
    return sock


def validate_request(data):
    """ Performs checks to validate dt-request packet. 
        Raises ValueError if invalid. """
    
    if len(data) != REQUEST_PACKET_SIZE:
        raise ValueError("ERROR: Packet length incorrect for a DT_Request, dropping packet")
    
    if data[0] != MAGIC_NO >> 8 or data[1] != MAGIC_NO & 0xff:
        raise ValueError("ERROR: Packet magic number is incorrect, dropping packet")
    
    if data[3] != REQUEST_PACKET_CODE:
        raise ValueError("ERROR: Packet is not a DT_Request, dropping packet")
    
    if data[5] not in REQUEST_TYPE.keys():
        raise ValueError("ERROR: Packet has invalid type, dropping packet")
    
    
    
def receive_packet(sockets):
    """ waits until one of the sockets are ready. Extracts and recieving socket, 
        recieved packet, and client address if packet is valid. Prints a status 
        message before returning. 
        
        Returns None if Error occurs"""
    
    #Print status message and wait until one of the sockets are ready to be recieved 
    print("Waiting for requests...")
    sock_list, write_sockets, err_sockets = select(sockets, [], [])
    
    #Extract socket to send response from
    sock = sock_list[0]
    
    #Extract dt-request packet and client address 
    try:
        recv_data, client_address = sock.recvfrom(64)  
        
    #Timeout exceeded
    except TimeoutError:
        print("ERROR: Receiving timed out, dropping packet")
        return
    
    #Receiving failed
    except OSError:
        print("ERROR: Receiving failed, dropping packet")
        return
    
    #Check packet validity
    try:
        validate_request(recv_data)
    except ValueError as err:
        print(err)
        return
    
    #Extract request type from packet
    request_type = recv_data[5]
    
    #Status message is packet is valid
    print(f"{LANG_REP[sockets.index(sock)]} received {REQUEST_TYPE[request_type]} request from {client_address[0]}")
    
    return recv_data, client_address, sock
    

def create_text_repr(date_time, lang_index, request_type):
    """ create a textual representation of given date and time in the language 
        specified by the lang_index. 
        
        1 = date
        2 = time """
    
    day, month, year = date_time.day, date_time.month, date_time.year
    hour, minute = date_time.hour, date_time.minute
    
    result = {1: (f"Today's date is {MONTHS[month][lang_index]} {day}, {year}", 
                  f"Ko te rā o tēnei rā ko {MONTHS[month][lang_index]} {day}, {year}",
                  f"Heute ist der {day}. {MONTHS[month][lang_index]} {year}"),
              
              2: (f"The current time is {hour:02d}:{minute:02d}",
                  f"Ko te wā o tēnei wā {hour:02d}:{minute:02d}",
                  f"Die Uhrzeit ist {hour:02d}:{minute:02d}")}
    
    return result[request_type][lang_index]

    
def create_response_packet(data, lang_index, sock):
    """ Creates and returns dt-response packet. """
    
    #Fetch current date and time
    curr_datetime = datetime.now()
    
    #Extract required date and time fields from the datetime object
    day, month, year = curr_datetime.day, curr_datetime.month, curr_datetime.year
    hour, minute = curr_datetime.hour, curr_datetime.minute    

    #Prepare enoded text based on request type
    encoded_text = create_text_repr(curr_datetime, lang_index, data[5]).encode("utf-8")
    
    #Check to make sure text is at most 255 bytes
    if len(encoded_text) > 255:
        print("ERROR: Text too long, dropping packet")
        return
    
    #Initialize packet with enough bytes to hold dt-response fixed fields (13-bytes) 
    # and the encoded text
    packet = bytearray(13 + len(encoded_text))
    
    #Set MagicNo field
    packet[0] = MAGIC_NO >> 8
    packet[1] = MAGIC_NO & 0xff
    
    #Set PacketType field
    packet[3] = RESPONSE_PACKET_TYPE   
    
    #Set Language Code field. Computed as lang_index + 1
    packet[5] = lang_index + 1
    
    #Set year
    packet[6] = year >> 8
    packet[7] = year & 0xff
    
    #Set month
    packet[8] = month
    
    #Set day
    packet[9] = day
    
    #Set hour
    packet[10] = hour
    
    #Set minute
    packet[11] = minute
    
    #Set length field which contains the length of the encoded text
    packet[12] = len(encoded_text)
    
    #Set text field. i is an index into the packet bytearray initialised to 13
    # as that is where the text field of a dt-response packet starts
    i = 13
    for byte in encoded_text:
        packet[i] = byte
        i+=1
        
    return packet
    
    
def validate_arguments(args):
    """ makes sure the command line arguments are valid. """
    
    if len(args) != NUM_ARGS:
        raise ValueError("ERROR: Incorrect number of command line arguments")
        
    if len(set(args)) != NUM_ARGS:
        raise ValueError("ERROR: Duplicate ports given")
        
    for arg in args:
        if not arg.isdigit() or int(arg) <= 0:
            raise ValueError(f"ERROR: Given port '{arg}' is not a positive integer")
            
    for arg in args:
        if int(arg) < MIN_PORT or int(arg) > MAX_PORT:
            raise ValueError(f"ERROR: Given port '{arg}' is not in the range [1024, 64000]")
              


def exit_server(sockets):
    
    for sock in sockets:
        if sock != None:
            sock.close()   

    exit()

def main():
    """ args must be three port numbers that are used for English, Maori and German
        respectively. """
    
    #Get command line arguments
    arguments = argv[1:]
    
    #Check for errors
    try:
        validate_arguments(arguments)
    except ValueError as err:
        print(err)
        exit()
    
    #create a seperate socket for each of the three languages. initialise sockets
    #here so they can be closed later if error occurs
    sockets = [None, None, None]
    try:
        for i in range(len(sockets)):
            sockets[i] = create_server_socket(LANG_REP[i], int(arguments[i]))
        
    #If error occurs, close all sockets, print error message, and exit program
    except OSError as err:     
        print(err)
        exit_server(sockets)
    
    #Enter receive loop until unhandeld error
    try:
        while True:
            
            #Retrieve dt-request packet, sending client's address, and the socket
            # which recieved the request packet
            received_data = receive_packet(sockets)
            
            #recieve_packet can return None. So check for None case before 
            # attempting to unpack return values
            if received_data != None:
                request_packet, client_address, sock = received_data
            else:
                continue
            
            #Create a dt-response packet. Can be None
            response_packet = create_response_packet(request_packet, sockets.index(sock), sock)
            
            #Send dt_response packet to client if response packet is not None
            if response_packet != None:
                try:
                    amount = sock.sendto(response_packet, client_address)
                except (OSError, TimeoutError):
                    print("ERROR: Sending failed, dropping packet")
                    continue
            
            #Print status message if response is sent successfully
            print("Response sent")
    
                
    except Exception as err:
        print(f"ERROR: {err}")
    finally:
        exit_server(sockets)
    
    
""" TEST COMMANDS """
#python3 src/Server.py 15442 6484 31912
#py src/Server.py 15442 6484 31912

main()