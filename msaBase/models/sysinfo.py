from typing import List, Optional

from pydantic import BaseModel


class MSAGPUInfo(BaseModel):
    """
    Pydantic GPU Info Model.

    Attributes:
        id: GPU identifier
        name: GPU name
        load: GPU current load
        free_memory: amount of free memory
        used_memory: amount of used memory
        total_memory: amount of total memory
        temperature: current temperature
        uuid: unique GPU identifier
    """

    id: Optional[int]
    name: Optional[str]
    load: Optional[str]
    free_memory: Optional[str]
    used_memory: Optional[str]
    total_memory: Optional[str]
    temperature: Optional[str]
    uuid: Optional[str]


class MSADiskIO(BaseModel):
    """
    Pydantic Disk IO Info Model.

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
    """
    Pydantic Network IO Info Model.

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
    """
    Pydantic Network Connection Info Model.

    Attributes:
        index: network connection index
        file_descriptor: the socket file descriptor. If the connection refers to the current process this may
        be passed to socket. fromfd to obtain a usable socket object. On Windows and SunOS this is always set to -1.
        family: the address family, either AF_INET, AF_INET6 or AF_UNIX.
        type: the address type, either "SOCK_STREAM", "SOCK_DGRAM" or "SOCK_SEQPACKET".
        local_addr: the local address as a "(ip, port)" named tuple or a "path" in case of AF_UNIX sockets.
        For UNIX sockets see notes below.
        remote_addr: the remote address as a "(ip, port)" named tuple or an absolute "path" in case of UNIX sockets.
        When the remote endpoint is not connected you’ll get an empty tuple (AF_INET*) or '""' (AF_UNIX).
        For UNIX sockets see notes below.
        status: represents the status of a TCP connection. The return value is one of the "psutil.CONN_*"
        constants (a string). For UDP and UNIX sockets this is always going to be psutil.CONN_NONE.
        pid: the PID of the process which opened the socket, if retrievable, else "None". On some platforms
        (e.g. Linux) the availability of this field changes depending on process privileges (root is needed).
    """

    index: Optional[int]
    file_descriptor: Optional[int]
    family: Optional[int]
    type: Optional[int]
    local_addr: Optional[str]
    remote_addr: Optional[str]
    status: str = ""
    pid: Optional[int]


class MSANetworkAdapter(BaseModel):
    """
    Pydantic Network Adapter Info Model.

    Attributes:
        family: the address family, either AF_INET or AF_INET6 or psutil.AF_LINK, which refers to a MAC address.
        address: the primary NIC address (always set).
        netmask: the netmask address (may be None).
        broadcast: the broadcast address (may be None).
        ptp: stands for “point to point”; it’s the destination address on a point to point interface
        (typically a VPN). broadcast and ptp are mutually exclusive. May be None.
    """

    family: Optional[int]
    address: Optional[str]
    netmask: Optional[str]
    broadcast: Optional[str]
    ptp: Optional[int]


class MSANetworkAdapters(BaseModel):
    """
    Pydantic Network Adapters List Model.

    Attributes:
        name: adapter list name
        adapters: list of adapters
    """

    name: str = ""
    adapters: List[MSANetworkAdapter] = []


class MSANetworkStat(BaseModel):
    """
    Pydantic Network Stats Info Model.

    Attributes:
        isup: a bool indicating whether the NIC is up and running (meaning ethernet cable or Wi-Fi is connected).
        duplex: the duplex communication type; it can be either NIC_DUPLEX_FULL, NIC_DUPLEX_HALF or NIC_DUPLEX_UNKNOWN.
        speed: the NIC speed expressed in mega bits, if it can’t be determined (e.g. ‘localhost’) it will be set to 0.
        mtu: NIC’s maximum transmission unit expressed in bytes.
    """

    isup: Optional[bool]
    duplex: Optional[int]
    speed: Optional[int]
    mtu: Optional[int]


class MSANetworkStats(BaseModel):
    """
    Pydantic Network Stats List Info Model.

    Attributes:
        name: list name
        adapters: list of network statistics
    """

    name: str = ""
    adapters: List[MSANetworkStat] = []


class MSATemperature(BaseModel):
    """
    Pydantic Temperature Info Model.

    Attributes:
        label: informational label
        current: current temperature
        high: highest temperature
        critical: critical temperature
    """

    label: Optional[str]
    current: Optional[float]
    high: Optional[float]
    critical: Optional[float]


class MSATemperatures(BaseModel):
    """
    Pydantic Temperatures List Model.

    Attributes:
        device: device name
        temps: list of temperatures
    """

    device: str = ""
    temps: List[MSATemperature] = []


class MSACPUFrequency(BaseModel):
    """
    Pydantic CPU Frequency Info Model.

    Attributes:
        current: current frequency
        min: minimal frequency
        max: maximal frequency
    """

    current: Optional[float]
    min: Optional[int]
    max: Optional[int]


class MSACPUTimes(BaseModel):
    """
    Pydantic CPU Timings Info Model.

    Attributes:
        user: time spent by normal processes executing in user mode; on Linux this also includes guest time
        nice: (UNIX): time spent by niced (prioritized) processes executing in user mode;
        on Linux this also includes guest_nice time
        system: time spent by processes executing in kernel mode
        idle: time spent doing nothing
        iowait: (Linux): time spent waiting for I/O to complete. This is not accounted in idle time counter.
        irq: (Linux, BSD): time spent for servicing hardware interrupts
        softirq: (Linux): time spent for servicing software interrupts
        steal: (Linux 2.6.11+): time spent by other operating systems running in a virtualized environment
        guest: (Linux 2.6.24+): time spent running a virtual CPU for guest operating systems
        under the control of the Linux kernel
        guest_nice: (Linux 3.2.0+): time spent running a niced guest (virtual CPU for guest operating
        systems under the control of the Linux kernel)
    """

    user: Optional[float]
    nice: Optional[int]
    system: Optional[float]
    idle: Optional[float]
    iowait: Optional[float]
    irq: Optional[int]
    softirq: Optional[float]
    steal: Optional[int]
    guest: Optional[float]
    guest_nice: Optional[int]


class MSACPUStats(BaseModel):
    """
    Pydantic CPU Stats Info Model.

    Attributes:
        ctx_switches: number of context switches (voluntary + involuntary) since boot.
        interrupts: number of interrupts since boot.
        soft_interrupts: number of software interrupts since boot. Always set to 0 on Windows and SunOS.
        syscalls: number of system calls since boot. Always set to 0 on Linux.
    """

    ctx_switches: Optional[int]
    interrupts: Optional[int]
    soft_interrupts: Optional[int]
    syscalls: Optional[int]
    """"""


class MSAMemoryUsage(BaseModel):
    """
    Pydantic Memory Usage Info Model.

    Attributes:
        total: total physical memory (exclusive swap).
        available: the memory that can be given instantly to processes without the system going into swap.
        This is calculated by summing different memory values depending on the platform and it is supposed to be
        used to monitor actual memory usage in a cross platform fashion.
        used: memory used, calculated differently depending on the platform and designed for informational purposes.
        total - free does not necessarily match used.
        free: memory not being used at all (zeroed) that is readily available; note that this doesn’t
        reflect the actual memory available (use available instead). total - used does not necessarily match free.
        percent: the percentage usage calculated as (total - available) / total * 100
        buffers: (Linux, BSD): cache for things like file system metadata.
        cached: (Linux, BSD): cache for various things.
        active: (UNIX): memory currently in use or very recently used, and so it is in RAM.
        inactive: (UNIX): memory that is marked as not used.
    """

    total: Optional[float]
    available: Optional[float]
    used: Optional[float]
    free: Optional[float]
    percent: Optional[float]
    buffers: Optional[float]
    cached: Optional[float]
    active: Optional[float]
    inactive: Optional[float]
    """"""


class MSASwap(BaseModel):
    """
    Pydantic Swapfile Info Model.

    Attributes:
        total: total swap size
        used: used swap size
        free: free swap size
        percent: the percentage usage calculated as (total - available) / total * 100
    """

    total: Optional[float]
    used: Optional[float]
    free: Optional[float]
    percent: Optional[float]


class MSASystemInfo(BaseModel):
    """
    Pydantic System Info Model.

    Attributes:
        OS_Name: name of the operational system
        Node_Name: name of the node
        Host_Name: name of the host
        OS_Release: release of the operational system
        OS_Version: operational system's version
        HW_Identifier: HW identifier
        IP_Address: IP address
        MAC_Address: MAC address
        CPU_Physical: Amount of physical CPU's
        CPU_Logical: Amount of logical (each physical core doing 2 or more threads, hyperthreading) CPU's
        Memory_Physical:  amount of physical memory
        Memory_Available: amount of available memory
        System_Boot: system boot info
        Service_Start: service start info
        Runtime_Exe: runtime info
        Runtime_Cmd: runtime cmd info
        Disk_IO: disk usage info (input/output)
        Network_IO: network usage info (input/output)
        Network_Connections: list of network connections
        Network_Adapters: list of network adapters
        Network_Stats: list of network stats
        Temperatures: list of temperatures
        CPU_Affinity: CPU affinity value
        CPU_Frequency: CPU frequency info
        CPU_Times: CPU timings
        CPU_Stats: CPU stats
        PID: process identifier
        CPU_Current: current CPU usage
        CPU_Usage_Total: total CPU usage
        CPU_Usage_Process: CPU usage process
        CPU_Usage_Name: CPU usage name
        CPU_LoadAvg: CPU average load
        Memory_Usage: memory usage info
        Swap: swap info
        Runtime_Status: Service Status, running or stopped
    """

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


class MSASystemGPUInfo(BaseModel):
    """
    Pydantic System GPU Info Model.

    Attributes:
        OS_Name: name of the operational system
        Node_Name: name of the current node
        Host_Name: name of the host
        OS_Release: operational system release info
        OS_Version: operational system version info
        HW_Identifier:
         HW_Identifier: HW identifier
        IP_Address: IP address
        MAC_Address: MAC address
        CPU_Physical: Amount of physical CPU's
        CPU_Logical: Amount of logical (each physical core doing 2 or more threads, hyperthreading) CPU's
        Memory_Physical:  amount of physical memory
        Memory_Available: amount of available memory
        System_Boot: system boot info
        Service_Start: service start info
        Runtime_Exe: runtime info
        Runtime_Cmd: runtime cmd info
        PID: process identifier
        GPUs: list of GPUs
        Runtime_Status: Service Status, running or stopped
    """

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
