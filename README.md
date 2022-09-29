[![Task Status](https://community-tc.services.mozilla.com/api/github/v1/repository/MozillaSecurity/browser-memory-monitor/main/badge.svg)](https://community-tc.services.mozilla.com/api/github/v1/repository/MozillaSecurity/browser-memory-monitor/main/latest)
[![codecov](https://codecov.io/gh/MozillaSecurity/browser-memory-monitor/branch/main/graph/badge.svg)](https://codecov.io/gh/MozillaSecurity/browser-memory-monitor)
[![Matrix](https://img.shields.io/badge/dynamic/json?color=green&label=chat&query=%24.chunk[%3F(%40.canonical_alias%3D%3D%22%23fuzzing%3Amozilla.org%22)].num_joined_members&suffix=%20users&url=https%3A%2F%2Fmozilla.modular.im%2F_matrix%2Fclient%2Fr0%2FpublicRooms&style=flat&logo=matrix)](https://riot.im/app/#/room/#fuzzing:mozilla.org)
[![PyPI](https://img.shields.io/pypi/v/browser-memory-monitor)](https://pypi.org/project/browser-memory-monitor)

Browser Memory Monitor is a Python tool to track and limit the amount of memory used by a subprocess such as a browser under test.

```
usage: bmm [-h] [--force] [--format {mprof,csv}] [--interval INTERVAL] [--limit LIMIT] [--pre-interval PRE_INTERVAL] [--time-limit TIME_LIMIT] [--verbose] [--version] browser data command [...]

Memory profiler/limiter for browsers

positional arguments:
  browser               Browser process name to monitor (eg. 'firefox')
  data                  Profiling data output filename
  command [...]         Command (and args) to execute as a subprocess

options:
  -h, --help            show this help message and exit
  --force, -f           Overwrite existing data output file.
  --format {mprof,csv}, -F {mprof,csv}
                        Output format (choices: mprof, csv, default: mprof)
  --interval INTERVAL, -T INTERVAL
                        Memory profiling interval (default: 0.1)
  --limit LIMIT, -m LIMIT
                        Memory limit in MiB (0 for no limit, default: 12288)
  --pre-interval PRE_INTERVAL, -P PRE_INTERVAL
                        Process start interval (default: 0.01)
  --time-limit TIME_LIMIT, -t TIME_LIMIT
                        Maximum time to run (in seconds, 0 for no limit, default: 0)
  --verbose, -v         Enable verbose logging
  --version, -V         Show version number
```
