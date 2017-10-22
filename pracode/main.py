#!/usr/bin/env python3

import argparse
import logging

from .leetcode import LeetCode


def create_parser():
    parser = argparse.ArgumentParser(
        description='practice your coding skills',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-d', '--debug', dest='debug', action='store_true',
                        default=False, help='debug mode, verbose log')
    return parser


def init_logger(args):
    logger = logging.getLogger('pracode')
    handler = logging.FileHandler('log.txt')
    handler.setFormatter(logging.Formatter('%(asctime)-15s [%(levelname)s] [%(name)-9s] %(message)s'))
    logger.addHandler(handler)

    if args.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.WARN)


def main():
    args = create_parser().parse_args()
    init_logger(args)
    LeetCode().cmdloop()
    print('bye!')


if __name__ == '__main__':
    main()
