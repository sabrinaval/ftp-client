#!/usr/bin/env python3

from urllib.parse import urlparse, unquote

class FTPURL:
    def __init__(self, url):
        """
        Initialize the FTPURL object by parsing the given FTP URL.
        
        Args:
            url (str): the FTP URL to parse, must start with 'ftp://'
        
        Raises:
            ValueError: URL is invalid, must have 'ftp' scheme
        """
        # parse URL
        parsed_url = urlparse(url)

        # check if the URL scheme is 'ftp'
        if parsed_url.scheme.lower() != 'ftp':
            raise ValueError(f"Invalid url, {parsed_url}, must have 'ftp'")
        
        # extract components from the parsed URL
        self.user = unquote(parsed_url.username) if parsed_url.username else 'anonymous' # default to 'anonymous'
        self.password = unquote(parsed_url.password) if parsed_url.password else None # default to None
        self.host = parsed_url.hostname
        if not self.host:
            raise ValueError("FTP URL must have a host")
        self.port = parsed_url.port or 21  # default FTP port
        self.path = parsed_url.path or '/' # default to root directory
