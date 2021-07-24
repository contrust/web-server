import json
import os
from dataclasses import dataclass, field


def get_abs_path(path: str) -> str:
    """
    Get absolute path from relative path to this file.
    If it is absolute, it remains the same.
    """
    return f'{os.path.dirname(__file__)}{os.path.sep}{path}' \
        if not os.path.isabs(path) else path


@dataclass
class Config:
    """
    Config settings for webserver.

    Attributes: # noqa
        fds (fd) =fds
    All the paths should not start and end with slash and dot characters.
    Root and log paths can be absolute or relative to this file.
    Proxy_pass is a dictionary containing server directories as keys
    and proxy server directories as values, '' key proxies the root.
    If auto_index is True, all the requests
    ending with the slash character (‘/’) produces a directory listing,
    which is located in this directory with certain index name.
    """
    hostname: str = 'localhost'
    port: int = 8080
    root: str = 'root'
    log_file: str = 'log.txt'
    max_threads: int = 5
    proxy_pass: dict = field(default_factory=lambda: {
        'dir': 'localhost:7080'
    })
    auto_index: bool = True
    index: str = 'index.html'
    keep_alive_timeout: float = 5
    open_file_cache_size: int = 5
    open_file_cache_inactive_time: int = 60
    open_file_cache_errors: bool = True

    root = get_abs_path(root)
    log_file = get_abs_path(log_file)

    def load(self, path: str) -> None:
        """
        Update config settings from dictionary with json format in the file.
        """
        with open(path) as json_file:
            data = json.load(json_file)
            self.__dict__.update(data)

    def unload(self, path: str) -> None:
        """
        Unload default config settings in the file.
        """
        with open(path, mode='w') as file:
            json.dump(self.__dict__, file, indent=4)
