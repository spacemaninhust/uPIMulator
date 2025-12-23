from typing import List, Optional

import numpy as np

from abi.word.immediate import Immediate
from abi.word.representation import Representation
from assembler.data_prep.bin import Bin
from encoder.byte import Byte
from util.config_loader import ConfigLoader


class GEMMDataPrep:
    def __init__(self, num_tasklets: int, data_prep_param: List[int], num_dpus: int):
        assert 0 < num_tasklets < ConfigLoader.max_num_tasklets()
        assert len(data_prep_param) == 6

        self._num_tasklets: int = num_tasklets
        self._num_dpus: int = num_dpus
        self._num_executions: int = 1

        self._padded_m = data_prep_param[0]
        self._padded_k = data_prep_param[1]
        self._padded_n = data_prep_param[2]
        self._tile_m = data_prep_param[3]
        self._tile_k = data_prep_param[4]
        self._tile_n = data_prep_param[5]

        # Constraint check: tilem * tilek * tilen * ndpu = paddedm * paddedk * paddedn
        total_ops_tile = self._tile_m * self._tile_k * self._tile_n * self._num_dpus
        total_ops_global = self._padded_m * self._padded_k * self._padded_n
        assert total_ops_tile == total_ops_global, \
            f"Constraint failed: tile({total_ops_tile}) != global({total_ops_global})"

        self._buffer_a = []
        self._buffer_b = []
        self._buffer_c = []

        for _ in range(self._num_dpus):
            # Generate random matrices A (tile_m x tile_k) and B (tile_k x tile_n)
            # Using range [0, 10) to keep values small and avoid overflow
            mat_a = np.random.randint(0, 10, size=(self._tile_m, self._tile_k), dtype=np.int32)
            mat_b = np.random.randint(0, 10, size=(self._tile_k, self._tile_n), dtype=np.int32)
            mat_c = np.matmul(mat_a, mat_b)

            self._buffer_a.append(mat_a)
            self._buffer_b.append(mat_b)
            self._buffer_c.append(mat_c)

    def num_executions(self) -> int:
        return self._num_executions

    def num_dpus(self) -> int:
        return self._num_dpus

    def input_dpu_mram_heap_pointer_name(self, execution: int, dpu_id: int) -> Optional[Bin]:
        assert 0 <= execution < self._num_executions
        assert 0 <= dpu_id < self._num_dpus

        # Optimize: Use numpy view to get bytes directly (Little Endian)
        bytes_a = self._buffer_a[dpu_id].astype(np.int32).ravel().view(np.uint8)
        bytes_b = self._buffer_b[dpu_id].astype(np.int32).ravel().view(np.uint8)
        
        all_bytes = np.concatenate((bytes_a, bytes_b))
        bytes_list = [Byte(int(b)) for b in all_bytes]

        return Bin(bytes_list)

    def output_dpu_mram_heap_pointer_name(self, execution: int, dpu_id: int) -> Optional[Bin]:
        assert 0 <= execution < self._num_executions
        assert 0 <= dpu_id < self._num_dpus

        # Optimize: Use numpy view to get bytes directly (Little Endian)
        bytes_a = self._buffer_a[dpu_id].astype(np.int32).ravel().view(np.uint8)
        bytes_b = self._buffer_b[dpu_id].astype(np.int32).ravel().view(np.uint8)
        bytes_c = self._buffer_c[dpu_id].astype(np.int32).ravel().view(np.uint8)

        all_bytes = np.concatenate((bytes_a, bytes_b, bytes_c))
        bytes_list = [Byte(int(b)) for b in all_bytes]

        return Bin(bytes_list)

    def dpu_input_arguments(self, execution: int, dpu_id: int) -> Optional[Bin]:
        assert 0 <= execution < self._num_executions
        assert 0 <= dpu_id < self._num_dpus

        bytes_: List[Byte] = []

        # Pass tile dimensions
        bytes_ += Immediate(Representation.UNSIGNED, 32, self._tile_m).to_bytes()
        bytes_ += Immediate(Representation.UNSIGNED, 32, self._tile_k).to_bytes()
        bytes_ += Immediate(Representation.UNSIGNED, 32, self._tile_n).to_bytes()

        return Bin(bytes_)

    def dpu_results(self, execution: int, dpu_id: int) -> Optional[Bin]:
        return None
