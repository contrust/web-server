#!/usr/bin/env python3
import argparse
import sys
from webserver.config import Config
from webserver.server import Server


def parse_arguments():
    parser = argparse.ArgumentParser(
        prog=None if not globals().get('__spec__')
        else f'python3 -m {__spec__.name.partition(".")[0]}'
    )
    parser.add_argument('-c', '--config', metavar='CONFIG', required=False,
                        help='run server with config file containing '
                             'dictionary with json format, '
                             'config.py values are used by default '
                             'if they are not mentioned in this file')
    parser.add_argument('--get-config', metavar='OUTPUT_FILE', required=False,
                        help='get config file with default values '
                             'in current directory and exit')
    parser.add_argument('--doc', required=False,
                        help='get config docs in console and exit',
                        action='store_true')
    return parser.parse_args()


def main():
    try:
        config = Config()
        args_dict = vars(parse_arguments())
        if args_dict['doc']:
            print(help(Config))
            sys.exit()
        if args_dict['get_config']:
            config.unload(args_dict['get_config'])
            sys.exit()
        if args_dict['config']:
            config.load(args_dict['config'])
        server = Server(config)
        server.run()
    except KeyboardInterrupt:
        print('\r   ')
    finally:
        sys.exit()


if __name__ == '__main__':
    main()
