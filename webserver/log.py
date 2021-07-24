from datetime import datetime, timezone

from webserver.http_message import Request, Response


def get_log_message(client: str,
                    request: Request,
                    response: Response,
                    processing_time: float) -> str:
    return f"{client} - - " \
           f"[{datetime.now(timezone.utc).strftime('%d/%b/%Y:%H:%M:%S %z')}]" \
           f" \"" \
           f"{request.line}\" " \
           f"{response.code} {response.headers.get('Content-Length', 0)} \"" \
           f"{request.headers.get('Referer', '-')}\" \"" \
           f"{request.headers.get('User-Agent', '-')}\" " \
           f"{int(processing_time * 1000)}"
