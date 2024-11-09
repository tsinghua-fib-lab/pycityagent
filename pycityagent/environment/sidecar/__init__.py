"""
用于接入模拟器同步框架的Sidecar框架服务（仅客户端）
Sidecar framework service for accessing the simulator synchronization framework (client only)
"""

from .sidecarv2 import *

__all__ = ["OnlyClientSidecar"]
