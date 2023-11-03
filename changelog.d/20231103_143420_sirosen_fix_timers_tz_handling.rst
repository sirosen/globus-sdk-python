Fixed
~~~~~

- When serializing ``TransferTimer`` data, do not convert to UTC if the input
  was a valid datetime with an offset. (:pr:`NUMBER`)
