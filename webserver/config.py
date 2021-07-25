import json
import os
from dataclasses import dataclass, field


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
    hostname: str = 'localhost'
    port: int = 2020
    root: str = 'root'
    log_file: str = 'log.txt'
    max_threads: int = 5
    proxy_pass: field = field(default_factory=lambda: {
        'profile': 'https://anytask.org/accounts/profile'
    })
    auto_index: bool = True
    index: str = 'index.html'
    keep_alive_timeout: float = 5
    open_file_cache_size: int = 5
    open_file_cache_inactive_time: float = 60
    open_file_cache_errors: bool = True

    def __post_init__(self):
        self.root = os.path.abspath(self.root)
        self.log_file = os.path.abspath(self.log_file)
        self.proxy_pass = {key.strip('/'): value.strip('/')
                           for key, value in self.proxy_pass.items()}

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
