Added
~~~~~

- Request encoding in the SDK will now automatically convert any ``uuid.UUID``
  objects into strings. Previously this was functionality provided by certain
  methods, but now it is universal. (:pr:`NUMBER`)
