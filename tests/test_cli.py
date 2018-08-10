#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest

from cr.cli import main
from cr.utils.shell import call

def test_help(capfd):
    with pytest.raises(SystemExit) as pytest_wrapped_ex:
        r = main(['--help'])
    assert pytest_wrapped_ex.type == SystemExit
    assert pytest_wrapped_ex.value.code == 0
    out, err = capfd.readouterr()
    assert out
    assert '-h, --help' in out
