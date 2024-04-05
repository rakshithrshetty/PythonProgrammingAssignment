import argparse
import socket
import sys
import configparser
import os
from time import sleep
import pickle


def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("server_name", help="Enter Name", type=str, choices=['/DFS1', '/DFS2', '/DFS3', '/DFS4'])
    parser.add_argument("server_port", help="Enter the port number", type=int)
    arg = parser.parse_args()
    return arg.server_name, arg.server_port


def create_socket(server_ip, server_port, credential):

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((server_ip, server_port))
    server_socket.listen(5)
    print("The server is ready to receive")

    while True:
        conn, address = server_socket.accept()
        print("Connected with Server IP and Port:", address)
        user = conn.recv(2048).decode()
        sleep(0.1)
        password = conn.recv(2048).decode()
        try:
            if credential[user] == password:
                print('Given Username and Password is Valid')
                conn.send(b"VALID")
            else:
                conn.send(b"INVALID")
                print("Password entered is incorrect")
        except KeyError or configparser.NoOptionError:
            conn.send(b"INVALID")
            print("Username entered is incorrect")

        username = conn.recv(2048).decode()
        sleep(0.1)
        function_password = conn.recv(2048).decode()
        try:
            if credential[username] == function_password:
                print('Authentication Successful')
                conn.send(b"VALID")
                user_function = conn.recv(2048).decode()
                sleep(0.1)
                if not os.path.exists('./' + username):
                    os.makedirs('./' + username)

                # Put Function Starts Here
                if user_function == 'put':
                    for i in range(0, 2):
                        filename = conn.recv(2048).decode()
                        print('Beginning to receive ', filename, ' on server')
                        sleep(0.1)
                        start = conn.recv(2048).decode()
                        print('Starting to receive the file', filename)
                        if start == 'Begin':
                            os.chdir('./' + username)
                            with open(filename, 'wb') as f:
                                while True:
                                    data = conn.recv(2048)
                                    print("receiving")
                                    try:
                                        if data.decode() == 'End':
                                            print(data)
                                            break
                                    except UnicodeDecodeError:
                                        pass
                                    f.write(data)
                                f.close()
                                os.chdir('../')
                elif user_function == 'list':
                    file_list = os.listdir('./'+username)
                    file_list = pickle.dumps(file_list)
                    sleep(0.1)
                    conn.send(file_list)
                elif user_function == 'get':
                    file_list1 = os.listdir('./' + username)
                    file_list = pickle.dumps(file_list1)
                    conn.send(file_list)
                    status = conn.recv(2048)
                    sleep(0.1)
                    fil_name = conn.recv(2048).decode()
                    if status == b'checked_file':
                        print('Preparing to send the', fil_name)
                        want_file = []
                        for i in range(len(file_list1)):
                            if file_list1[i].startswith('.'+fil_name):
                                want_file.append(file_list1[i])
                        sleep(0.1)
                        check = conn.recv(2048)
                        if check == b'send':
                            os.chdir('./'+username)
                            for i in range(len(want_file)):
                                sleep(0.1)
                                temp = want_file[i][-1:]
                                conn.send(temp.encode())
                                sleep(1)
                                conn.send(b"Begin")
                                with open(want_file[i], 'rb') as f:
                                    try:
                                        data = f.read(2048)
                                    except UnicodeDecodeError:
                                        pass
                                    sleep(0.1)
                                    while data:
                                        sleep(0.1)
                                        conn.send(data)
                                        try:
                                            data = f.read(2048)
                                        except UnicodeDecodeError:
                                            pass
                                        sleep(0.1)
                                    conn.send(b'End')

                                    f.close()
                            os.chdir('../')

                    elif status == b'incomplete':
                        print('The required file cannot be sent as it is incomplete')
                        sys.exit()
                else:
                    print("Incorrect Function was entered")
                    sys.exit()

            else:
                conn.send(b"INVALID")
                print("Incorrect Username or Password given by User for the operation")
        except KeyError or configparser.NoOptionError:
            conn.send(b"INVALID")
            print("Incorrect Username or Password given by User for the operation")


if __name__ == "__main__":
    server_names, server_ports = arg_parser()
    if not os.path.exists('.'+server_names):
        os.makedirs('.'+server_names)
    server_ips = '127.0.0.1'
    config = configparser.ConfigParser()
    config.read('dfs.conf')
    credentials = config['Credentials']
    os.chdir('.'+server_names)
    create_socket(server_ips, server_ports, credentials)
