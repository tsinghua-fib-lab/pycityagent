import os
import signal
import subprocess
import sys

_script_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_script_dir)


def wrapper(bin: str):
    binary_path = os.path.join(_parent_dir, bin)
    if not os.path.exists(binary_path):
        print(f"Error: {binary_path} not found")
        sys.exit(1)
    # get command line arguments
    args = sys.argv[1:]
    # run the binary
    p = subprocess.Popen(
        [binary_path] + args,
        env=os.environ,
        stdin=sys.stdin,
        stdout=sys.stdout,
        stderr=sys.stderr,
    )

    # register signal handler
    def signal_handler(sig, frame):
        if p.poll() is None:
            p.send_signal(sig)
        else:
            sys.exit(p.poll())

    signals = [signal.SIGINT, signal.SIGTERM, signal.SIGHUP]
    for sig in signals:
        signal.signal(sig, signal_handler)
    # wait for the child process to exit
    while p.poll() is None:
        pass
    # exit with the same code as the child process
    sys.exit(p.poll())


def agentsociety_sim():
    wrapper("agentsociety-sim")


def agentsociety_ui():
    wrapper("agentsociety-ui")
