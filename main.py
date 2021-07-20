import argparse
from config import Config
from server import Server


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', metavar='config.json', required=False,
                        help='set config file with .json extension,'
                             ' attributes\' values in config.py are used by default')
    return parser.parse_args()


def main(args):
    server_config = Config()
    args_dict = vars(args)
    if args_dict['config'] is not None:
        server_config.load(args_dict['config'])
    Server(server_config).start()


if __name__ == '__main__':
    main(parse_arguments())
