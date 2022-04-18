* Several changes expose more details of HTTP requests (:pr:`NUMBER`)
  * ``GlobusAPIError`` has a new property ``headers`` which provides the
    case-insensitive mapping of header values from the response
  * ``GlobusAPIError`` and ``GlobusHTTPResponse`` now include ``http_reason``,
    a string property containing the "reason" from the response
  * ``BaseClient.request`` and ``RequestsTransport.request`` now have options
    for setting boolean options ``allow_redirects`` and ``stream``, controlling
    how requests are processed
