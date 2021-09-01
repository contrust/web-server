import logging

from webserver.http_message import Request, Response

FORMATTER = logging.Formatter('[%(asctime)s] - %(levelname)s - %(message)s')


def setup_logger(name, log_file, level=logging.INFO):
    """To setup as many loggers as you want"""

    handler = logging.FileHandler(log_file)
    handler.setFormatter(FORMATTER)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


def get_log_message(client: str,
                    request: Request,
                    response: Response,
                    processing_time: float) -> str:
    return f"{client} \"" \
           f"{request.line}\" " \
           f"{response.code} {response.headers.get('Content-Length', 0)} \"" \
           f"{request.headers.get('Referer', '-')}\" \"" \
           f"{request.headers.get('User-Agent', '-')}\" " \
           f"{int(processing_time * 1000)}"
