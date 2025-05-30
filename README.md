# FTP Client

## High-Level Approach
I initially approached this as having everything in one big client file, but realized it would just look cleaner and make more sense to separate the URL processing and actual client running, then access them both in the main 4700ftp file. After doing this, I started with ftp_url and building the FTPURL class that parsed the URL and ensured it was valid for the client.
Then with the ftp_client file I built the FTPCL class that manages all the commands, connects and closes to the socket, and opens data channels in passive mode. Having this separate from the URL file made the process of connecting to and sending commands to the client clearer to me, and it is essentially a process of sending command messages, receiving responses, and executing the functionality based on which command.
Finally, the main 4700ftp file combines these, it first parses given command line arguments, checks if the path us an FTP URL, and then runs main() which handles all cases of command lines. 


## Challenges Faced
A major challenge I faced was figuring out how to correctly enter passive (PASV) mode, and actually successfully open a data channel. At first I was getting a lot of timeout issues, which I would test using timeout limits and error statements, and I eventually realized I needed to correctly connect the data sockets back to the control channel host, and not try to get a new one.
Another more minor challenge I faced was assuming I would read line termination until '\r\n', however that would create an infinite loop as it didn't know when to terminate since the server would only read to '\n', but after changing that I no longer ran into the issue.

## Testing
I tested this by utilizing the Khoury Linux environment to ensure network reachability. There, I also tested for all commands, such as 'ls', 'mkdir', 'rmdir', 'rm', 'cp', and 'mv'.
In addition to this, I also checked my error handling by purposely trying invalid URLs, fake files, and invalid user credentials.
To also make it more clear as I was working on it, I added debugging print statements to get a better idea of what was actually going on.


