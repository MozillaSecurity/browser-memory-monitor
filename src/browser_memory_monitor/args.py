"""browser-memory-monitor argument parser"""
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import annotations

from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Sequence

from .core import __version__


class BrowserMemoryMonitorArgs:
    """Class for parsing and recording arguments"""

    DEFAULT_TARGETS = ["firefox"]

    def __init__(self) -> None:
        """Instantiate a new instance"""
        super().__init__()  # call super for multiple-inheritance support
        if not hasattr(self, "parser"):
            self.parser = ArgumentParser(
                conflict_handler="resolve",
                prog="bmm",
                description="Memory profiler/limiter for browsers",
            )

        self.parser.add_argument(
            "--force",
            "-f",
            action="store_true",
            help="Overwrite existing data output file.",
        )
        self.parser.add_argument(
            "--format",
            "-F",
            choices=["mprof", "csv"],
            default="mprof",
            help="Output format (choices: %(choices)s, default: %(default)s)",
        )
        self.parser.add_argument(
            "--interval",
            "-T",
            type=float,
            default=0.1,
            help="Memory profiling interval (default: %(default)s)",
        )
        self.parser.add_argument(
            "--limit",
            "-m",
            type=int,
            default=12288,
            help="Memory limit in MiB (0 for no limit, default: %(default)s)",
        )
        self.parser.add_argument(
            "--pre-interval",
            "-P",
            type=float,
            default=0.01,
            help="Process start interval (default: %(default)s)",
        )
        self.parser.add_argument(
            "--time-limit",
            "-t",
            type=int,
            default=0,
            help="Maximum time to run (in seconds, 0 for no limit, "
            "default: %(default)s)",
        )
        self.parser.add_argument(
            "--verbose",
            "-v",
            action="store_true",
            help="Enable verbose logging",
        )
        self.parser.add_argument(
            "--version",
            "-V",
            action="version",
            version=f"%(prog)s {__version__}",
            help="Show version number",
        )
        self.parser.add_argument(
            "browser", help="Browser process name to monitor (eg. 'firefox')"
        )
        self.parser.add_argument(
            "data",
            type=Path,
            help="Profiling data output filename",
        )
        self.parser.add_argument(
            "command [...]", help="Command (and args) to execute as a subprocess"
        )

    def sanity_check(self, args: Namespace) -> None:
        """Perform parser checks

        Arguments:
            args: Parsed arguments
            cmdline: remaining arguments
        """
        # multiple-inheritance support
        if hasattr(super(), "sanity_check"):
            # pylint: disable=no-member
            super().sanity_check(args)  # type: ignore # pragma: no cover

        if args.interval <= 0.0:
            self.parser.error("--interval must be positive")
        if args.pre_interval <= 0.0:
            self.parser.error("--pre-interval must be positive")
        if not args.browser:
            self.parser.error("browser must be given")
        if args.limit < 0:
            self.parser.error("--limit must be positive")
        if args.time_limit < 0:
            self.parser.error("--time-limit must be positive")
        if args.data.exists() and not args.force:
            self.parser.error(
                f"Data output file '{args.data}' exists. Use --force to overwrite."
            )

    def parse_args(self, argv: Sequence[str] | None = None) -> Namespace:
        """Parse and validate args

        Arguments:
            argv: a list of arguments

        Returns:
            options - parsed arguments
        """
        args, command = self.parser.parse_known_args(argv)
        args.command = [getattr(args, "command [...]")] + command
        self.sanity_check(args)
        return args
