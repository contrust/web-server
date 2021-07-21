#!/usr/bin/env python3
import argparse
import sys

from webserver.config import Config
from webserver.server import Server


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', metavar='config.json', required=False,
                        help='set config file with .json extension,'
                             ' attributes\' values in config.py are used by default')
    return parser.parse_args()


def main():
    try:
        server_config = Config()
        args_dict = vars(parse_arguments())
        if args_dict['config'] is not None:
            server_config.load(args_dict['config'])
        Server(server_config).start()
    except KeyboardInterrupt:
        print('\r   ')
    except Exception as e:
        print(e)
    finally:
        sys.exit()


if __name__ == '__main__':
    main()

