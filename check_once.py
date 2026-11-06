"""Check a URL once; exit 0 for HTTP 2xx and 1 for a failed check."""
import logging
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    stream=sys.stdout,
)


def check_url():
    target = os.environ.get("TARGET_URL", "https://example.com")
    request = Request(target, headers={"User-Agent": "railway-background-example/1.0"})
    try:
        with urlopen(request, timeout=10) as response:
            status = response.status
        if not 200 <= status < 300:
            logging.error("Check failed: HTTP %s", status)
            return False
        logging.info("Check succeeded: HTTP %s", status)
        return True
    except HTTPError as error:
        logging.error("Check failed: HTTP %s", error.code)
        error.close()
    except (URLError, TimeoutError, OSError, ValueError):
        logging.error("Check failed: connection, timeout, or invalid URL")
    return False


if __name__ == "__main__":
    raise SystemExit(0 if check_url() else 1)
