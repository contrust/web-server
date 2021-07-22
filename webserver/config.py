import json
from dataclasses import dataclass, field


@dataclass
class Config:
    host: str = ''
    port: int = 8080
    root: str = 'root'
    max_threads: int = 5
    proxy_pass: dict = field(default_factory=lambda: {
        '/proxy': 'localhost:7080/test'
    })
    auto_index: bool = True
    index: str = 'index.html'
    connection_timeout: float = 0.3
    open_file_cache_size: int = 5
    open_file_cache_inactive_time: int = 60
    open_file_cache_errors: bool = True

    def load(self, path: str) -> None:
        with open(path) as json_file:
            data = json.load(json_file)
            self.__dict__.update(data)

    def unload(self, path: str) -> None:
        with open(path, mode='w') as file:
            print(self.__dict__)
            json.dump(self.__dict__, file, indent=4)
