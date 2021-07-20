class Config:
    host: str = ''
    port: int = 4235
    connection_timeout: float = 0.3
    max_threads: int = 5
    proxy_pass: dict = {
        '/puck/da': 'localhost:8080/hi',
        '/': 'google.com'
    }
    root: str = 'root'
    auto_index: bool = False
    index: str = 'index.html'
    open_file_cache_size: int = 5
    open_file_cache_inactive_time: int = 60
    open_file_cache_errors: bool = True
