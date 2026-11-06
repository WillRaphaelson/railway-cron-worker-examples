"""Check a URL repeatedly until the worker receives SIGTERM or SIGINT."""
import logging
import signal
from threading import Event

from check_once import check_url

stop = Event()


def request_stop(signum, frame):
    stop.set()


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, request_stop)
    signal.signal(signal.SIGINT, request_stop)
    logging.info("Worker started")
    while not stop.is_set():
        check_url()
        stop.wait(60)
    logging.info("Worker stopped")
