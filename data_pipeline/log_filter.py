# data_pipeline/log_filter.py
import re
from config import get_files_path, FILTERED_KERNEL_LOG


def filter_kernel_log(logs_dir):
    kernel_log = get_files_path(logs_dir).get('kernel_log', None)
    pattern = re.compile(
        r'^DEBUG kernel :\s+(Ambulance team|Police force|Fire brigade)\s+\((\d+)\)\s+can\s+see\s+\[(.*)\]',
        re.IGNORECASE
    )
    timestep_pattern = re.compile(r"INFO kernel : Timestep (\d+)\s*$")
    """Удаляем шумные строки из kernel.log &rarr; filtered_kernel.log"""
    with open(kernel_log, 'r', encoding='utf-8') as inp, \
            open(FILTERED_KERNEL_LOG, 'w', encoding='utf-8') as out:
        for line in inp:
            # if ("Adding message 4876" in line or
            #         "Output noise result: 4876" in line):
            #     continue
            if timestep_pattern.match(line) or pattern.match(line):
                out.write(line)
    print(f"[log_filter] {FILTERED_KERNEL_LOG} готов.")
