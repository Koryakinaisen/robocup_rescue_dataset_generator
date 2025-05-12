# data_pipeline/log_filter.py
import re
from config import get_files_path


def filter_kernel_log(logs_dir):
    kernel_log = get_files_path(logs_dir).get('kernel_log', None)
    pattern = re.compile(
        r'^DEBUG kernel :\s+(Ambulance team|Police force|Fire brigade)\s+\((\d+)\)\s+can\s+see\s+\[(.*)\]',
        re.IGNORECASE
    )
    timestep_pattern = re.compile(r"INFO kernel : Timestep (\d+)\s*$")

    filtered_lines = []

    with open(kernel_log, 'r', encoding='utf-8') as inp:
        for line in inp:
            if timestep_pattern.match(line) or pattern.match(line):
                filtered_lines.append(line)

    return filtered_lines