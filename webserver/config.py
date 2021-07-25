import json
import os
from dataclasses import dataclass, field


@dataclass
class Config:
    """
    Config settings for webserver.
    """
    hostname: str = ''
    port: int = 8080
    root: str = 'root'
    log_file: str = 'log.txt'
    max_threads: int = 5
    proxy_pass: field = field(default_factory=lambda: {
        'dir': 'localhost:7080'
    })
    auto_index: bool = True
    index: str = 'index.html'
    keep_alive_timeout: float = 5
    open_file_cache_size: int = 5
    open_file_cache_inactive_time: int = 60
    open_file_cache_errors: bool = True

    def __post_init__(self):
        self.root = os.path.abspath(self.root)
        self.log_file = os.path.abspath(self.log_file)
        self.proxy_pass = {key.strip('/'): value.strip('/')
                           for key, value in self.proxy_pass.items()}

    def load(self, path: str) -> None:
        """
        Update config settings from dictionary with json format in the file.
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
