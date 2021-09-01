#!/usr/bin/env python3
import argparse
import json
import logging
import sys

from webserver.config import Config
from webserver.server import Server


def parse_arguments():
    """
    Parse console arguments.
    """
    parser = argparse.ArgumentParser(
        prog=None if not globals().get('__spec__')
        else f'python3 -m {__spec__.name.partition(".")[0]}'
    )
    parser.add_argument('-c', '--config',
                        metavar='CONFIG_FILE',
                        required=False,
                        help='run server with settings in config file')
    parser.add_argument('-g', '--get-config',
                        metavar='OUTPUT_FILE',
                        required=False,
                        help='get config file with default values and exit')
    parser.add_argument('--config-doc',
                        action='store_true',
                        required=False,
                        help='print config attributes description and exit')
    return parser.parse_args()


def main():
    """
    Process parsed console arguments and run server.
    """
    config = Config()
    args_dict = vars(parse_arguments())
    if args_dict['config_doc']:
        print(config.__doc__)
        sys.exit()
    if args_dict['get_config']:
        try:
            config.unload(args_dict['get_config'])
        except NotADirectoryError as e:
            logging.getLogger('default').exception(e)
        sys.exit()
    if args_dict['config']:
        try:
            config.load(args_dict['config'])
        except (FileNotFoundError, json.decoder.JSONDecodeError) as e:
            logging.getLogger('default').exception(e)
            sys.exit()
    try:
        server = Server(config)
        server.run()
    except KeyboardInterrupt:
        print('\r   ')
    except Exception as e:
        logging.getLogger('default').exception(e)
    finally:
        sys.exit()


if __name__ == '__main__':
    main()
