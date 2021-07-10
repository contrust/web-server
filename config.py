class Config:
    host: str = ''
    port: int = 1925
    connection_timeout: float = 5
    max_threads: int = 5
    proxy_pass: dict[str, str] = {
        '/puck/': 'localhost:8085/hi/',
        '/da/': 'localhost:8085/'
    }
    root: str = 'root'
    auto_index: bool = True
    index: str = 'index.html'
    open_file_cache_size: int = 5
    open_file_cache_inactive_time: int = 60
    open_file_cache_errors: bool = True
