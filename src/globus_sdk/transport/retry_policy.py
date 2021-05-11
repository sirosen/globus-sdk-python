import time
import typing

import requests


class RetryPolicy:
    max_retries: int = 5
    max_sleep: int = 10

    def _backoff(self, attempt):
        # (0.5s * 2^attempt) results in ~15s of total sleep for 5 retries
        # 2^0 + 2^1 + 2^2 + 2^3 + 2^4 = 31
        # note that additional time can be spent sending the request or waiting for
        # a reply
        time.sleep(0.5 * (2 ** attempt))  # exponential backoff

    def _should_retry_err(self, attempt: int, error: Exception) -> bool:
        if isinstance(error, requests.RequestException):
            self._backoff(attempt)
            return True
        return False

    def _parse_retry_after(self, response: requests.Response) -> typing.Optional[int]:
        val = response.headers.get("Retry-After")
        if val:
            try:
                return int(val)
            except ValueError:
                pass
        return None

    def should_retry(
        self, attempt: int, response: typing.Union[Exception, requests.Response]
    ):
        if attempt > self.max_retries:
            return False
        if isinstance(response, Exception):
            return self._should_retry_err(attempt, response)

        if response.status_code == 429:
            retry_after = self._parse_retry_after(response)
            if retry_after:
                time.sleep(min(retry_after, self.max_sleep))
            else:
                self._backoff(attempt)
            return True

        return False
