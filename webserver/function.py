from importlib import import_module

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
                print(f"{type(e).__name__} at line "
                      f"{e.__traceback__.tb_lineno} of {__file__}: {e}")
                return Response(code=500)
    return None


def get_request_information(request):
    return Response(body=bytes(request))
