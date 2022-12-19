# -*- coding: utf-8 -*-
"""Provides System Information about devices, OS etc."""

import datetime
import decimal
import os
import re
import socket
import uuid
from subprocess import getoutput
from typing import Dict, List, Tuple

import GPUtil
import psutil
from msaBase.errorhandling import getMSABaseExceptionHandler
from msaBase.models.sysinfo import (
    MSACPUFrequency,
    MSACPUStats,
    MSACPUTimes,
    MSADiskIO,
    MSAGPUInfo,
    MSAMemoryUsage,
    MSANetworkAdapter,
    MSANetworkAdapters,
    MSANetworkConnection,
    MSANetworkIO,
    MSANetworkStat,
    MSANetworkStats,
    MSASwap,
    MSASystemGPUInfo,
    MSASystemInfo,
    MSATemperature,
    MSATemperatures,
)


def get_hostname() -> str:
    """
    Get current host name.

    Returns:
        hostname string
    """
    hostname: str = socket.gethostname()
    return hostname


def get_list_partitions() -> List:
    """
    Get mounted partitions as a list.

    Returns:
        List of mounted partitions.
    """
    partitions_list = []
    partitions = psutil.disk_partitions()
    partitions_list = [partition[1] for partition in partitions]

    return partitions_list


def get_gpus() -> List[MSAGPUInfo]:
    """
    Get GPU information.

    Returns:
        List of GPUs
    """
    gpus = GPUtil.getGPUs()
    list_gpus: List[MSAGPUInfo] = []
    for gpu in gpus:
        ng: MSAGPUInfo = MSAGPUInfo()
        # get the GPU id
        ng.id = gpu.id
        # name of GPU
        ng.name = gpu.name
        # get % percentage of GPU usage of that GPU
        ng.load = f"{gpu.load * 100}%"
        # get free memory in MB format
        ng.free_memory = f"{gpu.memoryFree}MB"
        # get used memory
        ng.used_memory = f"{gpu.memoryUsed}MB"
        # get total memory
        ng.total_memory = f"{gpu.memoryTotal}MB"
        # get GPU temperature in Celsius
        ng.temperature = f"{gpu.temperature} °C"
        ng.uuid = gpu.uuid
        list_gpus.append(ng)
    return list_gpus


def get_partition_usage(partitions) -> Dict:
    """
    Get disc usage statistics for given partitions.

    Returns:
        Dictionary containing partition usage statistics info
    """
    lstotal = []
    lsused = []
    lsfree = []
    lspercent = []
    lspartition: List = [partition for partition in partitions]

    for partition in partitions:
        usage = psutil.disk_usage(partition)
        total, used, free, percent = usage

        lstotal.append(total // (2**30))
        lsused.append(used // (2**30))
        lsfree.append(free // (2**30))
        lspercent.append(percent)

    ret: Dict = {
        "partition": lspartition,
        "total": lstotal,
        "used": lsused,
        "free": lsfree,
        "percent": lspercent,
    }
    return ret


def get_map_disk_usage() -> Dict:
    """
    Get reformatted disk usage info

    Returns:
        Dictionary containing reformatted disk usage statistics info
    """
    MapUsage: Dict = get_partition_usage(get_list_partitions())
    disk = MapUsage["partition"]
    total = MapUsage["total"]
    used = MapUsage["used"]
    free = MapUsage["free"]
    percent = MapUsage["percent"]
    rdict = dict(zip(disk, zip(total, used, free, percent)))
    return rdict


def get_memory_usage() -> MSAMemoryUsage:
    """
    Get virtual memory usage

    Returns:
        Pydantic model containing memory usage information
    """
    mu: MSAMemoryUsage = MSAMemoryUsage()
    memory = psutil.virtual_memory()

    mu.total = memory.total / 1024 / 1024
    mu.available = memory.available / 1024 / 1024
    mu.used = memory.used / 1024 / 1024
    mu.free = memory.free / 1024 / 1024
    mu.percent = memory.percent
    mu.buffers = memory.buffers / 1024 / 1024
    mu.cached = memory.cached / 1024 / 1024
    mu.active = memory.active / 1024 / 1024
    mu.inactive = memory.inactive / 1024 / 1024
    return mu


def get_cpu_freq() -> MSACPUFrequency:
    """
    Get CPU frequency information

    Returns:
        Pydantic model containing CPU frequency information
    """
    cpf: MSACPUFrequency = MSACPUFrequency()
    cpf.current, cpf.min, cpf.max = psutil.cpu_freq()
    return cpf


def get_cpu_times() -> MSACPUTimes:
    """
    Get CPU timings information

    Returns:
        Pydantic model containing CPU timings information
    """
    cti: MSACPUTimes = MSACPUTimes()
    (
        cti.user,
        cti.nice,
        cti.system,
        cti.idle,
        cti.iowait,
        cti.irq,
        cti.softirq,
        cti.steal,
        cti.guest,
        cti.guest_nice,
    ) = psutil.cpu_times()
    return cti


def get_cpu_stats() -> MSACPUStats:
    """
    Get CPU statistics

    Returns:
        Pydantic model containing CPU statistics
    """
    cst: MSACPUStats = MSACPUStats()
    (
        cst.ctx_switches,
        cst.interrupts,
        cst.soft_interrupts,
        cst.syscalls,
    ) = psutil.cpu_stats()
    return cst


def get_disk_io() -> MSADiskIO:
    """
    Get disk input/output information.

    Returns:
        Pydantic model containing disk input/output information
    """
    dio: MSADiskIO = MSADiskIO()
    (
        dio.read_count,
        dio.write_count,
        dio.read_bytes,
        dio.write_bytes,
        dio.read_time,
        dio.write_time,
        dio.read_merged_count,
        dio.write_merged_count,
        dio.busy_time,
    ) = psutil.disk_io_counters()
    return dio


def get_network_io() -> MSANetworkIO:
    """
    Get network input/output information.

    Returns:
        Pydantic model containing network input/output information
    """
    nio: MSANetworkIO = MSANetworkIO()
    (
        nio.bytes_sent,
        nio.bytes_recv,
        nio.packets_sent,
        nio.packets_recv,
        nio.errin,
        nio.errout,
        nio.dropin,
        nio.dropout,
    ) = psutil.net_io_counters()
    return nio


def get_network_adapters() -> List[MSANetworkAdapters]:
    """
    Get the addresses associated to each NIC (network interface card)

    Returns:
        List of Network Adapters List models
    """
    ret: List[MSANetworkAdapters] = []
    la: Dict = psutil.net_if_addrs()

    for key, val in la.items():
        na: MSANetworkAdapters = MSANetworkAdapters()
        na.name = key
        for entry in val:
            la_entry: MSANetworkAdapter = MSANetworkAdapter()
            la_entry.family = entry[0]
            la_entry.address = entry[1]
            la_entry.netmask = entry[2]
            la_entry.broadcast = entry[3]
            la_entry.ptp = entry[4]
            na.adapters.append(la_entry)
        ret.append(na)
    return ret


def get_temperatures() -> List[MSATemperatures]:
    """
    Get hardware temperatures.

    Returns:
        List of models containing temperature information.
    """
    ret: List[MSATemperatures] = []
    ta: Dict = psutil.sensors_temperatures()
    for key, val in ta.items():
        tp: MSATemperatures = MSATemperatures()
        tp.device = key
        for entry in val:
            tp_entry: MSATemperature = MSATemperature()
            tp_entry.label = entry[0]
            tp_entry.current = entry[1]
            tp_entry.high = entry[2]
            tp_entry.critical = entry[3]
            tp.temps.append(tp_entry)
        ret.append(tp)
    return ret


def get_network_stats() -> List[MSANetworkStats]:
    """
    Get information about each NIC (network interface card)

    Returns:
        List of models containing network statistics information.
    """
    ret: List[MSANetworkStats] = []
    net_stats: Dict = psutil.net_if_stats()
    for key, entry in net_stats.items():
        ns: MSANetworkStats = MSANetworkStats()
        ns.name = key
        ns_entry: MSANetworkStat = MSANetworkStat()
        ns_entry.isup = entry[0]
        ns_entry.duplex = entry[1]
        ns_entry.speed = entry[2]
        ns_entry.mtu = entry[3]
        ns.adapters.append(ns_entry)
        ret.append(ns)
    return ret


def get_network_connections() -> List[MSANetworkConnection]:
    """
    Get system-wide socket connections as a list

    Returns:
        List of models containing network connections information.
    """
    rlist: List[MSANetworkConnection] = []
    inlist = psutil.net_connections()
    for xi, entry in enumerate(inlist):
        nc: MSANetworkConnection = MSANetworkConnection()
        nc.index = xi
        nc.file_descriptor = entry[0]
        nc.family = entry[1]
        nc.type = entry[2]

        nc.local_addr = str(entry[3])
        nc.remote_addr = str(entry[4])

        nc.status = entry[5]
        nc.pid = entry[6]
        rlist.append(nc)
    return rlist


def get_swap() -> MSASwap:
    """
    Get system swap memory statistics.

    Returns:
        Pydantic model containing system swap memory information
    """
    swap = psutil.swap_memory()
    sw: MSASwap = MSASwap()
    sw.total = swap.total / 1024 / 1024
    sw.used = swap.used / 1024 / 1024
    sw.free = swap.free / 1024 / 1024
    sw.percent = swap.percent
    return sw


def get_load_average() -> List[float]:
    """
    Returns the CPU load average in tuple[1min, 5min, 15min].

    Returns:
        1min: total usage
        5min: largest process usage
        15min: name of the largest process

    """
    return [x / psutil.cpu_count() * 100 for x in psutil.getloadavg()]


def get_cpu_usage(user: str = None, ignore_self: bool = False) -> Tuple[int, int, str]:
    """
    Returns the total CPU usage for all available cores.

    Parameters:
        user: If given, returns only the total CPU usage of all processes for the given user.
        ignore_self: If ``True`` the process that runs this script will be ignored.

    Returns:
        total: total usage
        largest_process: largest process usage
        largest_process_name: name of the largest process
    """
    pid = os.getpid()
    cmd = "ps aux"
    output = getoutput(cmd)
    total: int = 0
    largest_process = 0
    largest_process_name = None
    for row in output.split("\n")[1:]:
        erow: List = row.split()
        if erow[1] == str(pid) and ignore_self:
            continue
        if user is None or user == erow[0]:
            cpu = decimal.Decimal(erow[2])
            if cpu > total:
                largest_process = cpu
                largest_process_name = " ".join(erow[10 : len(erow)])
            total += decimal.Decimal(erow[2])
    return total, largest_process, largest_process_name


def get_sysinfo() -> MSASystemInfo:
    """
    Get system information.

    Returns:
        Pydantic System Info Model.
    """
    system_info: MSASystemInfo = MSASystemInfo()
    try:
        system_info.OS_Name = os.uname().sysname
        system_info.Node_Name = os.uname().nodename
        system_info.Host_Name = get_hostname()
        system_info.OS_Release = os.uname().release
        system_info.OS_Version = os.uname().version
        system_info.HW_Identifier = os.uname().machine
        system_info.CPU_Physical = psutil.cpu_count(logical=False)
        system_info.CPU_Logical = os.cpu_count()
        system_info.Memory_Physical = str(round(psutil.virtual_memory().total / 1024000000.0, 2)) + " GB"
        system_info.Memory_Available = str(round(psutil.virtual_memory().available / 1024000000.0, 2)) + " GB"
        system_info.System_Boot = datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
        system_info.Service_Start = datetime.datetime.fromtimestamp(psutil.Process().create_time()).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        system_info.Runtime_Exe = psutil.Process().exe()
        system_info.Runtime_Cmd = psutil.Process().cmdline()
        system_info.PID = psutil.Process().pid
        system_info.CPU_Current = psutil.Process().cpu_num()
        system_info.Disk_IO = get_disk_io()
        system_info.Network_IO = get_network_io()
        system_info.CPU_Times = get_cpu_times()
        system_info.CPU_Stats = get_cpu_stats()
        system_info.CPU_Frequency = get_cpu_freq()
        system_info.CPU_Affinity = len(psutil.Process().cpu_affinity())
        system_info.Memory_Usage = get_memory_usage()
        system_info.CPU_LoadAvg = get_load_average()
        (
            system_info.CPU_Usage_Total,
            system_info.CPU_Usage_Process,
            system_info.CPU_Usage_Name,
        ) = get_cpu_usage()
        system_info.Runtime_Status = psutil.Process().status()
        system_info.Network_Adapters = get_network_adapters()
        system_info.Temperatures = get_temperatures()
        system_info.Network_Connections = get_network_connections()
        system_info.Swap = get_swap()
        system_info.Network_Stats = get_network_stats()
        system_info.IP_Address = socket.gethostbyname(socket.gethostname())
        system_info.MAC_Address = ":".join(re.findall("..", "%012x" % uuid.getnode()))

    except Exception as e:
        getMSABaseExceptionHandler().handle(e, "Error: Get System Information:")

    return system_info


def get_sysgpuinfo() -> MSASystemGPUInfo:
    """
    Get GPU information

    Returns:
        Pydantic model containing GPU information
    """
    system_gpu_info: MSASystemGPUInfo = MSASystemGPUInfo()
    try:
        system_gpu_info.OS_Name = os.uname().sysname
        system_gpu_info.Node_Name = os.uname().nodename
        system_gpu_info.Host_Name = get_hostname()
        system_gpu_info.OS_Release = os.uname().release
        system_gpu_info.OS_Version = os.uname().version
        system_gpu_info.HW_Identifier = os.uname().machine
        system_gpu_info.CPU_Physical = psutil.cpu_count(logical=False)
        system_gpu_info.CPU_Logical = os.cpu_count()
        system_gpu_info.Memory_Physical = str(round(psutil.virtual_memory().total / 1024000000.0, 2)) + " GB"
        system_gpu_info.Memory_Available = str(round(psutil.virtual_memory().available / 1024000000.0, 2)) + " GB"
        system_gpu_info.System_Boot = datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
        system_gpu_info.Service_Start = datetime.datetime.fromtimestamp(psutil.Process().create_time()).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        system_gpu_info.Runtime_Exe = psutil.Process().exe()
        system_gpu_info.Runtime_Cmd = psutil.Process().cmdline()
        system_gpu_info.Runtime_Status = psutil.Process().status()
        system_gpu_info.PID = psutil.Process().pid
        system_gpu_info.GPUs = get_gpus()
        system_gpu_info.IP_Address = socket.gethostbyname(socket.gethostname())
        system_gpu_info.MAC_Address = ":".join(re.findall("..", "%012x" % uuid.getnode()))

    except Exception as e:
        getMSABaseExceptionHandler().handle(e, "Error: Get System GPU Information:")

    return system_gpu_info
