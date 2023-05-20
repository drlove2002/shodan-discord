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


def kill_sh_process():
    process = Popen(["ps", "-fC", "sh"], stdout=PIPE, text=True)
    process.wait()
    for output in process.communicate()[0].split("\n"):
        if output and "bot" in output:
            kill(int(output.split()[1]), 9)


def main():
    kill_sh_process()
    while True:
        if is_running(args.pid):
            sleep(1)
            continue

        system(f"python shodan {getpid()}")
        exit(0)


if __name__ == "__main__":
    main()
