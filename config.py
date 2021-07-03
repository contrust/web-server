class Config:
    host: str = ''
    port: int = 3426
    proxy_host: str = 'www.nginx.org'
    proxy_port: int = 80
    proxy_on: bool = True
    connection_timeout: float = 1
    max_threads: int = 5
