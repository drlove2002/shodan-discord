from subprocess import Popen, PIPE
from os import kill, system, getpid
from argparse import ArgumentParser
from time import sleep

parser = ArgumentParser(description="Bot's subprocess pid")
parser.add_argument("pid", type=int, nargs="?")
args = parser.parse_args()


#  function to check if the pid is running
def is_running(pid):
    """Check For the existence of a unix pid. if alive then kill it."""
    try:
        kill(pid, 9)
    except OSError:
        return False
    else:
        return True

def main():
    while True:
        if is_running(args.pid):
            sleep(1)
            continue

        system(f"python3 shodan {getpid()}")
        exit(0)


if __name__ == "__main__":
    main()
