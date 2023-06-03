import socket
import json

class KlipperSocket :
    
    __slots__ : ('socket_conn')

    def __init__(self, socket_address:str) :

        self.socket_conn = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

        # try :
        #     self.socket_conn.connect(socket_address) 
        # except socket.error as msg :
        #     raise Exception(f"socket could not connect on {socket_address}")

    def closeSocket(self) :
        self.socket_conn.close()

    def sendMessage(self, message:dict) :
        """
        send JSON serialized messages (dictonaries) to the klipper uds

        messages do not have to be terminated with \x03 manually
        """
        str_message = json.dumps(message) + '\x03'
        self.socket_conn.sendall(str.encode(message))