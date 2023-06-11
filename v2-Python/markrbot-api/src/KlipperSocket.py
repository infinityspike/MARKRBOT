import socket
import json

class KlipperSocket :
    
    __slots__ = ('socket_conn')

    def __init__(self, socket_address:str) :

        self.socket_conn = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

        try :
            self.socket_conn.connect(socket_address) 
        except socket.error as msg :
            raise Exception(f"socket could not connect on {socket_address}")

    def closeSocket(self) :
        self.socket_conn.close()

    def sendMessage(self, message:dict) -> dict :
        """
        send JSON serialized messages (dictonaries) to the klipper uds

        messages do not have to be terminated with \x03 manually
        """
        str_message = json.dumps(message) + '\x03'
        self.socket_conn.sendall(str.encode(str_message))

        data = str()
        while True:
            data += bytes.decode(self.socket_conn.recv(32))
            if data.endswith('\x03'): break
        return json.loads(data)

if __name__ == '__main__' :
    klipper = KlipperSocket("/tmp/klippy_uds")

    info = {
        "id" : 123,
        "method" : "info",
        "params" : {}
    }
    info_response = klipper.sendMessage(info)
