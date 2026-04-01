import socket
import os
import sys
import threading
import logging

logging.basicConfig(level=logging.DEBUG)

STATUS_OK=(100,'OK')
STATUS_REQUEST_CONTENT_EMPTY=(201,'Content empty')
STATUS_NOT_A_NUMBER=(202,'Not a number')
STATUS_STACK_TOO_SHORT=(203,'Stack too short')
STATUS_REQUEST_CONTENT_NONEMPTY=(204,'Content non empty')
STATUS_REQUEST_STACK_EMPTY=(205,'Stack empty')
STATUS_BAD_REQUEST=(301,'Bad request')

class ConnectionClosed(Exception):

    pass

class Request:

    def __init__(self,f):

        lines=[]
        while True:
            line=f.readline()
            line=line.decode('utf-8')
            if not line:
                raise ConnectionClosed
            if line=='\n':
                break
            line=line.rstrip()
            lines.append(line)
        self.method=lines[0]
        self.content=lines[1:]

class Response:

    def __init__(self,status,content):

        self.status=status
        self.content=content

    def send(self,f):

        f.write(f'{self.status[0]} {self.status[1]}\n'.encode('utf-8'))
        for item in self.content:
            f.write(f'{item}\n'.encode('utf-8'))
        f.write('\n'.encode('utf-8'))
        f.flush()


def method_PUSH(req,stack):

    if not req.content:
        return Response(STATUS_REQUEST_CONTENT_EMPTY,[])
    aside=[]
    for line in req.content:
        try:
            line_int=int(line)
        except ValueError:
            return Response(STATUS_NOT_A_NUMBER,[])
        if line_int<0:
            return Response(STATUS_NOT_A_NUMBER,[])
        aside.append(line_int)
    stack.extend(aside)
    return Response(STATUS_OK,[])

def method_ADD(req,stack):

    if len(stack)<2:
        return Response(STATUS_STACK_TOO_SHORT,[])
    if req.content:
        return Response(STATUS_REQUEST_CONTENT_NONEMPTY,[])
    n1=stack.pop()
    n2=stack.pop()
    stack.append(n1+n2)
    return Response(STATUS_OK,[])

def method_MULTIPLY(req,stack):

    if len(stack)<2:
        return Response(STATUS_STACK_TOO_SHORT,[])
    if req.content:
        return Response(STATUS_REQUEST_CONTENT_NONEMPTY,[])
    n1=stack.pop()
    n2=stack.pop()
    stack.append(n1*n2)
    return Response(STATUS_OK,[])

def method_PEEK(req,stack):

    if not stack:
        return Response(STATUS_REQUEST_STACK_EMPTY,[])
    if req.content:
        return Response(STATUS_REQUEST_CONTENT_NONEMPTY,[])
    return Response(STATUS_OK,[str(stack[-1])])

def method_ZAP(req,stack):
    
    if req.content:
        return Response(STATUS_REQUEST_CONTENT_NONEMPTY,[])
    stack[:]=[] # del stack[:]
    return Response(STATUS_OK,[])

# Zobrazenie syntax -> spravanie
METHODS={
        'PUSH':method_PUSH,
        'ADD':method_ADD,
        'MULTIPLY':method_MULTIPLY,
        'PEEK':method_PEEK,
        'ZAP':method_ZAP,
        }

def handle_client(cs,addr):
       
        f=cs.makefile('rwb')
        stack=[]
        while True:
            try:
                req=Request(f)
            except ConnectionClosed:
                break
            logging.debug(f'Request method:{req.method} Content:{req.content}')
            if req.method in METHODS:
                response=METHODS[req.method](req,stack)
            else:
                response=Response(STATUS_BAD_REQUEST,[])
            response.send(f)
            if response.status==STATUS_BAD_REQUEST:
                break
        f.close()
        cs.close()


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
