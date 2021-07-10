class Config:
    host: str = ''
    port: int = 6444
    connection_timeout: float = 5
    max_threads: int = 5
    proxy_pass: dict[str, str] = {
        '/puck/': 'localhost:8085/hi/',
        '/da/': 'localhost:8085/'
    }
    root: str = 'root'
    auto_index: bool = True
    index: str = 'index.html'
