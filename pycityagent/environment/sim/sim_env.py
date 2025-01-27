import atexit
import logging
import os
import time
import warnings
from subprocess import Popen
from typing import Optional

from pycitydata.map import Map

from ..utils import encode_to_base64, find_free_port

__all__ = ["ControlSimEnv"]


def _generate_yaml_config(
    map_file: str, max_day: int, start_step: int, total_step: int
) -> str:
    map_file = os.path.abspath(map_file)
    return f"""
input:
  # 地图
  map:
    file: "{map_file}"

control:
  day: {max_day}
  step:
    start: {start_step}
    total: {total_step}
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
        max_day: int,
        start_step: int,
        total_step: int,
        log_dir: str,
        primary_node_ip: str,
        min_step_time: int = 1000,
        timeout: int = 5,
        max_process: int = 32,
        sim_addr: Optional[str] = None,
    ):
        """
        A control environment for managing a pycityagent-sim process.

        - **Description**:
            - This class sets up and manages a simulation environment using the specified parameters.
            - It can start a new simulation process or connect to an existing one.
        """
        self._task_name = task_name
        self._map_file = map_file
        self._max_day = max_day
        self._start_step = start_step
        self._total_step = total_step
        self._log_dir = log_dir
        self._min_step_time = min_step_time
        self._timeout = timeout
        self._primary_node_ip = primary_node_ip
        self._max_procs = max_process

        self._sim_config = _generate_yaml_config(
            map_file, max_day, start_step, total_step
        )
        # sim
        self.sim_port = None
        self._sim_proc = None
        os.makedirs(log_dir, exist_ok=True)

        self.sim_addr = self.reset(sim_addr)

    def reset(
        self,
        sim_addr: Optional[str] = None,
    ):
        """
        Reset the simulation environment by either starting a new simulation process or connecting to an existing one.

        - **Args**:
            - `sim_addr` (`Optional[str]`): Address of an existing simulation to connect to. If `None`, a new simulation is started.

        - **Returns**:
            - `str`: The address of the simulation server.

        - **Raises**:
            - `AssertionError`: If trying to start a new simulation when one is already running.
        """
        if sim_addr is None:
            # 启动pycityagent-sim
            # pycityagent-sim -config-data configbase64 -job test -listen :51102
            assert self.sim_port is None
            assert self._sim_proc is None
            self.sim_port = find_free_port()
            config_base64 = encode_to_base64(self._sim_config)
            os.environ["GOMAXPROCS"] = str(self._max_procs)
            sim_addr = self._primary_node_ip.rstrip("/") + f":{self.sim_port}"
            self._sim_proc = Popen(
                [
                    "pycityagent-sim",
                    "-config-data",
                    config_base64,
                    "-job",
                    self._task_name,
                    "-listen",
                    sim_addr,
                    "-run.min_step_time",
                    f"{self._min_step_time}",
                    "-run.pause_after_one_day",
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
                f"start pycityagent-sim at {sim_addr}, PID={self._sim_proc.pid}"
            )
            atexit.register(self.close)
            time.sleep(0.3)
        else:
            warnings.warn("单独启动模拟器模拟将被弃用", DeprecationWarning)

        return sim_addr

    def close(self):
        """
        Terminate the simulation process if it's running.
        """
        if self._sim_proc is not None:
            self._sim_proc.terminate()
            sim_code = self._sim_proc.wait()
            logging.info(f"pycityagent-sim exit with code {sim_code}")

        # sim
        self.sim_port = None
        self._sim_proc = None
