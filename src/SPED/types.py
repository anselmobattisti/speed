from typing import TypedDict


class InfrastructureData(TypedDict):
    """
    The data about the nodes in compute zones.
    """
    zone: str
    vnf: str
    gw: str
    delay: int
    node: str
    cost: float
    cpu_available: int
    mem_available: int


class AggregatedData(TypedDict):
    """
    The data aggregated in aggregation zones.
    """
    zone: str
    vnf: str
    gw: str
    delay: int
    cost: float