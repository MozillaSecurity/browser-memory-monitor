"""cmdline parsing tests"""
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from pytest import mark, raises

from browser_memory_monitor.args import BrowserMemoryMonitorArgs


def test_args_simple():
    """test parse_args() - success"""
    BrowserMemoryMonitorArgs().parse_args(["ff", "fake.bin", "ls"])


@mark.parametrize(
    "args, msg, idx",
    [
        # test help
        (["-h"], "usage: bmm", 0),
        # test without args
        ([], "the following arguments are required: browser, data", -1),
        (
            ["ff", "fake.bin", "--interval", "-1", "ls"],
            "--interval must be positive",
            -1,
        ),
        (
            ["ff", "fake.bin", "--pre-interval", "-1", "ls"],
            "--pre-interval must be positive",
            -1,
        ),
        (["", "fake.bin", "ls"], "browser must be given", -1),
        (["ff", "fake.bin"], "the following arguments are required: command", -1),
        (["ff", "fake.bin", "--limit", "-1", "ls"], "--limit must be positive", -1),
        (
            ["ff", "fake.bin", "--time-limit", "-1", "ls"],
            "--time-limit must be positive",
            -1,
        ),
        (["ff", "fake.bin", "--limit", "1.0", "ls"], "invalid int value", -1),
        (["ff", "fake.bin", "--time-limit", "1.0", "ls"], "invalid int value", -1),
    ],
)
def test_args_failure(capsys, args, msg, idx):
    """test parse_args() - failure"""
    with raises(SystemExit):
        BrowserMemoryMonitorArgs().parse_args(args)
    assert msg in capsys.readouterr()[idx]


def test_args_overwrite(capsys, tmp_path):
    """test no overwrite data without --force"""
    data = tmp_path / "data.txt"
    data.touch()
    with raises(SystemExit):
        BrowserMemoryMonitorArgs().parse_args(["ff", str(data), "ls"])
    assert "Use --force to overwrite" in capsys.readouterr()[-1]
