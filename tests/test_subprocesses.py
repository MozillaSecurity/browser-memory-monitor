"""process tree search tests"""
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from unittest.mock import Mock

from psutil import Process

from browser_memory_monitor.core import find_process, memory_usage


def test_find_process():
    """test find_process()"""
    children = []
    for pid, name in enumerate("ABCD"):
        child = Mock(spec=Process)
        child.pid = pid
        child.name.return_value = name
        children.append(child)
    parent = Mock(spec=Process)
    parent.children.return_value = children
    assert find_process(parent, "C").name() == "C"
    assert find_process(parent, "E") is None


def test_memory_usage():
    """test memory_usage()"""
    children = []
    for memory in range(4):
        child = Mock(spec=Process)
        child.memory_info.return_value.rss = (memory + 1) * 1024 * 1024
        children.append(child)
    parent = Mock(spec=Process)
    parent.children.return_value = children
    parent.memory_info.return_value.rss = 7 * 1024 * 1024
    assert memory_usage(parent) == 17.0
