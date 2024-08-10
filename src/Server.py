""" 
------Server------
Recieves dt-request packets from Client. Sends dt-response packets to Client.

Upon receiving: 
Check size (6 bytes), MagicNo == 0x36FB, PacketType = 0x0001, RequestType = 0x0001 | 0x0002.

Author: Yuvraj Singh Fagotra 
"""

import sys
import socket

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

def main():
    """ args must be three port numbers that are used for English, Maori and German
        respectively. """
    
    #Get command line arguments
    arguments = sys.argv[1:]
    
    #Check for Errors
    if len(arguments) != 3:
        print("ERROR: Incorrect number of command line arguments")
        return
    if len(set(arguments)) != 3:
        print("ERROR: Duplicate ports given")
        return
    for arg in arguments:
        if arg <= 0:
            print(f"ERROR: Given port '{arg}' is not a positive integer")
            return
    for arg in arguments:
        if arg < MIN_PORT or arg > MAX_PORT:
            print(f"ERROR: Given port '{arg}' is not in the range [1024, 64000]")
            return
    
        
main()