# -------------------------------------------
# Module containing utility functions for (re)shaping numpy arrays.
# -------------------------------------------
from typing import List, Iterable


def unique_in_order(iterable: Iterable) -> List:
    """
    Applies set operation to retrieve unique elements from iterable.
    Makes sure the original order of the iterable stays the same.
    """
    seen = set()
    result = []
    for item in iterable:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result
