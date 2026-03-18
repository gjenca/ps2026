import socket
import os
import sys

ss=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
ss.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
ss.bind(("",9999))
ss.listen(5)
while True:
    cs,addr=ss.accept()
    print(f'connected {addr}')
    if os.fork()==0:
        while True:
            data=cs.recv(1024)
            if not data: # Prazdne 'bytes' objekt ==koniec spojenia
                break
            # Posleme naspat dlzku prijatych dat
            len_data=len(data)
            send_back=f'{len_data}\n'.encode('utf-8')
            cs.send(send_back)
        print(f'disconnected {addr}')
        sys.exit(0)
