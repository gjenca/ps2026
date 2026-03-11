import socket
import struct
import sys
import time
import logging


FNM_SEND='Capybara_Hattiesburg_Zoo_(70909b-42)_2560x1600.jpg'

OPCODE_RRQ=1
OPCODE_DATA=3
OPCODE_ACK=4
OPCODE_DATA_b=struct.pack('>H',OPCODE_DATA)

logging.basicConfig(level=logging.WARNING)

class Reader:

    def __init__(self,s,addr):

        self.s=s
        self.addr=addr
        self.f=open(FNM_SEND,'rb')
        self.bn=0
        self.read_len=None
        self.normal_end=False
        self.error=False
        self.send_data()

    def send_data(self):
        send_back=self.f.read(512)
        self.read_len=len(send_back)
        self.bn=self.bn+1
        block_num_b=struct.pack('>H',self.bn)
        logging.info(f'sending data length={self.read_len}')
        s.sendto(OPCODE_DATA_b+block_num_b+send_back,self.addr)

    def handle_data(self,packet):
        
        opcode=struct.unpack('>H',data[:2])[0]
        block_num=struct.unpack('>H',data[2:4])[0]
        if opcode!=OPCODE_ACK:
            logging.warning(f'Received opcode={opcode}, expected 4\n')
            self.error=True
            self.f.close()
            return
        if self.bn!=block_num:
            logging.warning(f'Received block_num={block_num}, expected {self.bn}\n')
            self.error=True
            self.f.close()
            return
        logging.info(f'block {self.bn}')
        if self.read_len<512:
            self.normal_end=True
            self.f.close()
        else:
            self.send_data()

    def done(self):

        return self.normal_end or self.error

s=socket.socket(socket.AF_INET6,socket.SOCK_DGRAM)
s.bind(("",9999))

readers={}

while True:
    data,addr=s.recvfrom(1024)
    time.sleep(0.01)
    opcode=struct.unpack('>H',data[:2])[0]
    logging.debug(f'{opcode=}')
    if opcode==OPCODE_RRQ:
        logging.info(f'Creating reader {addr}')
        readers[addr]=Reader(s,addr)
    elif opcode==OPCODE_ACK:
        if addr in readers:
            readers[addr].handle_data(data)
            if readers[addr].done():
                del readers[addr]
        else:
            logging.warning(f'Unknown address {addr}')


