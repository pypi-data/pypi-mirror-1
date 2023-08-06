# -*- coding: utf-8 -*-
from ConfigObject import module_config
import tempfile

def test_new():
    module_config('ConfigObject.config')

    from ConfigObject import config

