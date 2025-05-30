#!/usr/bin/env python3

from urllib.parse import urlparse, unquote

class FTPURL:
    def __init__(self, url):
        parsed_url = urlparse(url)
        if parsed_url.scheme.lower() != 'ftp':
            raise ValueError(f"Invalid url, {parsed_url}, must have 'ftp'")
        self.user = unquote(parsed_url.username) if parsed_url.username else 'anonymous'
        self.password = unquote(parsed_url.password) if parsed_url.password else None
        self.host = parsed_url.hostname
        if not self.host:
            raise ValueError("FTP URL must have a host")
        self.port = parsed_url.port or 21
        self.path = parsed_url.path or '/'
