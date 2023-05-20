from random import randint
from threading import Thread

from flask import Flask

from shodan.utils.logging import get_logger

logger = get_logger(__name__)
app = Flask("Shodan")


@app.route("/")
def home():
    return "Online..."


def run():
    from waitress import serve

    # set logger
    logger.info("Starting webserver...")
    serve(app, host="0.0.0.0", port=randint(2000, 9000), _quiet=True)


def webserver():
    """Creates and starts new thread that runs the function run."""
    t = Thread(target=run)
    t.start()
