import socket
import selectors
import dataBase


HOST = '192.168.1.129'
PORT = 8888
startMarker = '<'
endMarker = '>'

sel = selectors.DefaultSelector()

lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
lsock.bind((HOST, PORT))
lsock.listen(3)
print('listening on', (HOST, PORT))
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ, data=None)


class Message:
    def __init__(self, selector, sock, addr):
        self.selector = selector
        self.sock = sock
        self.addr = addr


def creating_fd_addr(addr, key,):
    print(key.data)
    ipBase = dataBase.selectAllIP()
    for ips in ipBase:
        for ip in ips:
            if addr == ip:
                return(addr, key.fd)


def accept_wrapper():
    try:
        event = sel.select(timeout=None)
        for key, mask in event:
            sock = key.fileobj
            if key.data is None:
                conn, addr = sock.accept()
                print('accepted connection from:', addr)
                dataBase.update_port_count(addr)
                data = Message(sel, conn, addr)
                events = selectors.EVENT_READ | selectors.EVENT_WRITE
                sel.register(conn, events, data=data)
                return(addr)
    except ConnectionResetError:
        print("one of the clients have shut down!")


def recvData():
    Data = ""
    recvState = True
    appendState = False
    lst = []
    event = sel.select(timeout=None)
    for key, mask in event:
        sock = key.fileobj
        data = key.data
        if key.data is not None:
            if mask & selectors.EVENT_READ:
                while recvState == True:
                    recv_data = sock.recv(1024)
                    if recv_data:
                        recv_data = recv_data.decode('utf-8')
                        if recv_data != " ":
                            for rc in recv_data:
                                if rc == startMarker:
                                    appendState = True
                                elif appendState == True:
                                    if rc != endMarker:
                                        lst.append(rc)
                                    else:
                                        Data = ''.join(lst)
                                        appendState = False
                                        recvState = False
                                        return(Data, data.addr)
                    else:
                        print('closing connection to', data.addr)
                        sel.unregister(sock)
                        sock.close()
                        break


def sendData(send_data, ipAddr):
    event = sel.select(timeout=None)
    for key, mask in event:
        if mask & selectors.EVENT_WRITE:
            data = key.data
            if key.data is not None:
                addr = data.addr
                if addr == ipAddr:
                    sock = key.fileobj
                    sock.send(send_data.encode('utf-8'))
