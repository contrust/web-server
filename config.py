class Config:
    host: str = ''
    port: int = 8080
    connection_timeout: float = 1
    max_threads: int = 5
    proxy_pass: dict[str, str] = {
        '/': 'http://www.google.com/server/'
    }
