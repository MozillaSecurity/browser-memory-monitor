"""browser-memory-monitor implementation"""
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import annotations

import os
import signal
import sys
from argparse import Namespace
from logging import getLogger
from platform import system
from subprocess import Popen, check_call
from sys import version_info
from time import time
from typing import NoReturn, Sequence

import psutil

LOG = getLogger("bmm")

if version_info[:2] < (3, 8):
    # pylint: disable=import-error
    from importlib_metadata import PackageNotFoundError, version  # pragma: no cover
else:
    # pylint: disable=import-error
    from importlib.metadata import PackageNotFoundError, version  # pragma: no cover


try:
    __version__ = version("browser-memory-manager")
except PackageNotFoundError:
    # package is not installed
    __version__ = None


def find_process(parent: psutil.Process, name: str) -> psutil.Process | None:
    """Search recursively for a child process of parent, where the
    child process contains the given name.

    Arguments:
        parent: head of process tree to search within (exclusive)
        name: substring of process name to search for

    Returns:
        psutil.Process of most senior process matching,
        or None if no process found
    """
    for child in parent.children(recursive=True):
        if name in child.name():
            LOG.debug("found browser process: %d (%s)", child.pid(), child.name())
            return child
    return None


def memory_usage(process: psutil.Process) -> float:
    """aggregate memory of a process tree

    Arguments:
        process: head of process tree to sum (inclusive)

    Returns:
        rss memory usage of process tree in MiB
    """
    result = int(process.memory_info().rss)
    for child in process.children(recursive=True):
        result += int(child.memory_info().rss)
    return result / (1024 * 1024)


def ctrl_c(pid: int) -> None:
    """send ctrl+c to a given process (cross-platform)

    Arguments:
        pid: process ID to send signal

    Returns:
        None
    """
    if system() == "Windows":
        check_call(
            [
                sys.executable,
                "-m",
                "browser_memory_monitor.ctrl_c",
                str(pid),
            ]
        )
    else:
        os.kill(pid, signal.SIGINT)


def main(options: Namespace, command: Sequence[str]) -> NoReturn:
    """main entrypoint for browser-memory-monitor

    Arguments:
        options: parsed arguments
        command: subcommand to launch with limits
    """

    # launch subprocess
    with Popen(command) as hnd:
        proc = psutil.Process(hnd.pid)

        # poll pre-interval until some child process matches options.process
        while True:
            browser = find_process(hnd.pid, options.process)
            if browser is not None:
                break
            gone, _ = psutil.wait_procs([proc], timeout=options.pre_interval)
            if gone:
                LOG.warning(
                    "process exited before '%s' could be found (returned %d)",
                    options.process,
                    gone[0].returncode,
                )
                sys.exit(gone[0].returncode)

        # poll interval until exits or time-limit or memory-limit
        start = time()
        with options.data.open("w") as data:
            print(f"CMDLINE {browser.cmdline()}", file=data)
            while True:
                if browser.is_running():
                    memory = memory_usage(browser)
                    now = time()
                    print(f"MEM {memory:0.6f} {now:0.4f}", file=data)
                    if memory >= options.limit:
                        LOG.warning(
                            "process memory limit exhausted (%dMB vs %dMB)",
                            memory,
                            options.limit,
                        )
                        break
                    if (now - start) >= options.time_limit:
                        LOG.warning(
                            "process time limit exceeded (%ss vs %ss)",
                            now - start,
                            options.time_limit,
                        )
                        break
                gone, _ = psutil.wait_procs([proc], timeout=options.interval)
                if gone:
                    LOG.warning("process exited (returned %d)", gone[0].returncode)
                    sys.exit(gone[0].returncode)

        # either time-limit or memory-limit occurred
        # send ctrl+c to child
        ctrl_c(hnd.pid)
        sys.exit(hnd.wait())
