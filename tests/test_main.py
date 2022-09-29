"""process tree search tests"""
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from argparse import Namespace
from itertools import count
from unittest.mock import Mock

from psutil import Process
from pytest import raises

from browser_memory_monitor.core import ctrl_c, main


def test_ctrl_c(mocker):
    """ctrl_c calls subprocess on Windows and kill on Linux"""
    kill = mocker.patch("browser_memory_monitor.core.kill")
    system = mocker.patch("browser_memory_monitor.core.system", return_value="Windows")
    call = mocker.patch("browser_memory_monitor.core.check_call")
    ctrl_c(0)
    assert kill.call_count == 0
    assert call.call_count == 1
    call.reset_mock()
    system.return_value = "Linux"
    ctrl_c(0)
    assert kill.call_count == 1
    assert call.call_count == 0


def test_main_exit_before_found(mocker):
    """subprocess exits before browser can be found"""
    mocker.patch("browser_memory_monitor.core.Popen", autospec=True)
    proc = mocker.patch("browser_memory_monitor.core.Process", autospec=True)
    proc.return_value.returncode = 123
    mocker.patch(
        "browser_memory_monitor.core.find_process", autospec=True, return_value=None
    )
    mocker.patch(
        "browser_memory_monitor.core.wait_procs",
        autospec=True,
        return_value=([proc.return_value], None),
    )
    opts = Namespace()
    opts.process = "test"
    opts.pre_interval = 0.5
    with raises(SystemExit) as exc:
        main(opts, [])
    assert exc.value.code == 123


def test_main_exit_before_poll(mocker, tmp_path):
    """browser exits before memory polling begins"""
    child = Mock(spec=Process)
    child.is_running.return_value = False
    mocker.patch("browser_memory_monitor.core.Popen", autospec=True)
    proc = mocker.patch("browser_memory_monitor.core.Process", autospec=True)
    proc.return_value.returncode = 123
    mocker.patch(
        "browser_memory_monitor.core.find_process", autospec=True, return_value=child
    )
    mocker.patch(
        "browser_memory_monitor.core.wait_procs",
        autospec=True,
        return_value=([proc.return_value], None),
    )
    opts = Namespace()
    opts.data = tmp_path / "data.txt"
    opts.process = "test"
    opts.interval = 0.5
    with raises(SystemExit) as exc:
        main(opts, [])
    assert exc.value.code == 123


def test_main_memory_limit(mocker, tmp_path):
    """memory limit hit"""
    child = Mock(spec=Process)
    child.cmdline.return_value = "hello world"
    child.returncode = 123
    child.is_running.return_value = True
    mocker.patch("browser_memory_monitor.core.ctrl_c", autospec=True)
    proc = mocker.patch("browser_memory_monitor.core.Popen", autospec=True)
    proc.return_value.__enter__.return_value.wait.return_value = 0
    mocker.patch("browser_memory_monitor.core.Process", autospec=True)
    mocker.patch(
        "browser_memory_monitor.core.find_process", autospec=True, return_value=child
    )
    mocker.patch(
        "browser_memory_monitor.core.wait_procs", autospec=True, return_value=([], None)
    )
    mocker.patch(
        "browser_memory_monitor.core.memory_usage", side_effect=count(10.0, 1.0)
    )
    mocker.patch("browser_memory_monitor.core.time", side_effect=count())
    opts = Namespace()
    opts.data = tmp_path / "data.txt"
    opts.process = "test"
    opts.interval = 0.5
    opts.limit = 11
    opts.time_limit = 0
    with raises(SystemExit) as exc:
        main(opts, [])
    assert exc.value.code == 0
    data = opts.data.read_text().splitlines()
    assert len(data) == 3
    assert data[0] == "CMDLINE hello world"
    assert data[1] == "MEM 10.000000 1.0000"
    assert data[2] == "MEM 11.000000 2.0000"


def test_main_time_limit(mocker, tmp_path):
    """time limit hit"""
    child = Mock(spec=Process)
    child.cmdline.return_value = "hello world"
    child.returncode = 123
    child.is_running.return_value = True
    mocker.patch("browser_memory_monitor.core.ctrl_c", autospec=True)
    proc = mocker.patch("browser_memory_monitor.core.Popen", autospec=True)
    proc.return_value.__enter__.return_value.wait.return_value = 0
    mocker.patch("browser_memory_monitor.core.Process", autospec=True)
    mocker.patch(
        "browser_memory_monitor.core.find_process", autospec=True, return_value=child
    )
    mocker.patch(
        "browser_memory_monitor.core.wait_procs", autospec=True, return_value=([], None)
    )
    mocker.patch(
        "browser_memory_monitor.core.memory_usage", side_effect=count(10.0, 1.0)
    )
    mocker.patch("browser_memory_monitor.core.time", side_effect=count())
    opts = Namespace()
    opts.data = tmp_path / "data.txt"
    opts.process = "test"
    opts.interval = 0.5
    opts.limit = 0
    opts.time_limit = 5
    with raises(SystemExit) as exc:
        main(opts, [])
    assert exc.value.code == 0
    data = opts.data.read_text().splitlines()
    assert len(data) == 6
    assert data[0] == "CMDLINE hello world"
    assert data[1] == "MEM 10.000000 1.0000"
    assert data[2] == "MEM 11.000000 2.0000"
    assert data[3] == "MEM 12.000000 3.0000"
    assert data[4] == "MEM 13.000000 4.0000"
    assert data[5] == "MEM 14.000000 5.0000"