import json
import os
from dataclasses import dataclass
from webserver.log import setup_logger


@dataclass
class Config:
    """
    Config settings for webserver.

    #Attributes:

        hostname (str): hostname of the server

        port (int): port of the server

        root (str): path to directory which will be root of the server

        log_file (str): path to file which will log requests

        max_threads (int): max number of threads for the server

        proxy_pass (dict): dictionary which contains relative to the root paths
        of server directories as keys and paths of proxy directories as values

        python (dict): dictionary which contains relative to the root paths
        of server directories as keys and python functions names as values

        auto_index (bool): if true, for requests which end with '/' server
        gives directory listing as response

        index (str): file which contains directory listing in this directory

        keep_alive_timeout (float): time in seconds which client will have
        after his last request before server closes connection with him

        open_file_cache_size (int): max number of files which can be cached
        simultaneously in server

        open_file_cache_inactive_time (float): max time in seconds which cache
        object can be inactive, after this time it is removed from cache

        open_file_cache_errors (bool): if true, responses with errors
        will be also cached
    """

    def __init__(self):
        self.hostname = 'localhost'
        self.port = 2020
        self.servers = {
            "default": {
                "root": "root",
                "log_file": "log.txt",
                "proxy_pass": {
                    "wiki": "https://en.wikipedia.org/wiki/Main_Page"
                },
                "python": {
                    "info": "webserver.function.get_request_information"
                },
                "auto_index": True
            }
        }
        self.max_threads = 5
        self.index = 'index.html'
        self.keep_alive_timeout = 5
        self.open_file_cache_size: int = 5
        self.open_file_cache_inactive_time: float = 60
        self.open_file_cache_errors: bool = True

    def __post_init__(self):
        for hostname in self.servers:
            for key in self.servers['default']:
                if key not in self.servers[hostname]:
                    self.servers[hostname][key] = self.servers['default'][key]
        for hostname in self.servers:
            self.servers[hostname]['root'] = os.path.abspath(
                self.servers[hostname]['root'])
            self.servers[hostname]['log_file'] = os.path.abspath(
                self.servers[hostname]['log_file'])
            self.servers[hostname]['proxy_pass'] = {
                key.strip('/'): value.strip('/')
                for key, value in self.servers[hostname]['proxy_pass'].items()}
            self.servers[hostname]['python'] = {
                key.strip('/'): value.strip('/')
                for key, value in self.servers[hostname]['python'].items()}
        host = f'{self.hostname}:{self.port}'
        self.servers[host] = self.servers['default']
        for hostname in self.servers:
            setup_logger(hostname, self.servers[hostname]['log_file'])

    def load(self, path: str) -> None:
        """
        Update config settings from the file
        containing dictionary with json format.
        """
        with open(path) as json_file:
            data = json.load(json_file)
            self.__dict__.update(data)
            self.__post_init__()

    def unload(self, path: str) -> None:
        """
        Unload default config settings in the file.
        """
        with open(path, mode='w') as file:
            json.dump(self.__dict__, file, indent=4)
