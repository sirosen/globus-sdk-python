* Improve handling of array-style API responses (:pr:`NUMBER`)

  * Response objects now define ``__bool__`` as ``bool(data)``. This
    means that ``bool(response)`` could be ``False`` if the data is ``{}``,
    ``[]``, ``0``, or other falsey-types. Previously,
    ``__bool__`` was not defined, meaning it was always ``True``

  * Response objects now define ``__len__`` as ``len(data)``. As a special
    case, if there is no JSON data, ``len(response)`` is always 0

  * ``globus_sdk.response.ArrayResponse`` is a new class which describes
    responses which are expected to hold a top-level array. It satisfies the
    sequence protocol, allowing indexing with integers and slices, and
    iteration over the array data

  * ``globus_sdk.GroupsClient.get_my_groups`` returns an ``ArrayResponse``,
    meaning the response data can now be iterated and otherwise used
