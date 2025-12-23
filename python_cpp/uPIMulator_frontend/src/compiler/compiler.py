import os
import subprocess
from typing import Set

from util.path_collector import PathCollector


class Compiler:
    def __init__(self):
        pass

    @staticmethod
    def compile_benchmark(benchmark: str, num_tasklets: int):
        # source = Compiler._source_command()
        benchmark_path = os.path.join(PathCollector.benchmark_path_in_local(), benchmark)
        asm_path = os.path.join(PathCollector.asm_path_in_local(), f"{benchmark}.{num_tasklets}")
        
        cd = f"cd {benchmark_path}"
        make_clean = "make clean"
        make = f"make NR_TASKLETS={num_tasklets}"
        mkdir = f"mkdir -p {asm_path}"
        mv = f"mv {benchmark_path}/bin/dpu_code.S {asm_path}/main.S"
        
        commands = f"{cd} && {make_clean} && {make} && {mkdir} && {mv}"

        try:
            subprocess.run(commands, shell=True, check=True, executable="/bin/bash")
            return True
        except subprocess.CalledProcessError:
            return False

    @staticmethod
    def compile_sdk(num_tasklets: int) -> bool:
        for filepath in Compiler._sdk_filepaths_in_local():
            path_parts = filepath.split(os.path.sep)
            library_name = path_parts[-2]
            filename = path_parts[-1]

            common_flags = f"-O3 -S -w -DNR_TASKLETS={num_tasklets}"
            include_flags = f"-I{Compiler._misc_path()} -I{Compiler._stdlib_path()} -I{Compiler._syslib_path()}"
            
            output_dir = os.path.join(PathCollector.asm_path_in_local(), library_name)
            output_flag = f"-o {output_dir}/{filename[:-2]}.S"

            # source = Compiler._source_command()
            mkdir = f"mkdir -p {output_dir}"
            dpu_upmem_dpu_rte_clang = (
                f"{Compiler._dpu_upmem_dpurte_clang()} {common_flags} {include_flags} {output_flag} {filepath}"
            )
            
            commands = f"{mkdir} && {dpu_upmem_dpu_rte_clang}"

            try:
                subprocess.run(commands, shell=True, check=True, executable="/bin/bash")
            except subprocess.CalledProcessError:
                return False
        return True

    @staticmethod
    def clean() -> bool:
        rm = f"rm -rf {PathCollector.asm_path_in_local()}"
        try:
            subprocess.run(rm, shell=True, check=True, executable="/bin/bash")
            return True
        except subprocess.CalledProcessError:
            return False

    @staticmethod
    def _sdk_filepaths_in_local() -> Set[str]:
        filepaths: Set[str] = set()
        for root_path, _, filenames in os.walk(PathCollector.sdk_path_in_local()):
            for filename in filenames:
                if filename.split(".")[-1] == "c":
                    filepaths.add(os.path.join(root_path, filename))
        return filepaths

    @staticmethod
    def _source_command() -> str:
        return f"source {PathCollector.upmem_sdk_path_in_local()}/upmem_env.sh"

    @staticmethod
    def _upmem_include_path() -> str:
        return f"{PathCollector.upmem_sdk_path_in_local()}/include"

    @staticmethod
    def _misc_path() -> str:
        return f"{PathCollector.sdk_path_in_local()}/misc"

    @staticmethod
    def _stdlib_path() -> str:
        return f"{PathCollector.sdk_path_in_local()}/stdlib"

    @staticmethod
    def _syslib_path() -> str:
        return f"{PathCollector.sdk_path_in_local()}/syslib"

    @staticmethod
    def _dpu_upmem_dpurte_clang() -> str:
        return "/home/zhaoyuhang/work_space/uPIMulator/python_cpp/upmem-2024.2.0-Linux-x86_64/bin/dpu-upmem-dpurte-clang"
