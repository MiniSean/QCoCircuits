# -------------------------------------------
# Module containing utility functions for calculating element combinations.
# -------------------------------------------
from itertools import combinations
from typing import TypeVar, List, Set

T = TypeVar('T')


def generate_unique_subgroup_combinations(elements: List[T], subgroup_size: int = 2) -> List[List[List[T]]]:
    """:return: A list of unique combinations of subgroups, where each subgroup is of specified size."""

    def generate_combinations(remaining_elements: List[T], current_subgroups: List[List[T]], unique_combinations: Set[T]):
        """Recursive helper function to generate unique combinations of elements into subgroups."""
        if not remaining_elements:
            # Sort within each subgroup and then sort the list of subgroups to standardize order
            sorted_subgroups = sorted([sorted(subgroup) for subgroup in current_subgroups])
            unique_combinations.add(tuple([tuple(subgroup) for subgroup in sorted_subgroups]))
            return
        for combination in combinations(remaining_elements, subgroup_size):
            elements_left = remaining_elements.copy()
            for element in combination:
                elements_left.remove(element)
            generate_combinations(elements_left, current_subgroups + [combination], unique_combinations)

    unique_combinations_set = set()
    generate_combinations(elements, [], unique_combinations_set)
    # Convert from tuples back to lists for the output
    return [list(map(list, combo)) for combo in unique_combinations_set]
