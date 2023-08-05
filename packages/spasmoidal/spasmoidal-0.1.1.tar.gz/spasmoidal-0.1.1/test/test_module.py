#!/usr/bin/env python
# encoding: utf-8
"""
test_module.py

Created by Doug Fort on 2006-09-04.
Copyright (c) 2006 Doug Fort Consultiing, Inc.. All rights reserved.
"""      

import logging

try:
    from spasmodic_engine import make_task, spasmodic_coroutine
except ImportError:
    # if we fail to import, assume we are running locally;
    # so add '..' to the search path
    import os.path
    sys.path.append(os.path.dirname(sys.path[0]))
    from spasmodic_engine import SpasmodicEngine, spasmodic_coroutine
    
def factory(module_config, blackboard):
    @spasmodic_coroutine
    def test_coroutine(blackboard):
        blackboard["n"] = 0   
        log = logging.getLogger("test_coroutine") 
        this_generator = yield None #get our own handle
        assert this_generator is not None
        while True:
            blackboard["n"] += 1
            log.info("called %s times", blackboard["n"])
            x = yield None
    return (make_task(test_coroutine(blackboard)),)
