from __future__ import annotations

from globus_sdk.exc import GlobusAPIError


class FlowsAPIError(GlobusAPIError):
    """
    Error class to represent error responses from Flows.
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

    def _parse_messages(self) -> None:
        if isinstance(self._dict_data.get("error"), dict) and isinstance(
            self._dict_data["error"].get("detail"), list
        ):
            for error_detail in self._dict_data["error"]["detail"]:
                if isinstance(error_detail, dict) and isinstance(
                    error_detail.get("msg"), str
                ):
                    self.messages.append(error_detail["msg"])
        else:
            super()._parse_messages()
