from typing import List, Optional

from pydantic import BaseModel


class MSAGPUInfo(BaseModel):
    """Pydantic GPU Info Model."""

    id: Optional[int]
    name: Optional[str]
    load: Optional[str]
    free_memory: Optional[str]
    used_memory: Optional[str]
    total_memory: Optional[str]
    temperature: Optional[str]
    uuid: Optional[str]


class MSADiskIO(BaseModel):
    """Pydantic Disk IO Info Model.

    Attributes:
        read_count: number of reads
        write_count: number of writes
        read_bytes: number of bytes read
        write_bytes: number of bytes written
        read_time: (all except NetBSD and OpenBSD) time spent reading from disk (in milliseconds)
        write_time: (all except NetBSD and OpenBSD) time spent writing to disk (in milliseconds)
        busy_time: (Linux, FreeBSD) time spent doing actual I/Os (in milliseconds)
        read_merged_count (Linux): number of merged reads (see iostats doc)
        write_merged_count (Linux): number of merged writes (see iostats doc)

    """

    read_count: Optional[int]
    write_count: Optional[int]
    read_bytes: Optional[int]
    write_bytes: Optional[int]
    read_time: Optional[int]
    write_time: Optional[int]
    read_merged_count: Optional[int]
    write_merged_count: Optional[int]
    busy_time: Optional[int]


class MSANetworkIO(BaseModel):
    """Pydantic Network IO Info Model.

    Attributes:
        bytes_sent: number of bytes sent
        bytes_recv: number of bytes received
        packets_sent: number of packets sent
        packets_recv: number of packets received
        errin: total number of errors while receiving
        errout: total number of errors while sending
        dropin: total number of incoming packets which were dropped
        dropout: total number of outgoing packets which were dropped (always 0 on macOS and BSD)
    """

    bytes_sent: Optional[int]
    bytes_recv: Optional[int]
    packets_sent: Optional[int]
    packets_recv: Optional[int]
    errin: Optional[int]
    errout: Optional[int]
    dropin: Optional[int]
    dropout: Optional[int]


class MSANetworkConnection(BaseModel):
    """Pydantic Network Connection Info Model."""

    index: Optional[int]
    file_descriptor: Optional[int]
    """the socket file descriptor. If the connection refers to the current process this may be passed to socket.fromfd to obtain a usable socket object. On Windows and SunOS this is always set to -1."""
    family: Optional[int]
    """the address family, either AF_INET, AF_INET6 or AF_UNIX."""
    type: Optional[int]
    """the address type, either ``SOCK_STREAM``, ``SOCK_DGRAM`` or ``SOCK_SEQPACKET``."""
    local_addr: Optional[str]
    """the local address as a ``(ip, port)`` named tuple or a ``path`` in case of AF_UNIX sockets. For UNIX sockets see notes below."""
    remote_addr: Optional[str]
    """the remote address as a ``(ip, port)`` named tuple or an absolute ``path`` in case of UNIX sockets. When the remote endpoint is not connected you’ll get an empty tuple (AF_INET*) or ``""`` (AF_UNIX). For UNIX sockets see notes below."""
    status: str = ""
    """represents the status of a TCP connection. The return value is one of the ``psutil.CONN_*`` constants (a string). For UDP and UNIX sockets this is always going to be psutil.CONN_NONE."""
    pid: Optional[int]
    """the PID of the process which opened the socket, if retrievable, else ``None``. On some platforms (e.g. Linux) the availability of this field changes depending on process privileges (root is needed)."""


class MSANetworkAdapter(BaseModel):
    """Pydantic Network Adapter Info Model."""

    family: Optional[int]
    """the address family, either AF_INET or AF_INET6 or psutil.AF_LINK, which refers to a MAC address."""
    address: Optional[str]
    """the primary NIC address (always set)."""
    netmask: Optional[str]
    """the netmask address (may be None)."""
    broadcast: Optional[str]
    """the broadcast address (may be None)."""
    ptp: Optional[int]
    """stands for “point to point”; it’s the destination address on a point to point interface (typically a VPN). broadcast and ptp are mutually exclusive. May be None."""


class MSANetworkAdapters(BaseModel):
    """Pydantic Network Adapters List Model."""

    name: str = ""
    adapters: List[MSANetworkAdapter] = []


class MSANetworkStat(BaseModel):
    """Pydantic Network Stats Info Model."""

    isup: Optional[bool]
    """a bool indicating whether the NIC is up and running (meaning ethernet cable or Wi-Fi is connected)."""
    duplex: Optional[int]
    """the duplex communication type; it can be either NIC_DUPLEX_FULL, NIC_DUPLEX_HALF or NIC_DUPLEX_UNKNOWN."""
    speed: Optional[int]
    """the NIC speed expressed in mega bits (MB), if it can’t be determined (e.g. ‘localhost’) it will be set to 0."""
    mtu: Optional[int]
    """NIC’s maximum transmission unit expressed in bytes."""


class MSANetworkStats(BaseModel):
    """Pydantic Network Stats List Info Model."""

    name: str = ""
    adapters: List[MSANetworkStat] = []


class MSATemperature(BaseModel):
    """Pydantic Temperature Info Model."""

    label: Optional[str]
    current: Optional[float]
    high: Optional[float]
    critical: Optional[float]


class MSATemperatures(BaseModel):
    """Pydantic Temperatures List Model."""

    device: str = ""
    temps: List[MSATemperature] = []


class MSACPUFrequency(BaseModel):
    """Pydantic CPU Frequency Info Model."""

    current: Optional[float]
    min: Optional[int]
    max: Optional[int]


class MSACPUTimes(BaseModel):
    """Pydantic CPU Timings Info Model."""

    user: Optional[float]
    """time spent by normal processes executing in user mode; on Linux this also includes guest time"""
    nice: Optional[int]
    """(UNIX): time spent by niced (prioritized) processes executing in user mode; on Linux this also includes guest_nice time"""
    system: Optional[float]
    """time spent by processes executing in kernel mode"""
    idle: Optional[float]
    """time spent doing nothing"""
    iowait: Optional[float]
    """(Linux): time spent waiting for I/O to complete. This is not accounted in idle time counter."""
    irq: Optional[int]
    """(Linux, BSD): time spent for servicing hardware interrupts"""
    softirq: Optional[float]
    """(Linux): time spent for servicing software interrupts"""
    steal: Optional[int]
    """(Linux 2.6.11+): time spent by other operating systems running in a virtualized environment"""
    guest: Optional[float]
    """(Linux 2.6.24+): time spent running a virtual CPU for guest operating systems under the control of the Linux kernel"""
    guest_nice: Optional[int]
    """(Linux 3.2.0+): time spent running a niced guest (virtual CPU for guest operating systems under the control of the Linux kernel)"""


class MSACPUStats(BaseModel):
    """Pydantic CPU Stats Info Model."""

    ctx_switches: Optional[int]
    """number of context switches (voluntary + involuntary) since boot."""
    interrupts: Optional[int]
    """number of interrupts since boot."""
    soft_interrupts: Optional[int]
    """number of software interrupts since boot. Always set to 0 on Windows and SunOS."""
    syscalls: Optional[int]
    """number of system calls since boot. Always set to 0 on Linux."""


class MSAMemoryUsage(BaseModel):
    """Pydantic Memory Usage Info Model."""

    total: Optional[float]
    """total physical memory (exclusive swap)."""
    available: Optional[float]
    """the memory that can be given instantly to processes without the system going into swap. This is calculated by summing different memory values depending on the platform and it is supposed to be used to monitor actual memory usage in a cross platform fashion."""
    used: Optional[float]
    """memory used, calculated differently depending on the platform and designed for informational purposes only. total - free does not necessarily match used."""
    free: Optional[float]
    """memory not being used at all (zeroed) that is readily available; note that this doesn’t reflect the actual memory available (use available instead). total - used does not necessarily match free."""
    percent: Optional[float]
    """the percentage usage calculated as (total - available) / total * 100"""
    buffers: Optional[float]
    """(Linux, BSD): cache for things like file system metadata."""
    cached: Optional[float]
    """(Linux, BSD): cache for various things."""
    active: Optional[float]
    """(UNIX): memory currently in use or very recently used, and so it is in RAM."""
    inactive: Optional[float]
    """(UNIX): memory that is marked as not used."""


class MSASwap(BaseModel):
    """Pydantic Swapfile Info Model."""

    total: Optional[float]
    used: Optional[float]
    free: Optional[float]
    percent: Optional[float]
    """the percentage usage calculated as (total - available) / total * 100"""


class MSASystemInfo(BaseModel):
    """Pydantic System Info Model."""

    OS_Name: str = ""
    Node_Name: str = ""
    Host_Name: str = ""
    OS_Release: str = ""
    OS_Version: str = ""
    HW_Identifier: str = ""
    IP_Address: str = ""
    MAC_Address: str = ""
    CPU_Physical: Optional[int]
    """Amount of physical CPU's"""
    CPU_Logical: Optional[int]
    """Amount of logical (each physical core doing 2 or more threads, hyperthreading) CPU's"""
    Memory_Physical: str = ""
    Memory_Available: str = ""
    System_Boot: str = ""
    Service_Start: str = ""
    Runtime_Exe: str = ""
    Runtime_Cmd: List[str] = []
    Disk_IO: Optional[MSADiskIO]
    Network_IO: Optional[MSANetworkIO]
    Network_Connections: Optional[List[MSANetworkConnection]]
    Network_Adapters: Optional[List[MSANetworkAdapters]]
    Network_Stats: Optional[List[MSANetworkStats]]
    Temperatures: Optional[List[MSATemperatures]]
    CPU_Affinity: Optional[int]
    CPU_Frequency: Optional[MSACPUFrequency]
    CPU_Times: Optional[MSACPUTimes]
    CPU_Stats: Optional[MSACPUStats]
    PID: Optional[int]
    CPU_Current: Optional[int]
    CPU_Usage_Total: Optional[float]
    CPU_Usage_Process: Optional[float]
    CPU_Usage_Name: str = ""
    CPU_LoadAvg: Optional[List[float]]
    Memory_Usage: Optional[MSAMemoryUsage]
    Swap: Optional[MSASwap]
    Runtime_Status: str = ""
    """Service Status, running or stopped"""


class MSASystemGPUInfo(BaseModel):
    """Pydantic System GPU Info Model."""

    OS_Name: str = ""
    Node_Name: str = ""
    Host_Name: str = ""
    OS_Release: str = ""
    OS_Version: str = ""
    HW_Identifier: str = ""
    IP_Address: str = ""
    MAC_Address: str = ""
    CPU_Physical: Optional[int]
    CPU_Logical: Optional[int]
    Memory_Physical: str = ""
    Memory_Available: str = ""
    System_Boot: str = ""
    Service_Start: str = ""
    Runtime_Exe: str = ""
    Runtime_Cmd: List[str] = []
    PID: Optional[int]
    GPUs: Optional[List[MSAGPUInfo]]
    Runtime_Status: str = ""
