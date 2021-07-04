class Config:
    host: str = ''
    port: int = 8080
    proxy_host: str = 'googl.com'
    proxy_port: int = 80
    proxy_on: bool = True
    connection_timeout: float = 1
    max_threads: int = 5
    proxy_pass: dict[str, str] = {
        '/location/': 'http://www.google.com/suka'
    }
