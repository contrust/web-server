from importlib import import_module
import logging

from webserver.http_message import Request, Response


def try_get_function_response(request: Request, functions: dict) \
        -> Response or None:
    """
    Try to get response from python function, otherwise return None.
    """
    for location in functions:
        if request.path.startswith(f'/{location}/') or not location:
            try:
                p, m = functions[location].rsplit('.', 1)
                mod = import_module(p)
                met = getattr(mod, m)
                return met(request)
            except (ValueError, ModuleNotFoundError, AttributeError) as e:
                logging.getLogger(request.headers['Host']).exception(e)
                return Response(code=500)
    return None


def get_request_information(request):
    response = Response(body=bytes(request))
    return response
