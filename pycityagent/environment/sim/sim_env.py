import logging
import os
import time
import atexit
from subprocess import DEVNULL, Popen
from typing import Optional

from pycitydata.map import Map

from ..utils import encode_to_base64, find_free_port

__all__ = ["ControlSimEnv"]


def _generate_yaml_config(map_file: str, start_step: int, total_step: int) -> str:
    map_file = os.path.abspath(map_file)
    return f"""
input:
  # 地图
  map:
    file: "{map_file}"

control:
  step:
    # 模拟器起始步
    start: {start_step}
    # 模拟总步数，结束步为起始步+总步数
    total: {total_step}
    # 每步的时间间隔
    interval: 1
  skip_overtime_trip_when_init: true
  enable_platoon: false
  enable_indoor: false
  prefer_fixed_light: true
  enable_collision_avoidance: false # 计算性能下降10倍，需要保证subloop>=5
  enable_go_astray: true # 引入串行的路径规划调用，计算性能下降（幅度不确定）
  lane_change_model: earliest # mobil （主动变道+强制变道，默认值） earliest （总是尽可能早地变道）

output:
"""


class ControlSimEnv:
    def __init__(
        self,
        task_name: str,
        map_file: str,
        # person_file,
        start_step: int,
        total_step: int,
        log_dir: str,
        min_step_time: int = 1000,
        timeout: int = 5,
        simuletgo_addr: Optional[str] = None,
    ):
        self._task_name = task_name
        self._map_file = map_file
        # self._person_file = person_file
        self._start_step = start_step
        self._total_step = total_step
        self._log_dir = log_dir
        self._min_step_time = min_step_time
        self._timeout = timeout
        self.m = Map(pb_path=map_file)
        """
        地图数据
        """

        # 检查二进制文件是否存在
        # simulet-go: ~/.local/bin/simulet-go
        self._simuletgo_path = os.path.expanduser("~/.local/bin/simulet-go")
        if not os.path.exists(os.path.expanduser(self._simuletgo_path)):
            raise FileNotFoundError("simulet-go not found, please install it first")

        self._simuletgo_config = _generate_yaml_config(map_file, start_step, total_step)
        self.simuletgo_port = None
        self._simuletgo_proc = None
        self._traffic_client = None

        os.makedirs(log_dir, exist_ok=True)

        self.simuletgo_addr = self.reset(simuletgo_addr)

    def reset(
        self,
        simuletgo_addr: Optional[str] = None,
    ):
        """
        Args:
        - simuletgo_addr: str, simulet-go的地址。如果为None，则启动一个新的simulet-go
        """

        # 三个地址必须同时为None或者同时不为None
        if simuletgo_addr is None:
            # 1. 启动simulet-go
            # ./simulet-go -config-data configbase64 -job test -syncer http://localhost:53001 -listen :51102
            assert self.simuletgo_port is None
            assert self._simuletgo_proc is None
            self.simuletgo_port = find_free_port()
            config_base64 = encode_to_base64(self._simuletgo_config)
            self._simuletgo_proc = Popen(
                [
                    self._simuletgo_path,
                    "-config-data",
                    config_base64,
                    "-job",
                    self._task_name,
                    "-listen",
                    f":{self.simuletgo_port}",
                    "-run.min_step_time",
                    f"{self._min_step_time}",
                    "-output",
                    self._log_dir,
                    "-cache",
                    "",
                    "-log.level",
                    "error",
                ],
                # 忽略输出
                # stdout=DEVNULL,
            )
            logging.info(
                f"start simulet-go at localhost:{self.simuletgo_port}, PID={self._simuletgo_proc.pid}"
            )
            simuletgo_addr = f"http://localhost:{self.simuletgo_port}"
            atexit.register(self.close)
            time.sleep(1)
        elif simuletgo_addr is not None:
            pass
        else:
            # raise ValueError(
            #     "simuletgo_addr, syncer_addr, routing_addr must be all None or all not None"
            # )
            pass
        return simuletgo_addr

    def close(self):
        if self._simuletgo_proc is not None:
            self._simuletgo_proc.terminate()
            simuletgo_code = self._simuletgo_proc.wait()
            logging.info(f"simulet-go exit with code {simuletgo_code}")

        self.simuletgo_port = None
        self._simuletgo_proc = None
        self._traffic_client = None
