import requests


class RequestEncoder:
    """
    A RequestEncoder takes input parameters and outputs a requests.Requests object.
    """

    def encode(self, method, url, params, data, headers) -> requests.Request:
        if not isinstance(data, (str, bytes)):
            raise TypeError(
                "Cannot encode non-text in a text request. "
                "Either manually encode the data or use `encoding=form|json` to "
                "correctly format this data."
            )
        return requests.Request(method, url, data=data, params=params, headers=headers)


class JSONRequestEncoder(RequestEncoder):
    def encode(self, method, url, params, data, headers):
        if data is not None:
            headers = {"Content-Type": "application/json", **headers}
        return requests.Request(method, url, json=data, params=params, headers=headers)


class FormRequestEncoder(RequestEncoder):
    def encode(self, method, url, params, data, headers):
        if not isinstance(data, dict):
            raise TypeError("FormRequestEncoder cannot encode non-dict data")
        return requests.Request(method, url, data=data, params=params, headers=headers)
