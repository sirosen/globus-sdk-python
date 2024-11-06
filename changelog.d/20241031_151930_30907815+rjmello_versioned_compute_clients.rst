Added
~~~~~

- Created ``ComputeClientV2`` and ``ComputeClientV3`` classes to support Globus Compute
  API versions 2 and 3, respectively. The canonical ``ComputeClient`` is now a subclass
  of ``ComputeClientV2``, preserving backward compatibility. (:pr:`1096`)
