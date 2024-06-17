"""
#!/usr/bin/python3.9
# -*- coding: utf-8 -*-
@Project :pythonCodeSnippet
@File    :gpuTools.py
@IDE     :PyCharm
@Author  :chenxw
@Date    :2023/9/25 10:14
@Descr:
"""
import torch


class GPUHelper:
    def __int__(self):
        pass
    @staticmethod
    def get_gpu_utilization() -> None:
        """
        获取GPU利用率

        :return:
        """
        device_count = torch.cuda.device_count()
        gpu_utilizations = []
        for i in range(device_count):
            device = torch.device(f"cuda:{i}")
            # 一执行就奔溃
            gpu_utilization = torch.cuda.max_memory_allocated(device) / torch.cuda.max_memory_reserved(device) * 100
            gpu_utilizations.append(gpu_utilization)
        return gpu_utilizations

    @staticmethod
    def get_least_utilized_gpu() -> None:
        """
        得到最小利用率的GPU
        :return:
        """
        gpu_utilizations = GPUHelper.get_gpu_utilization()
        least_utilized_gpu = min(range(len(gpu_utilizations)), key=gpu_utilizations.__getitem__)
        return least_utilized_gpu
