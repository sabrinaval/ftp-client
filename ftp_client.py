#!/usr/bin/env python3

import socket
import re

class FTPCL:
    def __init__(self, host, port):
        self.ctrl = socket.create_connection((host, port))
        self.host = host
        self.read_hello()
    
    def send_msg(self, data):
        self.ctrl.sendall(data.encode('ascii'))

    def recv_msg(self, size=4096):
        return self.ctrl.recv(size).decode('ascii', errors='ignore')
    
    def recv_line(self):
        buffer = ''
        while True:
            ch = self.ctrl.recv(1).decode('ascii', errors='ignore')
            buffer += ch
            if buffer.endswith("\n"):
                return buffer
            
    def recv_resp(self, expect_code=None):
        line = self.recv_line()
        code = int(line[:3])
        if len(line) >3 and line[3] == '-':
            end = f"{code}"
            while True:
                line = self.recv_line()
                if line.startswith(end):
                    break
        if expect_code and code not in expect_code:
            raise RuntimeError(f"Incorrect response: {line.strip()}")
        return code, line.strip()

    def read_hello(self):
        self.recv_resp()

    def user_login(self, user, password=None):
        self.send_msg(f"USER {user}\r\n")
        code, _ = self.recv_resp(expect_code={230, 331})
        if code == 331:
            pw = password or ''
            self.send_msg(f"PASS {pw}\r\n")
            self.recv_resp(expect_code={230})
        self.send_msg(f"TYPE I\r\n")
        self.recv_resp(expect_code={200})
        self.send_msg(f"MODE S\r\n")
        self.recv_resp(expect_code={200})
        self.send_msg(f"STRU F\r\n")
        self.recv_resp(expect_code={200})

    def quit(self):
        try:
            self.send_msg(f"QUIT\r\n")
            self.recv_resp(expect_code={221})
        finally:
            self.ctrl.close()

    def pasv(self):
        self.send_msg(f"PASV\r\n")
        code, msg = self.recv_resp(expect_code={227})
        found_nums = re.findall(r"(\d+)", msg)
        pt1, pt2 = map(int, found_nums[-2:])
        # data_host = f"{hd1}.{hd2}.{hd3}.{hd4}"
        data_port = (pt1 << 8) + pt2
        return socket.create_connection((self.host, data_port), timeout=5)
    
    def lst(self, path):
        sock = self.pasv()
        self.send_msg(f"LIST {path}\r\n")
        self.recv_resp(expect_code={150})
        listed = b''
        while True:
            ch = sock.recv(4096)
            if not ch:
                break
            listed += ch
        sock.close()
        self.recv_resp(expect_code={226})
        print(listed.decode('utf-8', errors='ignore'), end='')

    def mkdir(self, path):
        self.send_msg(f"MKD {path}\r\n")
        self.recv_resp(expect_code={257})

    def rm(self, path):
        self.send_msg(f"DELE {path}\r\n")
        self.recv_resp(expect_code={250})

    def rmdir(self, path):
        self.send_msg(f"RMD {path}\r\n")
        self.recv_resp(expect_code={250})

    def upload_file(self, path_local, path_remote):
        sock = self.pasv()
        self.send_msg(f"STOR {path_remote}\r\n")
        self.recv_resp(expect_code={150})
        with open(path_local, 'rb') as f:
            while True:
                ch = f.read(4096)
                if not ch:
                    break
                sock.sendall(ch)
        sock.close()
        self.recv_resp(expect_code={226})

    def download_file(self, path_remote, path_local):
        sock = self.pasv()
        self.send_msg(f"RETR {path_remote}\r\n")
        self.recv_resp(expect_code={150})
        with open(path_local, 'wb') as f:
            while True:
                ch = sock.recv(4096)
                if not ch:
                    break
                f.write(ch)
        sock.close()
        self.recv_resp(expect_code={226})


