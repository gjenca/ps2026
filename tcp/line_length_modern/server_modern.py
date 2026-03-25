import socket
import os
import sys
import threading

def handle_client(cs,addr):
       
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


ss=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
ss.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
ss.bind(("",9999))
ss.listen(5)

while True:
    cs,addr=ss.accept()
    print(f'connected {addr}')
    thread=threading.Thread(target=handle_client,args=(cs,addr),daemon=True)
    thread.start()
    cs.close()
