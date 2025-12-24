from typing import List, Union

import numpy as np

from encoder.byte import Byte


class Bin:
    def __init__(self, bytes_: Union[List[Byte], np.ndarray]):
        self._bytes = bytes_

    def dump(self, filepath: str):
        if isinstance(self._bytes, np.ndarray):
            np.savetxt(filepath, self._bytes.flatten(), fmt='%d')
        else:
            with open(filepath, "w") as file:
                lines = ""
                for byte in self._bytes:
                    lines += f"{byte.value()}\n"
                file.writelines(lines)
