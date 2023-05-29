import socket
import sys

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

    amount_received = 0
    amount_expected = 20
    
    while amount_received < amount_expected:
        data = sock.recv(32)
        amount_received += len(data)
        print('received "%s"' % data, file=sys.stderr)

finally:
    print('closing socket', file=sys.stderr)
    sock.close()
