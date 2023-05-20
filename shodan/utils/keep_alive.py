from random import randint
from threading import Thread

from flask import Flask

app = Flask('')


@app.route('/')
def home():
	return 'Online...'


def run():
	app.run(
		host='0.0.0.0',
		port=randint(2000, 9000)
	)


def webserver():
	"""Creates and starts new thread that runs the function run."""
	t = Thread(target=run)
	t.start()