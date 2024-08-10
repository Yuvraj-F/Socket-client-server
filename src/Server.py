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

#Globals
NUM_ARGUMENTS = 3
MIN_PORT = 1024
MAX_PORT = 64000


""" dt-response format """
MagicNo = 0x36FB                #Identifies packet as a DateTime packet (16-bits)
PacketType = 0x0002             #Identifies packet as a dt-request packet (16-bits)
LanguageCode = "0x000(1|2|3)"     #Language used, 1 = English, 2 = Maori, 3 = German (16-bits)
Year = 0x0000                   #The year as a non negative integer (16-bits)
Month = 0x00                    #The month between 1-12 (8-bits)
Day = 0x00                      #The day between 1-31 (8-bits)
Hour = 0x00                     #The hour between 0-23 (8-bits)
Minute = 0x00                   #The minute between 0-59 (8-bits)
Length = 0x00                   #Lenght of text in bytes (8-bits)
Text = "variable"               #Text representation of response (variable)


def create_socket(lang, port):
    """ Before creating the socket, prints a status message which specifies the 
        language the socket is being used for and the associated port number.
        Creates and returns a new socket and binds it to the given port number."""
    
    print(f"Binding {lang} to port {port}")
    
    s = None

    try:
        s = socket(AF_INET, SOCK_DGRAM)
    except OSError:
        raise OSError("ERROR: Socket creation failed")
        
    try:
        s.bind(("localhost", port))
    except OSError:
        raise OSError("ERROR: Socket binding failed")
    
    return s

def main():
    """ args must be three port numbers that are used for English, Maori and German
        respectively. """
    
    #Get command line arguments
    arguments = argv[1:]
    arguments = [5000, 5001, 5002]
    
    
    #Check for Errors
    if len(arguments) != 3:
        print("ERROR: Incorrect number of command line arguments")
        exit()
    if len(set(arguments)) != 3:
        print("ERROR: Duplicate ports given")
        exit()
    for arg in arguments:
        if int(arg) <= 0:
            print(f"ERROR: Given port '{arg}' is not a positive integer")
            exit()
    for arg in arguments:
        if int(arg) < MIN_PORT or int(arg) > MAX_PORT:
            print(f"ERROR: Given port '{arg}' is not in the range [1024, 64000]")
            exit()
    
    
    #create a seperate socket for each of the three languages. initialise sockets
    #here so they can be closed later if error occurs
    eng_s = None
    maori_s = None
    german_s = None
    SOCKETS = {eng_s, maori_s, german_s}
    
    try:
        eng_s = create_socket("English", int(arguments[0]))
        maori_s = create_socket("Māori", int(arguments[1]))
        german_s = create_socket("German", int(arguments[2]))
        
    #If error occurs, close all sockets, print error message, and exit program
    except OSError as err:
        
        for s in SOCKETS:
            if s != None:
                s.close()
                
        print(err)
        exit()
    
    
    #Enter loop until 
    #print("Waiting for requests...")
    #packet, _, __ = select([eng_s, maori_s, german_s], [], [], 5)
    #print("Timeout")
    eng_s.close()
    maori_s.close()
    german_s.close()
       
    
        
main()