import socket
import os
import sys
import threading
import logging
import os.path
import os
import email.utils

logging.basicConfig(level=logging.DEBUG)

DOCUMENT_ROOT='documents'

STATUS_OK=200
STATUS_NOT_FOUND=404

STATUS_DESC={
        STATUS_OK:'OK',
        STATUS_NOT_FOUND:'Not found',
}

MIME_TYPES={
        'html':'text/html',
        'txt':'text/plain',
        'jpg':'image/jpeg',
        'png':'image/png',
        }

class ConnectionClosed(Exception):

    pass

class Request:

    def __init__(self,f):
        
        lines=[]
        while True:
            line_b=f.readline()
            if not line_b:
                raise ConnectionClosed
            line=line_b.decode('ASCII')
            line=line.strip()
            if not line:
                break
            lines.append(line)
        self.method,self.url,self.version=lines[0].split()
        self.headers={}
        for line in lines[1:]:
            header,value=line.split(' ',1)
            self.headers[header[:-1]]=value

class Response:

    def __init__(self,status,headers,content):

        self.status=status
        self.headers=headers
        self.content=content

    def send(self,f):

        text_send=[]
        text_send.append(f'HTTP/1.1 {self.status} {STATUS_DESC[self.status]}')
        for header in self.headers:
            text_send.append(f'{header}: {self.headers[header]}')
        text_send.append('')
        for line in text_send:
            logging.debug(f'sending <{line}>')
            f.write((line+'\r\n').encode('ASCII'))
        f.write(self.content)
        f.flush()

class ErrorResponse(Response):

    def __init__(self,status):
        
        content=f'''<html>
        <body>
        <h1>
        {status} {STATUS_DESC[status]}
        </h1>
        </body>
        </html>'''.encode('ASCII')
        headers={
                'Content-type':'text/html',
                'Content-length':f'{len(content)}',
        }
        super().__init__(status,headers,content)


def handle_client(cs,addr):
       
        f=cs.makefile('rwb')
        try:
            while True:
                req=Request(f)
                logging.debug(f'URL:{req.url}')
                logging.debug(f'headers:{req.headers}')
                filename=DOCUMENT_ROOT+req.url
                base,ext=os.path.splitext(filename)
                if ext:
                    ext=ext[1:]
                if ext in MIME_TYPES:
                    content_type=MIME_TYPES[ext]
                else:
                    content_type='application/octet-stream'
                try:
                    with open(filename,'rb') as fd:
                        content=fd.read()
                    last_modified=email.utils.formatdate(os.stat('/etc/passwd').st_mtime)
                    headers={
                            'Last-modified:':last_modified,
                            'Content-type':content_type,
                            'Content-length':f'{len(content)}'
                    }
                    resp=Response(STATUS_OK,headers,content)
                except FileNotFoundError:
                    resp=ErrorResponse(STATUS_NOT_FOUND)
                resp.send(f)

        except ConnectionClosed:
            logging.debug(f'disconnected {addr}')


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
