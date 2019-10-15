import sys
import os
import socket
from _thread import *
import hashlib
import time


ip = "localhost"
m = 3
default_port = 4000 
exitprogram = 0

class finger:
    def __init__(self,start,Node):
        self.start = start
        self.node = Node
    def getStart(self):
        return self.start
    
    def getNode(self):
        return self.node

    def update_node(self,node):
        self.node = node

    def printfinger(self):
        print(self.start,self.node)

class Node:
    k = 0
    def __init__(self,port):
        # self.key = get_hash(ip + str(port))
        self.key = get_hash(port)
        self.addr = port
        self.succ = port
        self.secsucc = port
        self.pred = port
        self.fingerTable = []
        self.files = []
        self.clientfiles = []
    
    def update_succ(self,succ):
        self.succ = succ

    def update_pred(self,pred):
        self.pred = pred
    
    def update_files(self,file):
        self.files.append(file)

    def print_info(self):
        print("-----Node Info-----")
        print("Key: ", self.key)
        print("addr: ", self.addr)
        print("Pred: ", self.pred)
        print("Succ: ", self.succ)
        # print("SecSucc: ", self.secsucc)
        # print("--Finger Table:--")
        # for i in self.fingerTable:
        #     print(i.getStart(),i.getNode())
        print("--------------------") 
        for i in self.files:
            print(i)

class obj:
    def __init__(self,key,isNode):
        self.key = key
        self.isNode = isNode


def make_and_sort_tuples(sNode,client):
    arr = []
    nodetup = obj(get_hash(sNode.addr),True)
    clienttup = obj(get_hash(client),True)
    arr.append(nodetup)
    arr.append(clienttup)
    for i in sNode.files:
        arr.append(obj(get_file_hash(i),False))
    
    for i in range(1,len(arr)):
        key=arr[i].key
        k = arr[i]
        j=i-1
        while j>=0 and key < arr[j].key:
            arr[j+1] = arr[j]
            j -= 1
        arr[j+1]=k
    return arr

def my_client_fileHashes(sNode,client):
    arr = make_and_sort_tuples(sNode,client)
    count = 0
    start = 0
    end = 0
    startNodeKey = 0
    endNodeKey = 0
    for i in range(len(arr)):
        if arr[i].isNode==True and count==0:
            start = i
            startNodeKey = arr[i].key
            count = count + 1
        if arr[i].isNode==True and count==1:
            end = i
            endNodeKey = arr[i].key
    
    temparr = []
    for i in range(start+1,end):
        temparr.append(arr[i].key)
    
    temparr2 = []
    for i in range(len(arr)):
        if arr[i].key not in temparr:
            temparr2.append(arr[i].key)
        
    if endNodeKey==get_hash(sNode.addr):
        return temparr2
    else:
        return temparr


    
def get_file_hash(myfile):
    if 'txt' in myfile:
        myfile = myfile.replace('.txt','')
    elif 'docx' in myfile:
        myfile = myfile.replace('.docx','')
    elif 'mp4' in myfile:
        myfile = myfile.replace('.mp4','')

    myfile = int(myfile)
    return myfile % pow(2,m)


def get_file_sorted_array(addr,succ,pred,myfile):
    arr = []
    arr.append(get_hash(addr))
    arr.append(get_hash(succ))
    arr.append(get_hash(pred))
    arr.append(get_file_hash(myfile))
    arr.sort()
    return arr

def get_file_succ(addr,succ,pred,myfile):
    arr = get_file_sorted_array(addr,succ,pred,myfile)
    for i in range(0,len(arr)):
        if arr[i] == get_file_hash(myfile):   
            if i == len(arr)-1:
                return arr[0]
            else:
                return arr[i+1]

def get_file_succ_port(sNode,myfile):
    addr = sNode.addr
    succ = sNode.succ
    pred = sNode.pred
    succ_key = get_file_succ(addr,succ,pred,myfile)
    arr = []
    arr.append(addr)
    arr.append(succ)
    arr.append(pred)
    for i in arr:
        if get_hash(i)==succ_key:
            return i
    return -1

def get_file_best_succ(sNode,myfile):
    temp_succ_port1 = get_file_succ_port(sNode,myfile)
    while True:
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        soc.connect((ip,temp_succ_port1))
        msg = "GET_FILE_TEMP_SUCC"
        msg = msg.encode('utf-8')
        soc.sendall(msg)
        ack = soc.recv(1024)
        soc.sendall((str(sNode.addr)).encode('utf-8'))
        ack = soc.recv(1024)
        soc.sendall(myfile.encode('utf-8'))
        succ_from_temp_succ_port1 = soc.recv(1024)
        succ_from_temp_succ_port1 = int(succ_from_temp_succ_port1.decode('utf-8'))
        soc.close()
        print("SUCC FROM ", temp_succ_port1, "is: ", succ_from_temp_succ_port1)
        if(temp_succ_port1==succ_from_temp_succ_port1):
            return temp_succ_port1
        else:
            temp_succ_port1 = succ_from_temp_succ_port1

def save_file(sock,Node,filename):
    print('Saving File...')

    data = sock.recv(1024)
    f = open(filename, 'wb')
    while data != bytes(''.encode()):
        f.write(data)
        data = sock.recv(1024)
    
    print("FILE DOWNLOAD: SUCCESS")
    f.close()


def send_file(ssock,myfile,sNode):
    print("Sending File....")

    f = open(myfile,'rb')
    data = f.read(1024)
    ssock.sendall(data)

    while data != bytes(''.encode()):
        data = f.read(1024)
        ssock.sendall(data)
    
    f.close()
    print("Success: File Sent ")

def get_hash(port):
    #sha1 takes in str values hash
    # return hashlib.sha1(ip_port).hexdigest()
    return port % pow(2,m)

def get_sorted_array(addr,succ,pred,client_Port):
    arr = []
    arr.append(get_hash(addr))
    arr.append(get_hash(succ))
    arr.append(get_hash(pred))
    arr.append(get_hash(client_Port))
    arr.sort()
    return arr

def get_pred(addr,succ,pred,client_Port):
    arr = get_sorted_array(addr,succ,pred,client_Port)
    for i in range(0,len(arr)):
        if arr[i] == get_hash(client_Port):
            if(i==0):
                return arr[len(arr)-1]
            else:
                return arr[i-1]

def get_pred_port(sNode,client_Port):
    addr = sNode.addr
    succ = sNode.succ
    pred = sNode.pred
    succ_key = get_pred(addr,succ,pred,client_Port)
    arr = []
    arr.append(addr)
    arr.append(succ)
    arr.append(pred)
    arr.append(client_Port)
    for i in arr:
        if get_hash(i)==succ_key:
            return i
    return -1


def get_succ(sNode,client_Port):
    addr = sNode.addr
    succ = sNode.succ
    pred = sNode.pred
    arr = get_sorted_array(addr,succ,pred,client_Port)
    for i in range(0,len(arr)):
        if arr[i] == get_hash(client_Port):
            if(i==len(arr)-1):
                return arr[0]
            else:
                return arr[i+1]

def get_succ_port(sNode,client_Port):
    addr = sNode.addr
    succ = sNode.succ
    pred = sNode.pred
    succ_key = get_succ(sNode,client_Port)
    arr = []
    arr.append(addr)
    arr.append(succ)
    arr.append(pred)
    arr.append(client_Port)
    for i in arr:
        if get_hash(i)==succ_key:
            return i
    return -1


def server_side(client_sock,sNode):
    query = client_sock.recv(1024)
    query = query.decode('utf-8')
    ACK = "ACK"
    ACK = ACK.encode('utf-8')
    client_sock.sendall(ACK)
    client_Port = int(((client_sock.recv(1024)).decode('utf-8')))
    print(client_Port)
    
    if query=="JOIN":
        if sNode.addr==sNode.succ and sNode.addr==sNode.pred:
            msg = "ONLY_ONE_PEER"
            msg = msg.encode('utf-8')
            client_sock.sendall(msg)
            sNode.succ = client_Port
            sNode.pred = client_Port
            print((get_hash(client_Port), client_Port), " JOINED ",(sNode.key, sNode.addr))
        else:
            temp_succ_port = get_succ_port(sNode,client_Port)
            temp_pred_port = get_pred_port(sNode,client_Port)
            print("TEMP_PRED_PORT requested by", client_Port, "is" ,temp_pred_port)
            msg = "MORE_PEERS"
            msg = msg.encode('utf-8')
            client_sock.sendall(msg)
            msg = str(temp_succ_port)
            msg = msg.encode('utf-8')
            client_sock.sendall(msg)
            ACK = client_sock.recv(1024)
            msg = str(temp_pred_port)
            msg = msg.encode('utf-8')
            client_sock.sendall(msg)
            # (client_sock.recv(1024)).decode('utf-8')
    elif query=="GET_TEMP_SUCC":
        temp_succ_port = get_succ_port(sNode,client_Port)
        msg = str(temp_succ_port)
        msg = msg.encode('utf-8')
        client_sock.sendall(msg)
        action = client_sock.recv(1024)
        action = action.decode('utf-8')
        if action=="UPDATE_PRED":
            sNode.pred = int((client_sock.recv(1024)).decode('utf-8'))
    
    elif query=="GET_FILE_TEMP_SUCC":
        ACK = "ACK"
        ACK = ACK.encode('utf-8')
        client_sock.sendall(ACK)
        filename = client_sock.recv(1024).decode('utf-8')
        temp_succ_port = get_file_succ_port(sNode,filename)
        msg = str(temp_succ_port)
        msg = msg.encode('utf-8')
        client_sock.sendall(msg)

    
    elif query=="UPDATE_SUCC":
        sNode.succ = int((client_sock.recv(1024)).decode('utf-8'))
        ACK = "ACK"
        ACK = ACK.encode('utf-8')
        client_sock.sendall(ACK)
    elif query=="LEAVING_UPDATE_SUCC":
        ACK = "ACK"
        ACK = ACK.encode('utf-8')
        client_sock.sendall(ACK)
        sNode.succ = client_sock.recv(1024)
        sNode.succ = (sNode.succ).decode('utf-8')
        sNode.succ = int(sNode.succ)

    elif query=="LEAVING_UPDATE_PRED":
        ACK = "ACK"
        ACK = ACK.encode('utf-8')
        client_sock.sendall(ACK)
        sNode.pred = client_sock.recv(1024)
        sNode.pred = (sNode.pred).decode('utf-8')
        sNode.pred = int(sNode.pred)
    
    elif query=="LEAVING_ONLY_TWO_PEER":
        sNode.succ = sNode.addr
        sNode.pred = sNode.addr

    elif query == "DOWNLOAD_AND_REMOVE_MULTIPLE_FILE":
        ACK = "ACK"
        ACK = ACK.encode('utf-8')
        client_sock.sendall(ACK)
        filename = client_sock.recv(1024).decode('utf-8')
        filecheck = False
        for i in sNode.files:
            if i == filename:
                filecheck = True
        

        if filecheck == True:
            print(filename,"SENDING FILE FOUND MSG")
            msg = "FILE_FOUND"
            msg = msg.encode('utf-8')
            client_sock.sendall(msg)
            ack = client_sock.recv(1024)
            send_file(client_sock,filename,sNode)
        else:
            msg = "FILE_NOT_FOUND"
            msg = msg.encode('utf-8')
            client_sock.sendall(msg)
        
        sNode.files.remove(filename)
        os.remove(filename)
    
    elif query == "UPLOAD_MULTIPLE_FILES":
        ACK = "ACK"
        ACK = ACK.encode('utf-8')
        client_sock.sendall(ACK)
        filename = client_sock.recv(1024).decode('utf-8')
        ACK = "ACK"
        ACK = ACK.encode('utf-8')
        client_sock.sendall(ACK)
        save_file(client_sock,sNode,filename)
        sNode.files.append(filename)
        print("FILE RECIEVED:", filename)
        
    elif query=="UPLOAD_FILE":
        ACK = "ACK"
        ACK = ACK.encode('utf-8')
        client_sock.sendall(ACK)
        filename = client_sock.recv(1024).decode('utf-8')
        ACK = "ACK"
        ACK = ACK.encode('utf-8')
        client_sock.sendall(ACK)
        save_file(client_sock,sNode,filename)
        sNode.files.append(filename)
        print("FILE RECIEVED:", filename)

    elif query == "DOWNLOAD_FILE":
        ACK = "ACK"
        ACK = ACK.encode('utf-8')
        client_sock.sendall(ACK)
        filename = client_sock.recv(1024).decode('utf-8')
        filecheck = False
        for i in sNode.files:
            if i == filename:
                filecheck = True
        
        if filecheck == True:
            msg = "FILE_FOUND"
            msg = msg.encode('utf-8')
            client_sock.sendall(msg)
            ack = client_sock.recv(1024)
            send_file(client_sock,filename,sNode)
        else:
            msg = "FILE_NOT_FOUND"
            msg = msg.encode('utf-8')
            client_sock.sendall(msg)

    elif query=="REHASH_FILES":
        ACK = "ACK"
        ACK = ACK.encode('utf-8')
        client_sock.sendall(ACK)
        arr = my_client_fileHashes(sNode,client_Port)

        print("MYHASH:", sNode.key)
        print("THESE FILES BELONG TO:", client_Port)
        for i in arr:
            print(i)

        client_files = []
        del_indexes = []
        for i in range(0,len(sNode.files)):
            hashedfile = get_file_hash(sNode.files[i])
            for j in arr:
                if j==hashedfile:
                    client_files.append(sNode.files[i])
                    del_indexes.append(i)
        

        print("sNODE has files = ", len(sNode.files))


        ack = client_sock.recv(1024)
        if len(client_files)==0:
            msg = "REHASHING_NONE_FILES"
            msg = msg.encode('utf-8')
            client_sock.sendall(msg)
        else:
            msg = "REHASHING_N_FILES"
            msg = msg.encode('utf-8')
            client_sock.sendall(msg)
            ack = client_sock.recv(1024)
            client_sock.sendall(str(len(client_files)).encode('utf-8'))
            
            print("REHASHING ", len(client_files), "FILES")

            sNode.client_files = client_files

            for i in client_files:
                print("Rehashing", i)
                client_sock.sendall(i.encode('utf-8'))
                ack = client_sock.recv(1024)

        # copysNodefiles = sNode.files
        # del_indexes.sort(reverse=True)
        # for i in del_indexes:
        #     print("DELETING AT INDEX", i)
        #     del copysNodefiles[int(i)]
        # sNode.files = copysNodefiles

    client_sock.close()



def client_side(Node):
    while True:
        print("")
        print("Enter 1 to print My Information")
        print("Enter 2 to join network")
        print("Enter 3 to download a file")
        print("Enter 4 to upload a file")
        print("Enter 5 to Leave network")

        inp = input("Select option:")
        if inp == '':
            print("INVALID INPUT")
        else:
            inp = int(inp)

            if inp == 1:
                Node.print_info()

            elif inp == 2:
                print("Join Network")
                otherport = input("Enter a node's port through which to join network: ")
                if(otherport):
                    print("Joining..." + otherport)
                    otherport = int(otherport)
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    s.connect((ip,otherport))
                    msg = "JOIN"
                    msg = msg.encode('utf-8')
                    s.sendall(msg)
                    ack = s.recv(1024)
                    s.sendall((str(Node.addr)).encode('utf-8'))
                    res = s.recv(1024)
                    res = res.decode('utf-8')

                    if(res=="ONLY_ONE_PEER"):
                        Node.succ = otherport
                        Node.pred = otherport
                        print((Node.key, Node.addr), " JOINED ", (get_hash(otherport), otherport))
                        # s.close()
                    elif res=="MORE_PEERS":
                        temp_succ_port1 = s.recv(1024)
                        temp_succ_port1 = int(temp_succ_port1.decode('utf-8'))
                        print(temp_succ_port1)
                        ACK = "ACK"
                        ACK = ACK.encode('utf-8')
                        s.sendall(ACK)
                        temp_pred_port1 = s.recv(1024)
                        temp_pred_port1 = (temp_pred_port1).decode('utf-8')
                        print(temp_pred_port1)
                        temp_pred_port1 = int(temp_pred_port1)
                        print("TEMP_SUCC_PORT1", temp_succ_port1, " FROM ", otherport )
                        print("TEMP_PRED_PORT1", temp_pred_port1, " FROM ", otherport )
                        s.close()
                        while True:
                            soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                            soc.connect((ip,temp_succ_port1))
                            msg = "GET_TEMP_SUCC"
                            msg = msg.encode('utf-8')
                            soc.sendall(msg)
                            ack = soc.recv(1024)
                            soc.sendall((str(Node.addr)).encode('utf-8'))
                            succ_from_temp_succ_port1 = soc.recv(1024)
                            succ_from_temp_succ_port1 = int(succ_from_temp_succ_port1.decode('utf-8'))
                            print("SUCC FROM ", temp_succ_port1, "is: ", succ_from_temp_succ_port1)
                            if(temp_succ_port1==succ_from_temp_succ_port1):
                                print("UPDATED SUCC!! NEW SUCC:", temp_succ_port1)
                                Node.succ = temp_succ_port1
                                print("UPDATED PRED!! NEW PRED:", temp_pred_port1)
                                Node.pred = temp_pred_port1
                                
                                msg = "UPDATE_PRED"
                                msg = msg.encode('utf-8')
                                soc.sendall(msg)
                                soc.sendall((str(Node.addr)).encode('utf-8'))
                                soc.close()
                                
                                
                                soc2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                soc2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                                soc2.connect((ip,temp_pred_port1))
                                msg = "UPDATE_SUCC"
                                msg = msg.encode('utf-8')
                                soc2.sendall(msg)
                                ack = soc2.recv(1024)
                                soc2.sendall((str(Node.addr)).encode('utf-8'))
                                soc2.sendall((str(Node.addr)).encode('utf-8'))
                                ack = soc2.recv(1024)
                                soc2.close()
                                break
                            else:
                                temp_pred_port1 = temp_succ_port1
                                temp_succ_port1 = succ_from_temp_succ_port1
                    
                    # RE-DISTRIBUTE/RE_HASH FILES
                    newSoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    newSoc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    newSoc.connect((ip,Node.succ))
                    msg = "REHASH_FILES"
                    msg = msg.encode('utf-8')
                    newSoc.sendall(msg)
                    ack = newSoc.recv(1024)
                    newSoc.sendall((str(Node.addr)).encode('utf-8'))
                    ack = newSoc.recv(1024)
                    ACK = "ACK"
                    ACK = ACK.encode('utf-8')
                    newSoc.sendall(ACK)
                    status = newSoc.recv(1024).decode('utf-8')
                    if status == "REHASHING_NONE_FILES":
                        print("_NO FILES REHASHED_")
                        newSoc.close()
                    elif status == "REHASHING_N_FILES":
                        ACK = "ACK"
                        ACK = ACK.encode('utf-8')
                        newSoc.sendall(ACK)
                        N_files = int(newSoc.recv(1024).decode('utf-8'))
                        print("REHASHING ", N_files , "FILES")
                        for i in range(0,N_files):
                            myfile = newSoc.recv(1024).decode('utf-8')
                            Node.files.append(myfile)
                            ACK = "ACK"
                            ACK = ACK.encode('utf-8')
                            newSoc.sendall(ACK)
                        newSoc.close()
                        
                        for i in range(0,N_files):
                            mysoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            mysoc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                            mysoc.connect((ip,Node.succ))
                            msg = "DOWNLOAD_AND_REMOVE_MULTIPLE_FILE"
                            msg = msg.encode('utf-8')
                            mysoc.sendall(msg)
                            ack = mysoc.recv(1024)
                            mysoc.sendall((str(Node.addr)).encode('utf-8'))
                            ack = mysoc.recv(1024)
                            mysoc.sendall(Node.files[i].encode('utf-8'))
                            status = mysoc.recv(1024).decode('utf-8')
                            print("STATUS:" ,status)
                            if status=="FILE_NOT_FOUND":
                                print("FILE NOT IN NETWORK")
                                mysoc.close()
                            elif status=="FILE_FOUND":
                                print("FILE FOUND!! DOWNLOADING....")
                                ACK = "ACK"
                                ACK = ACK.encode('utf-8')
                                mysoc.sendall(ACK)
                                save_file(mysoc,Node,Node.files[i])
                                mysoc.close()
                            else:
                                print("SOMETHING WENT TERRIBLY WRONG")
                                mysoc.close()

                    else:
                        print("SOMETHING TERRIBLY WENT WRONG WHILE REHASHING FILES")


                else:
                    path = str(os.path.dirname(os.path.abspath(__file__)))
                    files = []
                    # r=root, d=directories, f = files
                    for r, d, f in os.walk(path):
                        for file in f:
                            if '.txt' in file:
                                files.append(file)
                            elif 'docx' in file:
                                files.append(file)
                            elif 'mp4' in file:
                                files.append(file)
                    
                    Node.files = files
                    print("file hashes")
                    for i in files:
                        print(get_file_hash(i))
                    print("---You are the first node in the network---")
                    
            elif inp == 3:
                print("Download File")
                filename = input("Enter File Name:")
                succ = get_file_best_succ(Node,filename)
                if (succ==Node.addr):
                    print("I already have the files")
                else:
                    soc2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    soc2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    soc2.connect((ip,succ))
                    msg = "DOWNLOAD_FILE"
                    msg = msg.encode('utf-8')
                    soc2.sendall(msg)
                    ack = soc2.recv(1024)
                    soc2.sendall((str(Node.addr)).encode('utf-8'))
                    ack = soc2.recv(1024)
                    soc2.sendall(filename.encode('utf-8'))
                    status = soc2.recv(1024).decode('utf-8')
                    print("STATUS:" ,status)
                    if status=="FILE_NOT_FOUND":
                        print("FILE NOT IN NETWORK")
                    elif status=="FILE_FOUND":
                        print("FILE FOUND!! DOWNLOADING....")
                        ACK = "ACK"
                        ACK = ACK.encode('utf-8')
                        soc2.sendall(ACK)
                        save_file(soc2,Node,filename)
                        Node.files.append(filename)
                    else:
                        print("SOMETHING WENT TERRIBLY WRONG")
                    soc2.close()
            elif inp == 5:
                print("LEAVING NETWORK....")
                if Node.addr == Node.succ and Node.addr==Node.pred:
                    print("Left Network")
                    os._exit(1)
                elif Node.succ == Node.pred:
                    #UPDATING PRED AND SUCC
                    print("Left Network")
                    newsoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    newsoc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    newsoc.connect((ip,Node.pred))
                    msg = "LEAVING_ONLY_TWO_PEER"
                    msg = msg.encode('utf-8')
                    newsoc.sendall(msg)
                    ack = newsoc.recv(1024)
                    newsoc.sendall((str(Node.addr)).encode('utf-8'))
                    newsoc.close()

                    #UPLOADING MY FILES TO SUCC BEFORE LEAVING
                    copysNodefiles = Node.files
                    if len(Node.files) > 0:
                        for i in range(0,len(Node.files)):
                            mysoc3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            mysoc3.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                            mysoc3.connect((ip,Node.succ))
                            msg = "UPLOAD_MULTIPLE_FILES"
                            msg = msg.encode('utf-8')
                            mysoc3.sendall(msg)
                            ack = mysoc3.recv(1024)
                            mysoc3.sendall((str(Node.addr)).encode('utf-8'))
                            ack = mysoc3.recv(1024)
                            mysoc3.sendall(Node.files[i].encode('utf-8'))
                            ack = mysoc3.recv(1024)
                            send_file(mysoc3,Node.files[i],Node)
                            print("FILE UPLOADED TO:",Node.succ, "FILE:", Node.files[i])
                            mysoc3.close()

                        for i in reversed(range(len(copysNodefiles))):
                            print("Removing at index", i)
                            os.remove(Node.files[i])
                            del Node.files[i]

                    time.sleep(1)
                    os._exit(1)
                else:
                    print("Left Network")
                    #UPDATING PRED AND SUCC
                    newsoc1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    newsoc1.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    newsoc1.connect((ip,Node.pred))
                    msg = "LEAVING_UPDATE_SUCC"
                    msg = msg.encode('utf-8')
                    newsoc1.sendall(msg)
                    ack = newsoc1.recv(1024)
                    newsoc1.sendall((str(Node.addr)).encode('utf-8'))
                    ack = newsoc1.recv(1024)
                    newsoc1.sendall(str(Node.succ).encode('utf-8'))
                    newsoc1.close()

                    newsoc2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    newsoc2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    newsoc2.connect((ip,Node.succ))
                    msg = "LEAVING_UPDATE_PRED"
                    msg = msg.encode('utf-8')
                    newsoc2.sendall(msg)
                    ack = newsoc2.recv(1024)
                    newsoc2.sendall((str(Node.addr)).encode('utf-8'))
                    ack = newsoc2.recv(1024)
                    newsoc2.sendall(str(Node.pred).encode('utf-8'))
                    newsoc2.close()

                    #UPLOADING MY FILES TO SUCC BEFORE LEAVING
                    copysNodefiles = Node.files
                    if len(Node.files) > 0:
                        for i in range(0,len(Node.files)):
                            mysoc2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            mysoc2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                            mysoc2.connect((ip,Node.succ))
                            msg = "UPLOAD_MULTIPLE_FILES"
                            msg = msg.encode('utf-8')
                            mysoc2.sendall(msg)
                            ack = mysoc2.recv(1024)
                            mysoc2.sendall((str(Node.addr)).encode('utf-8'))
                            ack = mysoc2.recv(1024)
                            mysoc2.sendall(Node.files[i].encode('utf-8'))
                            ack = mysoc2.recv(1024)
                            send_file(mysoc2,Node.files[i],Node)
                            print("FILE UPLOADED TO:",Node.succ, "FILE:", Node.files[i])
                            mysoc2.close()

                        for i in reversed(range(len(copysNodefiles))):
                            print("Removing at index", i)
                            os.remove(Node.files[i])
                            del Node.files[i]

                    time.sleep(1)
                    os._exit(1)
                    break

            elif inp==4:
                print("_UPLOAD FILE_")
                filename = input("ENTER FILE NAME:")
                path = str(os.path.dirname(os.path.abspath(__file__)))
                files = []
                # r=root, d=directories, f = files
                for r, d, f in os.walk(path):
                    for file in f:
                        if '.txt' in file:
                            files.append(file)
                        elif 'docx' in file:
                            files.append(file)
                        elif 'mp4' in file:
                            files.append(file)
                
                if filename in files:
                    succ = get_file_best_succ(Node,filename)
                    mysoc4 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    mysoc4.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    mysoc4.connect((ip,succ))
                    msg = "UPLOAD_FILE"
                    msg = msg.encode('utf-8')
                    mysoc4.sendall(msg)
                    ack = mysoc4.recv(1024)
                    mysoc4.sendall((str(Node.addr)).encode('utf-8'))
                    ack = mysoc4.recv(1024)
                    mysoc4.sendall(filename.encode('utf-8'))
                    ack = mysoc4.recv(1024)
                    send_file(mysoc4,filename,Node)
                    print("FILE UPLOADED TO:",succ, "FILE:", filename)
                    mysoc4.close()
                else:
                    print("NO SUCH FILE YOUR DIRECTORY")
            else:
                print("_____INVALID INPUT____")

if __name__ == '__main__':
    myport = int(sys.argv[1])
    newNode = Node(myport)
    start_new_thread(client_side,(newNode,))
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((ip,myport))
    s.listen(m)
    while True:
        if(exitprogram==1):
            # os._exit(1)
            break
        else:
            client_sock, addr = s.accept()
            start_new_thread(server_side,(client_sock,newNode))