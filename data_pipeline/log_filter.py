# data_pipeline/log_filter.py
from config import KERNEL_LOG, FILTERED_KERNEL_LOG


def filter_kernel_log():
    """Удаляем шумные строки из kernel.log &rarr; filtered_kernel.log"""
    with open(KERNEL_LOG, 'r', encoding='utf-8') as inp, \
            open(FILTERED_KERNEL_LOG, 'w', encoding='utf-8') as out:
        for line in inp:
            if ("Adding message 4876" in line or
                    "Output noise result: 4876" in line):
                continue
            out.write(line)
    print(f"[log_filter] {FILTERED_KERNEL_LOG} готов.")
