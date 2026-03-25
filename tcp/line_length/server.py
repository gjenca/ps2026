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
        ss.close()
        f=cs.makefile('rwb')
        while True:
            #data=cs.recv(1024)
            line=f.readline()
            if not line: # Prazdne 'bytes' objekt ==koniec spojenia
                break
            # Posleme naspat dlzku prijatych dat
            len_line=len(line)
            send_back=f'{len_line}\n'.encode('utf-8')
            f.write(send_back)
            f.flush()
        print(f'disconnected {addr}')
        sys.exit(0)
    else:
        cs.close()
