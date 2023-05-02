from __future__ import annotations

from globus_sdk.exc import GlobusAPIError


class TimerAPIError(GlobusAPIError):
    """
    Error class to represent error responses from Timer.

    Has no particular additions to the base ``GlobusAPIError``, but implements a
    different method for parsing error responses from Timer due to the differences
    between pydantic-generated errors and other errors.
    """

    def _parse_errors_array(self) -> None:
        """
        Treat any top-level "error" key as an "array of size 1".
        Meaning that we'll see a single subdocument for data shaped like
            {
              "error": {
                "foo": "bar"
              }
            }
        """
        if isinstance(self._dict_data.get("error"), dict):
            self.errors = [self._dict_data["error"]]
        else:
            return super()._parse_errors_array()

    def _parse_code(self) -> None:
        if isinstance(self._dict_data.get("detail"), list):
            self.code = "Validation Error"
        else:
            super()._parse_code()

    def _parse_messages(self) -> None:
        """
        The messages are assembled from arrays of validation details when present.
        Error shapes include:

            {
                "detail": [
                    {
                        "loc": ["body", "start"],
                        "msg": "field required",
                        "type": "value_error.missing"
                    },
                    {
                        "loc": ["body", "callback_url"],
                        "msg": "field required",
                        "type": "value_error.missing"
                    }
                ]
            }
        """
        if isinstance(self._dict_data.get("detail"), list):
            self.messages.extend(
                [
                    e["msg"] + ": " + ".".join(k for k in e["loc"])
                    for e in self._dict_data["detail"]
                ]
            )
        else:
            super()._parse_messages()
