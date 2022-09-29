"""browser-memory-monitor console entrypoint"""
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import sys
from logging import DEBUG, INFO, basicConfig
from typing import NoReturn, Sequence

from .args import BrowserMemoryMonitorArgs
from .core import __version__
from .core import main as core_main


def init_logging(level: int = INFO) -> None:
    """Initialize logging

    Arguments:
        level: logging verbosity level

    Returns:
        None
    """
    log_fmt = "[%(asctime)s] %(message)s"
    if level == DEBUG:
        log_fmt = "%(levelname).1s %(name)s [%(asctime)s] %(message)s"
    basicConfig(format=log_fmt, datefmt="%Y-%m-%d %H:%M:%S", level=level)


def main(argv: Sequence[str] | None = None) -> NoReturn:
    """console entrypoint

    Arguments:
        argv: a list of arguments
    """
    opts, cmdline = BrowserMemoryMonitorArgs().parse_args(argv)
    if opts.verbose or bool(os.getenv("DEBUG")):
        init_logging(DEBUG)
    else:
        init_logging()
    if opts.version:
        print(f"bmm version {__version__}", file=sys.stderr)
        sys.exit(0)

    core_main(opts, cmdline)
