import sys
from argparse import ArgumentParser
from os import environ, kill

from shodan.core.bot import BaseMainBot
from shodan.utils import logging

parser = ArgumentParser(description="restart.py subprocess pid")
parser.add_argument("pid", type=int, nargs="?")
args = parser.parse_args()

bot = BaseMainBot()
logger = logging.get_logger(__name__)


def main():
    if args.pid:
        try:
            kill(args.pid, 9)
        except OSError:
            pass
    bot.run(environ["TOKEN"])


if __name__ == "__main__":
    try:
        if sys.platform not in ("win32", "cygwin", "cli"):
            import uvloop

            uvloop.install()
    except ImportError:
        logger.info("UVLoop can't be installed in windows")
    main()
