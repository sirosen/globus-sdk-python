"""
Make sure the generated data does not duplicate names
"""

import globus_sdk


def test_no_attribute_names_repeat():
    attribute_sets = globus_sdk._LAZY_IMPORT_TABLE.values()
    collected_attrs = set()
    for attr_set in attribute_sets:
        for attribute in attr_set:
            assert attribute not in collected_attrs
            collected_attrs.add(attribute)
