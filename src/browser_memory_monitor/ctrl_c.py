"""Send Ctrl+C event to the console of another process."""
# ref: https://stackoverflow.com/a/60795888

import argparse
import ctypes
import os
import signal
import sys
from typing import NoReturn

KERNEL32 = ctypes.windll.kernel32  # type: ignore


def attach_console(pid: int) -> None:
    """Attach the calling process to the console of the specified process."""
    if not KERNEL32.FreeConsole():
        raise ctypes.WinError()  # type: ignore
    if not KERNEL32.AttachConsole(pid):
        raise ctypes.WinError()  # type: ignore


def ignore_ctrl_c() -> None:
    """Calling process and children will ignore Ctrl+C."""
    if not KERNEL32.SetConsoleCtrlHandler(None, 1):
        raise ctypes.WinError()  # type: ignore


def main() -> NoReturn:
    """Send Ctrl+C to another process.

    This must be a separate process and not a function because it clears the global
    Ctrl+C handler.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("pid", type=int)
    args = parser.parse_args()

    # attach to the target console
    attach_console(args.pid)
    # ignore Ctrl+C in this process only, so we can return success
    ignore_ctrl_c()
    # send Ctrl+C to the current console (except self)
    # pylint: disable=no-member
    os.kill(0, signal.CTRL_C_EVENT)  # type: ignore
    sys.exit(0)


if __name__ == "__main__":
    main()
