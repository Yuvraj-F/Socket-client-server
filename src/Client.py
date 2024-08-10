""" 
------Client------
Sends dt-request packets to Server. Recieves dt-response packets from Server. 

Upon receiving: 
Check size (>=13 bytes), MagicNo == 0x36FB, PacketType == 0x0002 

Author: Yuvraj Singh Fagotra 
"""

""" dt-request format """

from sys import exit, argv
from socket import socket, AF_INET, SOCK_STREAM, getaddrinfo

MagicNo = 0x36FB                #Identifies packet as a DateTime packet (16-bits)
PacketType = 0x0001             #Identifies packet as a dt-request packet (16-bits)
RequestType = "0x000(1|2)"        #Type of request. 1 = date, 2 = time (16-bits)




def main():
    pass

main()