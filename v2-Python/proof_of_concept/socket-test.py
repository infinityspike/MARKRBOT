import socket
import sys
import os

# Create a UDS socket
sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = '/tmp/klippy_uds'
print('connecting to %s' % server_address, file=sys.stderr)
try:
    sock.connect(server_address)
except socket.error as msg :
    print(msg, file=sys.stderr)
    sys.exit(1)

try:
    
    # Send data
    message = '{"id": 123, "method": "info", "params": {}}\x03'
    print('sending "%s"' % message, file=sys.stderr)
    sock.sendall(str.encode(message))

    data = bytes()
    while True:
        data += sock.recv(32)
        if bytes.decode(data).endswith('\x03'): break
    print('received "%s"' % data, file=sys.stderr)

except KeyboardInterrupt:
    print("KeyboardInt")
    print('closing socket', file=sys.stderr)
    sock.close()
    try:
        sys.exit()
    except SystemExit:
            os._exit(130)
