#!/usr/bin/env python3

# import necessary libraries
import socket
import re

# FTP Client class to handle FTP operations
class FTPCL:
    def __init__(self, host, port):
        """
        Initialize the FTP client with the host and port.

        Args:
            host (str): the hostname or IP address of the FTP server
            port (int): the port number of the FTP server (default is 21)
        """
        self.ctrl = socket.create_connection((host, port))
        self.host = host
        # reads the welcome message from the server
        self.read_hello()
    
    def send_msg(self, data):
        """
        Sends a message to the FTP server.
        
        Args:
            data (str): the message to send encoded in ASCII
        """
        self.ctrl.sendall(data.encode('ascii'))

    def recv_msg(self, size=4096):
        """
        Receives a message from the FTP server.
        
        Args:
            size (int): the number of bytes to read 
                        from the server (default is 4096)
            
        Returns:
            str: the message received from the server, decoded from ASCII
        """
        return self.ctrl.recv(size).decode('ascii', errors='ignore')
    
    def recv_line(self):
        """
        Receives a line from the FTP server until a 
        newline character is encountered.
        
        Returns:
            str: the line received from the server
        """
        # initialize an empty buffer to store the line
        buffer = ''
        # loops until a newline character is found
        while True:
            ch = self.ctrl.recv(1).decode('ascii', errors='ignore')
            buffer += ch
            if buffer.endswith("\n"):
                return buffer
            
    def recv_resp(self, expect_code=None):
        """
        Receives a response from the FTP server, 
        checks the response code.
        
        Args:
            expect_code (set): a set of expected response codes (default is None)
            
        Returns:
            tuple: a tuple containing response code and full response line
        """
        line = self.recv_line()
        # checks if the line starts with a digit
        code = int(line[:3])
        if len(line) >3 and line[3] == '-':
            # reads multi-line response
            end = f"{code}"
            while True:
                line = self.recv_line()
                if line.startswith(end):
                    break
        # checks if response code is in expected set
        if expect_code and code not in expect_code:
            raise RuntimeError(f"Incorrect response: {line.strip()}")
        return code, line.strip()

    def read_hello(self):
        """
        Reads the initial welcome message from the FTP server.
        """
        self.recv_resp()

    def user_login(self, user, password=None):
        """
        Logs in to the FTP server with given user info.
        
        Args:
            user (str): the username for login
            password (str): the password for the user (default is None)
        """
        # sends USER command to the server
        self.send_msg(f"USER {user}\r\n")
        # receives response from the server
        # expects either 230 (already logged in) or 331 (password required)
        code, _ = self.recv_resp(expect_code={230, 331})
        if code == 331:
            pw = password or ''
            self.send_msg(f"PASS {pw}\r\n")
            self.recv_resp(expect_code={230})
        # sets transfer type, mode, and structure
        self.send_msg(f"TYPE I\r\n")
        self.recv_resp(expect_code={200})
        self.send_msg(f"MODE S\r\n")
        self.recv_resp(expect_code={200})
        self.send_msg(f"STRU F\r\n")
        self.recv_resp(expect_code={200})

    def quit(self):
        """
        Sends QUIT command to the FTP server and closes the connection
        """
        try:
            self.send_msg(f"QUIT\r\n")
            # expects 221 response code to disconnect
            self.recv_resp(expect_code={221})
        finally:
            self.ctrl.close()

    def pasv(self):
        """
        Starts passive mode for data transfer.
        
        Returns:
            socket: a new socket connection transfer data
        """
        # sends PASV command to the server
        self.send_msg(f"PASV\r\n")
        # expects 227 response code with data connection info
        code, msg = self.recv_resp(expect_code={227})

        # gets port numbers from response message
        found_nums = re.findall(r"(\d+)", msg)
        pt1, pt2 = map(int, found_nums[-2:])
        data_port = (pt1 << 8) + pt2

        # creates new socket connection for data transfer
        return socket.create_connection((self.host, data_port), timeout=5)
    
    def lst(self, path):
        """
        Lists contents of a directory on FTP server.
        
        Args:
            path (str): the path of the directory to list out
        """
        # starts passive mode for data transfer
        sock = self.pasv()
        # sends LIST command to the server
        self.send_msg(f"LIST {path}\r\n")
        # expects 150 response code to be ready for data transfer
        self.recv_resp(expect_code={150})

        # reads data from the socket until the end
        listed = b''
        while True:
            ch = sock.recv(4096)
            if not ch:
                break
            listed += ch
        # closes the data socket and expects 226 response code
        sock.close()
        self.recv_resp(expect_code={226})

        # decodes and prints the listed directory contents
        print(listed.decode('utf-8', errors='ignore'), end='')

    def mkdir(self, path):
        """
        Creates a new directory on FTP server.
        
        Args:
            path (str): the name of the directory to create
        """
        # sends MKD command to create a new directory
        self.send_msg(f"MKD {path}\r\n")
        # expects 257 response code for valid creation
        self.recv_resp(expect_code={257})

    def rm(self, path):
        """
        Removes a file from the FTP server.
        
        Args:
            path (str): the path of the file to remove
        """
        # sends DELE command to delete a file
        self.send_msg(f"DELE {path}\r\n")
        # expects 250 response code for correct deletion
        self.recv_resp(expect_code={250})

    def rmdir(self, path):
        """
        Removes a directory from the FTP server.
        
        Args:
            path (str): the path of the directory to remove
        """
        # sends RMD command to remove a directory
        self.send_msg(f"RMD {path}\r\n")
        # expects 250 response code for correct removal
        self.recv_resp(expect_code={250})

    def upload_file(self, path_local, path_remote):
        """
        Uploads a file to the FTP server.
        
        Args:
            path_local (str): the local path of the file to upload
            path_remote (str): the remote path on the FTP server
        """
        # starts passive mode for data transfer
        sock = self.pasv()
        # sends STOR command to upload a file
        self.send_msg(f"STOR {path_remote}\r\n")
        # expects 150 response code to be ready for data transfer
        self.recv_resp(expect_code={150})

        # opens the local file and reads it in chunks
        with open(path_local, 'rb') as f:
            while True:
                ch = f.read(4096)
                if not ch:
                    break
                sock.sendall(ch)
        sock.close()
        # expects 226 response code for successful upload
        self.recv_resp(expect_code={226})

    def download_file(self, path_remote, path_local):
        """
        Downloads a file from the FTP server.
        
        Args:
            path_remote (str): the remote path of the file to download
            path_local (str): the local path to save the downloaded file
        """
        # starts passive mode for data transfer
        sock = self.pasv()
        # sends RETR command to download a file
        self.send_msg(f"RETR {path_remote}\r\n")
        # expects 150 response code to be ready for data transfer
        self.recv_resp(expect_code={150})

        # opens the local file and writes the received data
        with open(path_local, 'wb') as f:
            while True:
                ch = sock.recv(4096)
                if not ch:
                    break
                f.write(ch)
        sock.close()
        # expects 226 response code for successful download
        self.recv_resp(expect_code={226})


