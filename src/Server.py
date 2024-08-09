""" 
------Server------
Recieves dt-request packets from Client. Sends dt-response packets to Client.

Upon receiving: 
Check size (6 bytes), MagicNo == 0x36FB, PacketType = 0x0001, RequestType = 0x0001 | 0x0002.

Author: Yuvraj Singh Fagotra 
"""

import sys
import socket

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
    for arg in sys.argv:
        print(arg)
        
main()