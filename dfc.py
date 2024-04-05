import socket
import argparse
import os
import sys
import configparser
from time import sleep
import math
import hashlib
import pickle
from itertools import groupby


def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="Enter the file", type=str)
    arg = parser.parse_args()
    return arg.filename


def file_split(content):
    split_data = [content[i: i + math.ceil(len(content)/4)] for i in range(0, len(content), math.ceil(len(content)/4))]
    return split_data


def md_5(file_name):
    hash_md5 = hashlib.md5()
    with open(file_name, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
        value = hash_md5.hexdigest()
        decision = int(value, 16) % 4
        return decision


def authentication(client_socket, username, password, active_server, inp_file1):
    flag = False
    for item in active_server:
        client_socket[item].send(username.encode())
        sleep(0.1)
        client_socket[item].send(password.encode())
        status = client_socket[item].recv(2048).decode()
        if status == 'VALID':
            flag = True
        else:
            flag = False
        client_socket[item].send(inp_file1.encode())
        sleep(0.1)
    return flag


def selection():
    list = [{}, {}, {}, {}]
    list[0][0] = [0, 1]; list[0][1] = [1, 2]; list[0][2] = [2, 3]; list[0][3] = [3, 0]
    list[1][0] = [3, 0]; list[1][1] = [0, 1]; list[1][2] = [1, 2]; list[1][3] = [2, 3]
    list[2][0] = [2, 3]; list[2][1] = [3, 0]; list[2][2] = [0, 1]; list[2][3] = [1, 2]
    list[3][0] = [1, 2]; list[3][1] = [2, 3]; list[3][2] = [3, 0]; list[3][3] = [0, 1]
    return list


def create_socket(server_ip, server_port, username, password):

    client_socket = []
    for i in range(4):
        client_socket.append(socket.socket(socket.AF_INET, socket.SOCK_STREAM))

    j = 0
    active_server = []
    for ser in server_port:
        try:
            client_socket[j].connect((server_ip, ser))
            active_server.append(j)
            print('Connected to Server:', j)
        except ConnectionRefusedError:
            print('Not Connected to Server', j)
            pass
        j = j+1
    print(active_server)
    for item in active_server:
        client_socket[item].send(username.encode())
        sleep(0.1)
        client_socket[item].send(password.encode())

    print("Got reply back from server!")
    check = []
    for ser in active_server:
        status = client_socket[ser].recv(2048).decode()
        check.append(status)
    print(check)
    if 'INVALID' in check:
        print("Incorrect Username or Password given by User for the operation")
        sys.exit()
    elif 'VALID' in check:
        print("You can perform the following task\n"
              "get <filename> <username> <password>\n"
              "put <filename> <username> <password>\n"
              "list <username> <password>")

        file_name = input("Enter the filename in the given format\n")
        inp_file = file_name.split()
        if inp_file[0] == 'list':
            inp_file.append(inp_file[2])
            inp_file[2] = inp_file[1]
        try:
            authentic = authentication(client_socket, inp_file[2], inp_file[3], active_server, inp_file[0])
        except IndexError:
            print('Incorrect Input')
            sys.exit()
        if authentic:
            if inp_file[0] == 'put':
                if len(active_server) == 4:
                    filename = inp_file[1]
                    with open(filename, 'rb') as f:
                        data = f.read()
                        split = file_split(data)
                        for l in range(0, 4):
                            with open('.' + filename + '.' + str(l), 'wb') as g:
                                g.write(split[l])
                            g.close()

                    f.close()
                    md_value = md_5(inp_file[1])
                    server_decision = selection()
                    server_list = server_decision[md_value]
                    for ser in active_server:
                        file_list = server_list[ser]
                        for i in range(0, 2):
                            print("Starting to send File to ser: ", str(ser))
                            with open('.' + inp_file[1] + '.' + str(file_list[i]), 'rb') as q:
                                try:
                                    data = q.read(2048)
                                except UnicodeDecodeError:
                                    pass
                                client_socket[ser].send(('.' + inp_file[1] + '.' + str(file_list[i])).encode())

                                sleep(0.1)
                                client_socket[ser].send(b"Begin")
                                sleep(0.1)
                                while data:
                                    print("Sending Part "+str(i+1)+" of the File to Server ", str(ser))
                                    sleep(0.1)
                                    client_socket[ser].send(data)
                                    try:
                                        data = q.read(2048)
                                    except UnicodeDecodeError:
                                        pass
                                    sleep(0.1)
                                client_socket[ser].send(b"End")
                                q.close()
                            sleep(0.1)
                else:
                    print("Unable to upload file as 1 or more servers are down")
                    sys.exit()
            elif inp_file[0] == 'list':
                rlist = []
                for ser in active_server:
                    file_list = client_socket[ser].recv(2048)
                    file_list = pickle.loads(file_list)
                    rlist = rlist + file_list
                temp = list(set(rlist))
                temp2 = []
                for i in range(len(temp)):
                    temp3 = temp[i][1:-2]
                    temp2.append(temp3)
                temp2 = sorted(temp2)
                temp4 = [len(list(group)) for key, group in groupby(temp2)]
                temp2 = list(set(temp2))
                print('List of Files in the server are:')
                for i in range(len(temp4)):
                    if temp4[i] == 4:
                        print(temp2[i]+'\n')
                    else:
                        print(temp2[i]+'[INCOMPLETE]\n')
            elif inp_file[0] == 'get':
                rlist = []
                for ser in active_server:
                    file_list = client_socket[ser].recv(2048)
                    file_list = pickle.loads(file_list)
                    rlist = rlist + file_list
                temp = list(set(rlist))
                temp2 = []
                for i in range(len(temp)):
                    temp3 = temp[i][1:-2]
                    temp2.append(temp3)
                temp2 = sorted(temp2)

                temp4 = [len(list(group)) for key, group in groupby(temp2)]
                temp2 = list(set(temp2))
                temp2 = sorted(temp2)
                if inp_file[1] in temp2:
                    for i in range(len(temp2)):
                        if temp2[i] == inp_file[1]:
                            position = i
                else:
                    print("Required File Does not Exist")
                    sys.exit()
                if temp4[position] == 4:
                    for ser in active_server:
                        client_socket[ser].send(b'checked_file')
                        sleep(0.1)
                        client_socket[ser].send(inp_file[1].encode())
                        sleep(0.1)

                    data = [b'', b'', b'', b'']
                    if 0 in active_server:
                        if 2 in active_server:
                            print('Available')
                            active_server1 = [0, 2]
                            for ser in active_server1:
                                client_socket[ser].send(b'send')
                                for i in range(0, 2):
                                    sleep(0.1)
                                    f = client_socket[ser].recv(2048).decode()
                                    f = int(f)
                                    sleep(0.1)
                                    start = client_socket[ser].recv(2048).decode()
                                    if start == 'Begin':
                                        print('Receivng')
                                        while True:
                                            data_temp = client_socket[ser].recv(2048)
                                            try:
                                                if data_temp.decode() == 'End':
                                                    break
                                            except UnicodeDecodeError:
                                                pass
                                            data[f] = data[f] + data_temp
                                            sleep(0.1)

                    elif 1 in active_server:
                        if 3 in active_server:
                            print('Available')
                            active_server2 = [1, 3]
                            for ser in active_server2:
                                client_socket[ser].send(b'send')
                                for i in range(0, 2):
                                    sleep(0.1)
                                    f = client_socket[ser].recv(2048).decode()
                                    print(f)
                                    print(type(f))
                                    f = int(f)
                                    sleep(0.1)
                                    start = client_socket[ser].recv(2048).decode()
                                    if start == 'Begin':
                                        print('Receiving')
                                        while True:
                                            data_temp = client_socket[ser].recv(2048)
                                            try:
                                                if data_temp.decode() == 'End':
                                                    print(data_temp)
                                                    break
                                            except UnicodeDecodeError:
                                                pass
                                            data[f] = data[f] + data_temp
                                            sleep(0.1)

                    else:
                        print('File Not Retrievable because server are down')

                    with open(inp_file[1], 'wb') as f:
                        for i in range(len(data)):
                            f.write(data[i])
                        f.close()

                else:
                    for ser in active_server:
                        client_socket[ser].send(b'incomplete')
                        print('The required file cannot be sent as it is incomplete')
                    sys.exit()

            else:
                print("Incorrect Function was entered")
                sys.exit()

        else:
            print('Incorrect details entered')


if __name__ == '__main__':
    filename = arg_parser()
    ip_Address = '127.0.0.1'
    if os.path.isfile(filename):
        config = configparser.ConfigParser()
        config.read(filename)
        username = config['Credentials']['username']
        password = config['Credentials']['password']
        server_port = [10001, 10002, 10003, 10004]
        create_socket(ip_Address, server_port, username, password)
    else:
        print('Config file not found')
        sys.exit()
