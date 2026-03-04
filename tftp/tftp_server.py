import socket
import struct

FNM_SEND='Capybara_Hattiesburg_Zoo_(70909b-42)_2560x1600.jpg'



s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
s.bind(("",9999))

data,addr=s.recvfrom(1024)
print(data)
opcode=struct.unpack('>H',data[:2])
fnm,encoding,null=data[2:].split(b'\x00')
print(f'{opcode=} {fnm=} {encoding=} {null=}')
data_b=struct.pack('>H',3)
with open(FNM_SEND,'rb') as f:
    bn=0
    while True:
        send_back=f.read(512)
        bn=bn+1
        block_num_b=struct.pack('>H',bn)
        s.sendto(data_b+block_num_b+send_back,addr)
        data,addr=s.recvfrom(1024)
        opcode=struct.unpack('>H',data[:2])
        block_num=struct.unpack('>H',data[2:4])
        print(f'{opcode=} {block_num=}')
        if len(send_back)<512:
            break

