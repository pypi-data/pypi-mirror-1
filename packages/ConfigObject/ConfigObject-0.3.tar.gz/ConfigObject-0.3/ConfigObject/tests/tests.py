# -*- coding: utf-8 -*-
from ConfigObject import ConfigObject
from ConfigObject.tests import config

def test_module():
    assert isinstance(config, ConfigObject)

def test_lists():
    assert config.list.flat.as_list() == ['1', '2']
    assert config.list.flat.as_list() == config.list.lines.as_list('\n')

def test_bools():
    assert config.bool.true.as_bool() is False
    config.bool.true = True
    assert config.bool.true.as_bool() is True
