# -------------------------------------------
# Module describing factory construction of index kernels.
# -------------------------------------------
from typing import List
from qce_circuit.structure.acquisition_indexing.intrf_stabilizer_index_kernel import IStabilizerIndexingKernel
from qce_circuit.structure.acquisition_indexing.intrf_index_strategy import FixedIndexStrategy


class KernelPartitioner:
    """
    Behaviour class, for slicing/partitioning indexing kernels.
    """

    # region Static Class Methods
    @staticmethod
    def partition_in_equal_sections(index_kernel: IStabilizerIndexingKernel, sections: int) -> List[IStabilizerIndexingKernel]:
        """
        Creates a list of subset kernels based on a self.
        :param index_kernel: The kernel describing the structure of a single subset (cycle).
        :param sections: The number of subsets (partitions) to generate.
        :return: List of independent kernel objects, each pointing to a unique subset of the data.
        """
        subsets: List[IStabilizerIndexingKernel] = []

        # Calculate the cycle length of the template.
        # We assume the template is 'floating', but we need its length.
        # To ensure calculation is correct, we temporarily bind it to 0 to measure length.
        offset_strategy = FixedIndexStrategy(index=index_kernel.start_index)
        experiment_repetitions: int = index_kernel.experiment_repetitions
        subset_repetitions: int = experiment_repetitions // sections

        for i in range(sections):
            # Calculate absolute start index for this subset
            subset_start_index = offset_strategy.index + (i * subset_repetitions * index_kernel.kernel_cycle_length)

            # Create strategy for this specific window
            strategy = FixedIndexStrategy(index=subset_start_index)

            # Create the subset kernel using the interface method
            subset_kernel = index_kernel.with_index_strategy(
                strategy=strategy,
                experiment_repetitions=subset_repetitions,
            )
            subsets.append(subset_kernel)

        return subsets
    # endregion
